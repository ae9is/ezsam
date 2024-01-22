# SPDX-License-Identifier: AGPL-3.0-only

import itertools
import math
import os
import sys
import shlex
import subprocess as sub

import cv2
import numpy as np
import supervision as sv
import torch
import torchvision
import tqdm

import groundingdino.util.inference as gd
# import segment_anything_hq as samhq # Noisy

from ezsam.lib.date import now
from ezsam.lib.file import InputMode, get_input_mode
from ezsam.formats import OutputImageFormat, OutputVideoCodec, get_video_fmt_from_codec


def process_file(
  src: str,
  prompts: list[str],
  box_threshold: float,
  text_threshold: float,
  nms_threshold: float,
  sam_predictor,  #: samhq.SamPredictor,
  grounding_dino_model: gd.Model,
  img_fmt: OutputImageFormat,
  codec: OutputVideoCodec,
  num_test_frames: int,
  output_suffix: str,
  output_dir: str,
  debug: bool,
  cleanup: bool,
) -> None:
  input_mode = get_input_mode(src)
  # Determine output extension: preserve for images in debug mode, else use formats that support transparency.
  input_filename, input_ext = os.path.splitext(os.path.basename(src))
  ext = input_ext
  if input_mode == InputMode.image and not debug:
    ext = '.' + img_fmt
  elif input_mode == InputMode.video:
    ext = '.' + get_video_fmt_from_codec(codec)
  out = output_dir + '/' + input_filename + output_suffix + ext
  print(f'{now()}: Processing file {src} to {out} ...')
  process_image_args = {
    'prompts': prompts,
    'box_threshold': box_threshold,
    'text_threshold': text_threshold,
    'nms_threshold': nms_threshold,
    'sam_predictor': sam_predictor,
    'grounding_dino_model': grounding_dino_model,
    'debug': debug,
  }
  print(f'Process image args: {process_image_args}')

  if input_mode == InputMode.image:
    # Load image, discarding any alpha channel information if present
    image: np.ndarray = cv2.imread(src)  # note: default method cv2.IMREAD_COLOR, format BGR
    # Version of image with alpha information if present. Note that BGR is default colour mode using OpenCV library (cv2).
    image_unchanged: np.ndarray = cv2.imread(src, cv2.IMREAD_UNCHANGED)
    processed_image = process_image(image=image, image_unchanged=image_unchanged, **process_image_args)
    cv2.imwrite(out, processed_image)

  elif input_mode == InputMode.video:
    print(f'Using extension / codec: {ext} / {codec} ...')

    # Process all input frames to temporary image files
    tmp_files = []
    video_frames_generator = sv.get_video_frames_generator(source_path=src)
    video_info = sv.VideoInfo.from_video_path(video_path=src)
    fps = video_info.fps
    (w, h) = video_info.resolution_wh
    i = 0
    # I.e. 10 frames => 1 digit, 0..9. 11 frames => 2 digits, 00..10.
    num_digits = int(math.log10(video_info.total_frames - 1)) + 1
    if num_test_frames is None:
      total = video_info.total_frames
      frame_gen = video_frames_generator
    else:
      total = num_test_frames
      frame_gen = itertools.islice(video_frames_generator, total)
    for frame in tqdm.tqdm(frame_gen, total=total):
      # Pad counter to num_digits
      i_pad = str(i).zfill(num_digits)
      tmp = f'{output_dir}/{input_filename}.{i_pad}.tmp.{img_fmt}'
      processed_image = process_image(image=frame, image_unchanged=None, **process_image_args)
      i += 1
      print(f'Writing frame {i} to {tmp} ...')
      cv2.imwrite(tmp, processed_image)
      tmp_files.append(tmp)

    # Join temporary processed images into video using either FFmpeg or ImageMagick's convert
    if codec == OutputVideoCodec.gif:
      tmp_img_naming = f'{output_dir}/{input_filename}.*.tmp.{img_fmt}'
      cmd_in = ''
    else:
      tmp_img_naming = f'{output_dir}/{input_filename}.%{num_digits}d.tmp.{img_fmt}'
      cmd_in = f'ffmpeg -y -framerate {fps} -i {tmp_img_naming}'
    # ref: https://stackoverflow.com/a/75461590
    # Note: Software support is iffy for all but gif.
    # Chrome can display alpha for vp9+webm.
    # mpv works for the rest.
    cmd_out = ''
    if codec == OutputVideoCodec.prores:
      cmd_out = f'-c:v prores -pix_fmt yuva444p10le {out}'
    elif codec == OutputVideoCodec.vp9:
      cmd_out = f'-c:v libvpx-vp9 -pix_fmt yuva420p {out}'
    elif codec == OutputVideoCodec.ffv1:
      cmd_out = f'-c:v ffv1 -pix_fmt yuva420p {out}'
    elif codec == OutputVideoCodec.apng:
      cmd_out = f'-c:v apng -pix_fmt rgba {out}'
    elif codec == OutputVideoCodec.gif:
      delay = get_delay_from_fps(fps)
      cmd_out = f'convert -resize {w}x{h} -delay {delay} -dispose Background -loop 0 "{tmp_img_naming}" {out}'
    else:
      raise ValueError(f'Invalid codec: {codec}')
    cmd = cmd_in + ' ' + cmd_out
    print(f'Joining video frames via command: {cmd} ...')
    cmd_args = shlex.split(cmd)
    sub.run(cmd_args)

    if cleanup:
      for tmp in tmp_files:
        try:
          print(f'Deleting temp file: {tmp} ...')
          os.remove(tmp)
        except Exception as err:
          print(f'Error deleting temporary image file {tmp}')
          print(f'{err}')


