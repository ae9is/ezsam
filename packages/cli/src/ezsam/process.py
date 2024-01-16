import itertools
import os

import cv2
import numpy as np
import supervision as sv
import torch
import torchvision
import tqdm
import groundingdino.util.inference as gd
import segment_anything_hq as samhq

from ezsam.dateutils import now
from ezsam.fileutils import InputMode, get_input_mode
from ezsam.config import (
  OUTPUT_IMAGE_FORMAT,
  OUTPUT_VIDEO_FORMAT,
)


def process_file(
  src: str,
  prompts: list[str],
  box_threshold: float,
  text_threshold: float,
  nms_threshold: float,
  sam_predictor: samhq.SamPredictor,
  grounding_dino_model: gd.Model,
  output_suffix: str,
  output_dir: str,
  debug: bool,
) -> None :
  input_mode = get_input_mode(src)
  input_filename, ext = os.path.splitext(os.path.basename(src))
  codec = None
  # Determine output extension
  if debug:
    # Debug (annotations) mode can use original format
    pass
  else:
    # Pick a format that supports transparency
    if input_mode == InputMode.image:
      ext = '.' + OUTPUT_IMAGE_FORMAT
    elif input_mode == InputMode.video:
      ext = '.' + OUTPUT_VIDEO_FORMAT
      codec = None
      # TODO
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
    # TODO
    pass


def process_image(
  image: np.ndarray,
  # Masks are generated using alpha-stripped version of image, but output image is original with added masks
  image_unchanged: np.ndarray | None,
  prompts: list[str],
  box_threshold: float,
  text_threshold: float,
  nms_threshold: float,
  sam_predictor: samhq.SamPredictor,
  grounding_dino_model: gd.Model,
  debug: bool,
) -> np.ndarray :
  # Detect objects
  detections: sv.Detections = grounding_dino_model.predict_with_classes(
    image=image,
    classes=prompts,
    box_threshold=box_threshold,
    text_threshold=text_threshold
  )

  def get_labels(prompts: list[str], detections) -> list[str]:
    return [f'{prompts[class_id]} {confidence:0.2f}' for _, _, confidence, class_id, _ in detections]

  # NMS post processing to remove lower quality boxes
  print(f'{now()} Before NMS: {len(detections.xyxy)} boxes')
  nms_idx = torchvision.ops.nms(
    torch.from_numpy(detections.xyxy),
    torch.from_numpy(detections.confidence),
    nms_threshold
  ).numpy().tolist()
  detections.xyxy = detections.xyxy[nms_idx]
  detections.confidence = detections.confidence[nms_idx]
  detections.class_id = detections.class_id[nms_idx]
  print(f'{now()} After NMS: {len(detections.xyxy)} boxes')

  def segment(sam_predictor: samhq.SamPredictor, image: np.ndarray, xyxy: np.ndarray) -> np.ndarray:
    # Prompt SAM with boxes for all detected objects
    sam_predictor.set_image(image, 'BGR')
    result_masks = []
    for box in xyxy:
      masks, scores, logits = sam_predictor.predict(
        box=box,
        multimask_output=True
      )
      index = np.argmax(scores)
      result_masks.append(masks[index])
    return np.array(result_masks)

  print(f'{now()} Converting object detections to segment masks ...')
  detections.mask = segment(
    sam_predictor=sam_predictor,
    image=image,
    xyxy=detections.xyxy
  )

  if debug:
    print(f'{now()} Annotating output image ...')
    # Annotate image with SAM segment masks and GroundingDINO object detection boxes
    mask_annotator = sv.MaskAnnotator()
    box_corner_annotator = sv.BoxCornerAnnotator()
    label_annotator = sv.LabelAnnotator(text_position=sv.Position.CENTER_OF_MASS)
    labels = get_labels(prompts, detections)
    processed_image = mask_annotator.annotate(scene=image.copy(), detections=detections)
    processed_image = box_corner_annotator.annotate(scene=processed_image, detections=detections)
    processed_image = label_annotator.annotate(scene=processed_image, detections=detections, labels=labels)
  else:
    print(f'{now()} Filtering output image ...')
    # Filter image using masks...
    # First join all masks together; reduce on first axis, since that's the mask number in detections.mask.
    # Note: detection.mask is array of n masks * H pixels * W pixels, with each pixel True or False.
    supermask_true_false: np.ndarray = np.logical_or.reduce(detections.mask, axis=0)
    # Where mask value is true (opaque), set alpha channel to 255
    supermask_255_0 = np.where(supermask_true_false, 255, 0)
    # We prefer basing output on original image including any alpha channel, if present
    processed_image = cv2.cvtColor(image if ndarrayIsNone(image_unchanged) else image_unchanged, cv2.COLOR_BGR2BGRA)
    # Set alpha channel and save output image
    processed_image[:, :, 3] = supermask_255_0
  return processed_image


def ndarrayIsNone(array: np.ndarray):
  return type(array) is np.ndarray
