# SPDX-License-Identifier: AGPL-3.0-only
#
# A pipeline to delete background from images or video.
# Selects the foreground using text prompts to GroundingDINO to detect objects,
#  and then segments everything using Segment-Anything or Segment-Anything HQ.
#
# Based on code in Grounded-Segment-Anything, copyright 2020 IDEA, Inc.
# ref: https://github.com/IDEA-Research/Grounded-Segment-Anything
#

import argparse
#import itertools
import os
import sys
from enum import Enum

import cv2
import filetype
import numpy as np
import supervision as sv
import torch
import torchvision
#import tqdm
import groundingdino.util.inference as gd
#import segment_anything_hq as samhq # Delayed import of noisy package

from ezsam.dateutils import now
from ezsam.downloader import download
from ezsam.models import Model, MODEL_URL, get_default_path_from_model
from ezsam.config import (
  DEFAULT_SAM_MODEL,
  DEFAULT_GROUNDING_DINO_CONFIG_PATH,
  DEFAULT_OUTPUT_DIR,
  DEFAULT_OUTPUT_SUFFIX ,
  DEFAULT_BOX_THRESHOLD,
  DEFAULT_TEXT_THRESHOLD,
  DEFAULT_NMS_THRESHOLD,
  OUTPUT_IMAGE_FORMAT,
)


def parse_args(argv = None):
  parser = argparse.ArgumentParser('ezsam', add_help=True)
  # fmt: off
  parser.add_argument('input', nargs='+', help='Input image(s) or video(s) to process')
  parser.add_argument('-d', '--debug', action='store_true', help='Debug mode: annotate output with detection boxes and masks instead of removing backgrounds')
  parser.add_argument('--hq', '--use_sam_hq', action='store_true', help='Use SAM-HQ for object segmenting instead of SAM')
  parser.add_argument('--bmin', '--box_threshold', type=float, default=DEFAULT_BOX_THRESHOLD, help='Confidence threshold for object detection boxes')
  parser.add_argument('--tmin', '--text_threshold', type=float, default=DEFAULT_TEXT_THRESHOLD, help='Confidence threshold for text prompts to be used at all')
  parser.add_argument('--nmin', '--nms_threshold', type=float, default=DEFAULT_NMS_THRESHOLD, help='Threshold to remove lower quality object boxes during post processing')
  parser.add_argument('--gd', '--gd_checkpoint', type=str, required=False, help='Path to GroundingDINO checkpoint file')
  parser.add_argument('-c', '--gconf', '--gd_config', type=str, required=False, help='Path to GroundingDINO config file')
  parser.add_argument('-m', '--sam_model', type=str, required=False, help='SAM ViT version: vit_b / vit_l / vit_h. If omitted, will guess from checkpoint filename.')
  parser.add_argument('--sam', '--sam_checkpoint', type=str, required=False, help='Path to Segment-Anything checkpoint file')
  parser.add_argument('-p', '--prompts', '--prompt_string', nargs='*', help='Comma delimited list of prompts to use in foreground selection')
  parser.add_argument('--pfile', '--prompt_file', type=str, required=False, help='Path to file with foreground selection prompts, one per line')
  parser.add_argument('-s', '--output_suffix', type=str, default=DEFAULT_OUTPUT_SUFFIX, help='Suffix to append to processed output name(s) i.e. for ".out", src.jpg -> src.out.jpg')
  parser.add_argument('-o', '--output_dir', type=str, default=DEFAULT_OUTPUT_DIR, help='Directory to write processed output to')
  # fmt: on
  return parser.parse_args(argv)