def get_delay_from_fps(fps):
  # Get centiseconds delay from frames per second, used as ImageMagick's delay parameter
  f = fps if (fps is not None and fps != 0) else 1
  return 100.0 / f


def get_video_codec(src: str):
  codec = None
  try:
    video_capture = cv2.VideoCapture(src)
    codec_code = video_capture.get(cv2.CAP_PROP_FOURCC)
    # Convert OpenCV codec code which is a float to 4 character string
    codec = int(codec_code).to_bytes(4, byteorder=sys.byteorder).decode()
  except Exception:
    print(f'Error getting codec for video {src}')
  return codec


def process_image(
  image: np.ndarray,
  # Masks are generated using alpha-stripped version of image, but output image is original with added masks
  image_unchanged: np.ndarray | None,
  prompts: list[str],
  box_threshold: float,
  text_threshold: float,
  nms_threshold: float,
  sam_predictor,  #: samhq.SamPredictor,
  grounding_dino_model: gd.Model,
  debug: bool,
) -> np.ndarray:
  # Detect objects
  detections: sv.Detections = grounding_dino_model.predict_with_classes(
    image=image, classes=prompts, box_threshold=box_threshold, text_threshold=text_threshold
  )

  def get_labels(prompts: list[str], detections: sv.Detections) -> list[str]:
    if not prompts or len(prompts) <= 0:
      raise ValueError('get_labels: No prompts')
    if not detections or len(detections) <= 0:
      raise ValueError('get_labels: No detections')

    def generate_label(class_id, confidence):
      if class_id is None:
        label = 'Error'
      else:
        label = prompts[class_id] if len(prompts) > class_id else f'Class {class_id}'
      if confidence is None:
        confidence = 0
      return f'{label} {confidence:0.2f}'

    return [generate_label(class_id, confidence) for _, _, confidence, class_id, _ in detections]

  # NMS post processing to remove lower quality boxes
  print(f'{now()} Before NMS: {len(detections.xyxy)} boxes')
  nms_idx = (
    torchvision.ops.nms(torch.from_numpy(detections.xyxy), torch.from_numpy(detections.confidence), nms_threshold)
    .numpy()
    .tolist()
  )
  detections.xyxy = detections.xyxy[nms_idx]
  detections.confidence = detections.confidence[nms_idx]
  detections.class_id = detections.class_id[nms_idx]
  num_detections = len(detections.xyxy)
  print(f'{now()} After NMS: {num_detections} boxes')

  if num_detections <= 0:
    if debug:
      print(f'Warning: no objects detected for prompts {prompts}, returning original image ...')
      return image
    else:
      print(f'Warning: no objects detected for prompts {prompts}, returning empty image ...')
      # Create a new image with dimensions of old image plus an alpha channel, and then zero out everything
      processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
      processed_image[:, :, :] = 0
      return processed_image

  import segment_anything_hq as samhq

  def segment(sam_predictor: samhq.SamPredictor, image: np.ndarray, xyxy: np.ndarray) -> np.ndarray:
    # Prompt SAM with boxes for all detected objects
    sam_predictor.set_image(image, 'BGR')
    result_masks = []
    for box in xyxy:
      masks, scores, logits = sam_predictor.predict(box=box, multimask_output=True)
      index = np.argmax(scores)
      result_masks.append(masks[index])
    return np.array(result_masks)

  print(f'{now()} Converting object detections to segment masks ...')
  detections.mask = segment(sam_predictor=sam_predictor, image=image, xyxy=detections.xyxy)

  if debug:
    print(f'{now()} Annotating output image ...')
    # Annotate image with SAM segment masks and GroundingDINO object detection boxes.
    # Note: Should set ColorLookup.INDEX when annotating for SAM.
    # ref: https://github.com/roboflow/notebooks/blob/main/notebooks/how-to-segment-anything-with-sam.ipynb
    # ref: https://supervision.roboflow.com/annotators/
    mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)
    box_corner_annotator = sv.BoxCornerAnnotator(color_lookup=sv.ColorLookup.INDEX)
    label_annotator = sv.LabelAnnotator(text_position=sv.Position.CENTER_OF_MASS, color_lookup=sv.ColorLookup.INDEX)
    labels = get_labels(prompts, detections)
    processed_image = mask_annotator.annotate(scene=image.copy(), detections=detections)
    processed_image = box_corner_annotator.annotate(scene=processed_image, detections=detections)
    processed_image = label_annotator.annotate(scene=processed_image, detections=detections, labels=labels)
  else:
    print(f'{now()} Filtering output image ...')
    # Filter image using masks...
    # First join all masks together; reduce on first axis, since that's the mask number in detections.mask.
    # Note: detection.mask is array of n masks * H pixels * W pixels, with each pixel True or False.
    supermask: np.ndarray = np.logical_or.reduce(detections.mask, axis=0)
    # We prefer basing output on original image including any alpha channel, if present
    processed_image = cv2.cvtColor(image if not is_ndarray(image_unchanged) else image_unchanged, cv2.COLOR_BGR2BGRA)
    # Apply mask to image's alpha channel
    processed_image[:, :, 3] = np.multiply(processed_image[:, :, 3], supermask)
  return processed_image


def is_ndarray(array: np.ndarray):
  return type(array) is np.ndarray
