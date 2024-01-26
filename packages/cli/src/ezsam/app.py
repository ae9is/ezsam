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
import numbers
import os
import sys

import torch
import groundingdino.util.inference as gd
# import segment_anything_hq as samhq # Noisy

from ezsam.lib.date import now
from ezsam.lib.downloader import download
from ezsam.lib.gpu import attempt_gpu_cleanup
from ezsam.models import Model, MODEL_URL, get_default_path_from_model
from ezsam.formats import OutputImageFormat, OutputVideoCodec
from ezsam.process import process_file
from ezsam.config.utils import cleanup_gdconfig_tmpfile, create_gdconfig_tmpfile
from ezsam.config.defaults import (
  DEFAULT_SAM_MODEL,
  DEFAULT_GROUNDING_DINO_CONFIG_PATH,
  DEFAULT_OUTPUT_DIR,
  DEFAULT_OUTPUT_SUFFIX,
  DEFAULT_BOX_THRESHOLD,
  DEFAULT_TEXT_THRESHOLD,
  DEFAULT_NMS_THRESHOLD,
  DEFAULT_IMAGE_FORMAT,
  DEFAULT_VIDEO_CODEC,
)


def parse_args(argv=None):
  def unit_interval(value: str):
    # First, try to parse as a number
    num = float(value)
    # Enforce that value is a real number between 0 and 1 inclusive.
    # Note boolean is subclass of real numbers.
    if isinstance(num, bool) or not isinstance(num, numbers.Real) or num < 0 or num > 1:
      raise ValueError(f'Error value {num} should be a float between 0 and 1 inclusive')
    return num

  parser = argparse.ArgumentParser('ezsam', add_help=True)
  # fmt: off
  parser.add_argument('input', nargs='+', help='Input image(s) or video(s) to process')
  parser.add_argument('-d', '--debug', action='store_true', help='Debug mode: annotate output with detection boxes and masks instead of removing backgrounds')
  parser.add_argument('--hq', '--use_sam_hq', action='store_true', help='Use SAM-HQ for object segmenting instead of SAM')
  parser.add_argument('--bmin', '--box_threshold', type=unit_interval, default=DEFAULT_BOX_THRESHOLD, help='Confidence threshold for object detection boxes [0,1]')
  parser.add_argument('--tmin', '--text_threshold', type=unit_interval, default=DEFAULT_TEXT_THRESHOLD, help='Confidence threshold for text prompts to be used at all [0,1]')
  parser.add_argument('--nmin', '--nms_threshold', type=unit_interval, default=DEFAULT_NMS_THRESHOLD, help='Threshold to remove lower quality object boxes during post processing [0,1]')
  parser.add_argument('--gd', '--gd_checkpoint', type=str, required=False, help='Path to GroundingDINO checkpoint file')
  parser.add_argument('-c', '--gconf', '--gd_config', type=str, required=False, help='Path to GroundingDINO config file')
  parser.add_argument('-m', '--sam_model', '--model', choices=['vit_h', 'vit_l', 'vit_b', 'vit_tiny'], required=False, help='SAM ViT version (vit_h/l/b). If omitted, will guess from checkpoint filename.')
  parser.add_argument('--sam', '--sam_checkpoint', type=str, required=False, help='Path to Segment-Anything checkpoint file')
  parser.add_argument('-p', '--prompts', '--prompt_string', nargs='*', help='Comma delimited list of prompts to use in foreground selection')
  parser.add_argument('--pfile', '--prompt_file', type=str, required=False, help='Path to file with foreground selection prompts, one per line')
  parser.add_argument('--img', '--img_fmt', choices=[c.value for c in OutputImageFormat], default=DEFAULT_IMAGE_FORMAT, help='Image file format to use for output files(s)')
  parser.add_argument('--codec', '--vc', '--vcodec', choices=[c.value for c in OutputVideoCodec], default=DEFAULT_VIDEO_CODEC, help='Video codec to use for output file(s)')
  parser.add_argument('--nf', '--num_frames', type=int, required=False, help='Number of frames to process for each input video, for testing purposes')
  parser.add_argument('-s', '--output_suffix', type=str, default=DEFAULT_OUTPUT_SUFFIX, help='Suffix to append to processed output name(s) i.e. for ".out", src.jpg -> src.out.png')
  parser.add_argument('-o', '--output_dir', type=str, default=DEFAULT_OUTPUT_DIR, help='Directory to write processed output to')
  parser.add_argument('-k', '--keep', action='store_true', help='Keep temporary image files generated when processing video')
  parser.add_argument('--smem', '--show_memory', action='store_true', help='Show PyTorch CUDA memory summary on completion')
  # fmt: on
  return parser.parse_args(argv)


