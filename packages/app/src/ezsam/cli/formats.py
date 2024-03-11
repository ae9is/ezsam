from enum import Enum


# Image file formats with transparency
class OutputImageFormat(str, Enum):
  png = 'png'
  tiff = 'tiff'


# Some video codecs (and animated image formats) with alpha channel support that can be written out by FFmpeg
class OutputVideoCodec(str, Enum):
  prores = 'prores'
  vp9 = 'vp9'
  ffv1 = 'ffv1'
  apng = 'apng'
  gif = 'gif'


# Map video codecs to container format
codec_to_video_format = {
  OutputVideoCodec.prores: 'mov',
  OutputVideoCodec.vp9: 'webm',
  OutputVideoCodec.ffv1: 'mkv',
  OutputVideoCodec.apng: 'apng',
  OutputVideoCodec.gif: 'gif',
}


def get_video_fmt_from_codec(codec: OutputVideoCodec) -> str:
  format = codec_to_video_format[codec]
  if not format:
    raise ValueError(f'Invalid codec: {codec}')
  return format