def main(argv = None):
  args = parse_args(argv)
  INPUT: list[str] = args.input or []
  DEBUG: bool = args.debug
  GD_CONFIG_PATH = args.gconf or DEFAULT_GROUNDING_DINO_CONFIG_PATH
  SAM_MODEL: str = args.sam_model or DEFAULT_SAM_MODEL
  USE_SAM_HQ: bool = args.hq
  model_name = ''
  if USE_SAM_HQ and (SAM_MODEL in [Model.vit_h, Model.vit_l, Model.vit_b]):
    model_name = 'hq_'
  model_name += SAM_MODEL
  default_sam_checkpoint_path: str = get_default_path_from_model(model_name)
  sam_checkpoint_path = args.sam or default_sam_checkpoint_path
  sam_checkpoint_specified: bool = not not args.sam
  default_gd_checkpoint_path: str = get_default_path_from_model(Model.gd)
  gd_checkpoint_path = args.gd or default_gd_checkpoint_path
  gd_checkpoint_specified: bool = not not args.gd
  BOX_THRESHOLD: float = args.bmin
  TEXT_THRESHOLD: float = args.tmin
  NMS_THRESHOLD: float = args.nmin
  PROMPT_STRING: str = ' '.join(args.prompts) if args.prompts else None
  PROMPT_FILE: str = args.pfile
  OUTPUT_DIR: str = args.output_dir
  OUTPUT_SUFFIX: str = args.output_suffix
  print('---------------------')
  print('Running with options:')
  print(f'--input: {INPUT}')
  print(f'--debug: {DEBUG}')
  print(f'--box_threshold: {BOX_THRESHOLD}')
  print(f'--text_threshold: {TEXT_THRESHOLD}')
  print(f'--nms_threshold: {NMS_THRESHOLD}')
  print(f'--gd_checkpoint: {gd_checkpoint_path}')
  print(f'--gd_config: {GD_CONFIG_PATH}')
  print(f'--sam_model: {SAM_MODEL}')
  print(f'--sam_checkpoint: {sam_checkpoint_path}')
  print(f'--use_sam_hq: {USE_SAM_HQ}')
  print(f'--output_dir: {OUTPUT_DIR}')
  print(f'--output_suffix: {OUTPUT_SUFFIX}')
  print(f'--prompt_string: {PROMPT_STRING}')
  print(f'--prompt_file: {PROMPT_FILE}')
  print('---------------------')

  # Make a list of all user prompts for selecting foreground elements, prediction classes used in GroundingDINO
  file_prompts = []
  if PROMPT_FILE:
    with open(PROMPT_FILE, 'r') as f:
      file_prompts = [line.strip() for line in f.readlines()]
  string_prompts = [prompt.strip() for prompt in PROMPT_STRING.split(',')] if PROMPT_STRING else []
  prompts = file_prompts + string_prompts
  if not prompts or len(prompts) <= 0:
    raise ValueError('You need to specify --prompts for selecting the foreground. See --help')
  print(f'Foreground selection prompts are: {prompts}')

  # Create output directory if it doesn't exist already
  if os.path.exists(OUTPUT_DIR):
    if not os.path.isdir(OUTPUT_DIR):
      raise ValueError(f'--output_dir is not a directory: {OUTPUT_DIR}. Please specify a directory to write output to!')
  else:
    print(f'Creating output directory: {OUTPUT_DIR} ...')
    os.makedirs(OUTPUT_DIR)

  # If checkpoint files are not specified, then download default checkpoints as needed
  print('Downloading models if needed ...')
  if not gd_checkpoint_specified and not os.path.isfile(default_gd_checkpoint_path):
    print('Downloading default GroundingDINO model ...')
    outdir = os.path.dirname(default_gd_checkpoint_path)
    download(MODEL_URL[Model.gd], outdir)
  if not sam_checkpoint_specified and not os.path.isfile(default_sam_checkpoint_path):
    outdir = os.path.dirname(default_sam_checkpoint_path)
    if USE_SAM_HQ:
      print('Downloading default SAM-HQ model ...')
      download(MODEL_URL[Model.hq_vit_h], outdir)
    else:
      print('Downloading default SAM model ...')
      download(MODEL_URL[Model.vit_h], outdir)
  for checkpoint in [gd_checkpoint_path, sam_checkpoint_path]:
    if not os.path.isfile(checkpoint):
      raise Exception(f'Could not find model checkpoint file: {checkpoint}')

  DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  print(f'Running on: {DEVICE}')

  if DEBUG:
    print('Debug mode active: output images will have bounding box and masks overlaying original')

  print(f'{now()}: Building GroundingDINO inference model ...')
  grounding_dino_model = gd.Model(model_config_path=GD_CONFIG_PATH, model_checkpoint_path=gd_checkpoint_path)

  print(f'{now()}: Building SAM model and predictor ...')
  import segment_anything_hq as samhq
  sam = samhq.sam_model_registry[SAM_MODEL](checkpoint=sam_checkpoint_path)
  sam.to(device=DEVICE)
  sam_predictor = samhq.SamPredictor(sam)

  for src in INPUT:
    try:
      input_mode = get_input_mode(src)
      input_filename, ext = os.path.splitext(os.path.basename(src))
      if DEBUG:
        # Debug mode or video can use original format
        pass
      else:
        # Output is with transparency
        if input_mode == InputMode.image:
          ext = '.' + OUTPUT_IMAGE_FORMAT
        elif input_mode == InputMode.video:
          # TODO 
          pass
      out = OUTPUT_DIR + '/' + input_filename + OUTPUT_SUFFIX + ext
      print(f'{now()}: Processing file {src} to {out} ...')
      process_image_args = {
        'prompts': prompts,
        'box_threshold': BOX_THRESHOLD,
        'text_threshold': TEXT_THRESHOLD,
        'nms_threshold': NMS_THRESHOLD,
        'sam_predictor': sam_predictor,
        'grounding_dino_model': grounding_dino_model,
        'debug': DEBUG,
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
    except Exception as err: 
      print(f'Error processing file {src}: {err}')
  print(f'Finished all processing jobs at: {now()}')


def process_image(
  image: np.ndarray,
  # Masks are generated using alpha-stripped version of image, but output image is original with added masks
  image_unchanged: np.ndarray | None,
  prompts: list[str],
  box_threshold: float,
  text_threshold: float,
  nms_threshold: float,
  sam_predictor,
  grounding_dino_model,
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

  import segment_anything_hq as samhq
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


class InputMode(Enum):
  image = 1
  video = 2
  other = 3


def get_input_mode(file):
  # Check whether we are parsing a folder or file.
  # If file, check if it's an image or video using file signature (not extension).
  # ref: https://github.com/h2non/filetype.py
  input_mode = None
  if os.path.isdir(file):
    raise ValueError(f'Input is a directory, specify individual file(s) instead of: {file}')
  if os.path.isfile(file):
    kind = filetype.guess(file)
    if kind is None or kind.mime is None:
      raise ValueError(f'Could not determine input file type: {file}')
    if kind.mime.startswith('image'):
      input_mode = InputMode.image
    elif kind.mime.startswith('video'):
      input_mode = InputMode.video
    else:
      input_mode = InputMode.other
  else:
    raise ValueError(f'Input is not a file: {file}')
  if input_mode == InputMode.video:
    raise NotImplementedError(f'Video processing not yet implemented, skipping input: {file}')
  if input_mode == InputMode.other:
    raise ValueError(f'Can only process videos and images, skipping input: {file}')
  return input_mode


if __name__ == '__main__':
  main(sys.argv[1:])