def main(argv=None):
  args = parse_args(argv)
  INPUT: list[str] = args.input or []
  DEBUG: bool = args.debug
  GD_CONFIG_PATH = args.gconf or DEFAULT_GROUNDING_DINO_CONFIG_PATH
  SAM_MODEL: str = args.sam_model or DEFAULT_SAM_MODEL
  USE_SAM_HQ: bool = args.hq
  model_name = ''
  if USE_SAM_HQ:
    model_name = 'hq_'
  elif SAM_MODEL == 'vit_tiny':
    raise ValueError('Must use vit_tiny with SAM-HQ only! Please try again with --hq if this is intended')
  model_name += SAM_MODEL
  default_sam_checkpoint_path: str = get_default_path_from_model(model_name)
  sam_checkpoint_path = args.sam or default_sam_checkpoint_path
  sam_checkpoint_specified: bool = not not args.sam
  default_gd_checkpoint_path: str = get_default_path_from_model(Model.gd)
  gd_checkpoint_path = args.gd or default_gd_checkpoint_path
  gd_checkpoint_specified: bool = not not args.gd
  print(f'args.bmin: {args.bmin}')
  BOX_THRESHOLD: float = args.bmin
  TEXT_THRESHOLD: float = args.tmin
  NMS_THRESHOLD: float = args.nmin
  PROMPT_STRING: str = ' '.join(args.prompts) if args.prompts else None
  PROMPT_FILE: str = args.pfile
  IMG_FMT: OutputImageFormat = args.img or DEFAULT_IMAGE_FORMAT
  CODEC: OutputVideoCodec = args.codec or DEFAULT_VIDEO_CODEC
  NUM_TEST_FRAMES: int = args.nf
  OUTPUT_DIR: str = args.output_dir.rstrip('/')
  OUTPUT_SUFFIX: str = args.output_suffix
  CLEANUP: bool = not args.keep
  SHOW_MEMORY_SUMMARY: bool = args.smem
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
  print(f'--img_fmt: {IMG_FMT}')
  print(f'--vcodec: {CODEC}')
  print(f'--num_frames: {NUM_TEST_FRAMES}')
  print(f'--output_dir: {OUTPUT_DIR}')
  print(f'--output_suffix: {OUTPUT_SUFFIX}')
  print(f'--prompt_string: {PROMPT_STRING}')
  print(f'--prompt_file: {PROMPT_FILE}')
  print(f'--show_memory: {SHOW_MEMORY_SUMMARY}')
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

  # If GroundingDINO config file doesn't exist already, create temporary config under a different path
  using_gdconfig_tmpfile = False
  if not os.path.isfile(GD_CONFIG_PATH):
    print(f'Warning: No GroundingDINO config at: {GD_CONFIG_PATH}')
    GD_CONFIG_PATH = create_gdconfig_tmpfile()
    using_gdconfig_tmpfile = True

  # If checkpoint files are not specified, then download default checkpoints as needed
  print('Checking if models need to be downloaded ...')
  something_downloaded = False
  if not gd_checkpoint_specified and not os.path.isfile(default_gd_checkpoint_path):
    print('Downloading default GroundingDINO model ...')
    outdir = os.path.dirname(default_gd_checkpoint_path)
    download(MODEL_URL[Model.gd], outdir)
    something_downloaded = True
  if not sam_checkpoint_specified and not os.path.isfile(default_sam_checkpoint_path):
    outdir = os.path.dirname(default_sam_checkpoint_path)
    print('Downloading model ...')
    download(MODEL_URL[model_name], outdir)
    something_downloaded = True
  for checkpoint in [gd_checkpoint_path, sam_checkpoint_path]:
    if not os.path.isfile(checkpoint):
      raise Exception(f'Could not find model checkpoint file: {checkpoint}')
  if something_downloaded:
    print('Downloads finished')
  else:
    print('... no')

  if DEBUG:
    print('Debug mode active: output images will have bounding box and masks overlaying original')

  grounding_dino_model = None
  sam = None
  sam_predictor = None
  try:
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Running on: {DEVICE}')

    # Only running inference, not training models, so disable gradient calculation to reduce memory usage
    # ref: https://pytorch.org/docs/stable/generated/torch.no_grad.html
    with torch.no_grad():
      attempt_gpu_cleanup()

      print(f'{now()}: Loading GroundingDINO model ...')
      grounding_dino_model = gd.Model(model_config_path=GD_CONFIG_PATH, model_checkpoint_path=gd_checkpoint_path, device=DEVICE)

      print(f'{now()}: Loading SAM model and predictor ...')
      import segment_anything_hq as samhq

      sam = samhq.sam_model_registry[SAM_MODEL](checkpoint=sam_checkpoint_path)
      sam.to(device=DEVICE)
      sam_predictor = samhq.SamPredictor(sam)

      for src in INPUT:
        try:
          process_file_args = {
            'src': src,
            'prompts': prompts,
            'box_threshold': BOX_THRESHOLD,
            'text_threshold': TEXT_THRESHOLD,
            'nms_threshold': NMS_THRESHOLD,
            'sam_predictor': sam_predictor,
            'grounding_dino_model': grounding_dino_model,
            'img_fmt': IMG_FMT,
            'codec': CODEC,
            'num_test_frames': NUM_TEST_FRAMES,
            'output_suffix': OUTPUT_SUFFIX,
            'output_dir': OUTPUT_DIR,
            'debug': DEBUG,
            'cleanup': CLEANUP,
          }
          process_file(**process_file_args)
        except Exception as err:
          print(f'Error processing file {src}: {err}')
      print(f'Finished all processing jobs at: {now()}')
  except Exception as err:
    print(err)
  finally:
    if using_gdconfig_tmpfile:
      cleanup_gdconfig_tmpfile()
    del grounding_dino_model
    del sam_predictor
    del sam
    attempt_gpu_cleanup()
    if torch.cuda.is_available() and SHOW_MEMORY_SUMMARY:
      print(torch.cuda.memory_summary())


if __name__ == '__main__':
  main(sys.argv[1:])
