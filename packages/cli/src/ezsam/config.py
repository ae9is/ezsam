from ezsam.formats import OutputImageFormat, OutputVideoCodec


DEFAULT_SAM_MODEL = 'vit_h'
DEFAULT_GROUNDING_DINO_CONFIG_PATH = './config/GroundingDINO_SwinT_OGC.py'
DEFAULT_OUTPUT_DIR = '.'
DEFAULT_OUTPUT_SUFFIX = '.out'
DEFAULT_BOX_THRESHOLD = 0.3
DEFAULT_TEXT_THRESHOLD = 0.3
DEFAULT_NMS_THRESHOLD = 0.8
DEFAULT_IMAGE_FORMAT = OutputImageFormat.png.value
DEFAULT_VIDEO_CODEC = OutputVideoCodec.vp9.value
