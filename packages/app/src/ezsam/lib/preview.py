import cv2
import PIL as pil
import numpy as np

from ezsam.lib.file import get_input_mode, InputMode
from ezsam.lib.logger import log
from ezsam.lib.resize import resize_and_pad


def get_preview_image(src: str, width: int, height: int) -> pil.Image.Image:
  """
  Return preview image fitting in (width, height) given a path to an image or video file.
  Respects original image or video file's aspect ratio and pads with black as needed.
  """
  frame = get_preview_image_array(src, width, height)
  image: pil.Image.Image = pil.Image.fromarray(frame)
  return image


def get_preview_image_array(src: str, width: int, height: int) -> np.ndarray:
  frame: np.ndarray = None
  try:
    input_mode = get_input_mode(src)
    if input_mode == InputMode.image:
      raw = cv2.imread(src, cv2.IMREAD_UNCHANGED)
    elif input_mode == InputMode.video:
      # This method isn't accurate for long captures but we just need the first frame
      # ref: https://stackoverflow.com/a/47867180
      capture = cv2.VideoCapture(src)
      capture.set(cv2.CAP_PROP_POS_FRAMES, -1)
      res, raw = capture.read()
    else:
      raise ValueError('Error: input is not an image or video')
    rgba = cv2.cvtColor(raw, cv2.COLOR_BGRA2RGBA)
    frame = resize_and_pad(rgba, (width, height))
  except Exception as err:
    log(f'Error: could not generate preview for {src}')
    log(err)
    frame = np.zeros(shape=[width, height, 3], dtype=np.uint8)
  return frame
