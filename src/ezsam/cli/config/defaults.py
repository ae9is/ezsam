import pathlib

from ezsam.cli.formats import OutputImageFormat, OutputVideoCodec

HOME_FOLDER = pathlib.Path.home().as_posix()
DEFAULT_CACHE_FOLDER_LOCATION = f'{HOME_FOLDER}/.cache/ezsam'
DEFAULT_GROUNDING_DINO_CONFIG_PATH = f'{DEFAULT_CACHE_FOLDER_LOCATION}/GroundingDINO_SwinT_OGC.py'
DEFAULT_SAM_MODEL = 'vit_h'
DEFAULT_OUTPUT_DIR = '.'
DEFAULT_OUTPUT_SUFFIX = '.out'
DEFAULT_BOX_THRESHOLD = 0.3
DEFAULT_TEXT_THRESHOLD = 0.3
DEFAULT_NMS_THRESHOLD = 0.8
DEFAULT_IMAGE_FORMAT = OutputImageFormat.png.value
DEFAULT_VIDEO_CODEC = OutputVideoCodec.vp9.value
