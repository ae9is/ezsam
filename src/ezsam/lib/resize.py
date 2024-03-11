# Resize an image while keeping aspect ratio
# ref: https://stackoverflow.com/a/44724368
#
# Example: scaled = resize_and_pad(image, (200,200))
#

import cv2
import numpy as np


def resize_and_pad(img, size, pad_color=0):
  h, w = img.shape[:2]
  sh, sw = size

  # interpolation method
  if h > sh or w > sw:  # shrinking image
    interp = cv2.INTER_AREA

  else:  # stretching image
    interp = cv2.INTER_CUBIC

  # aspect ratio of image
  aspect = float(w) / h
  saspect = float(sw) / sh

  if (saspect >= aspect) or ((saspect == 1) and (aspect <= 1)):  # new horizontal image
    new_h = sh
    new_w = np.round(new_h * aspect).astype(int)
    pad_horz = float(sw - new_w) / 2
    pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
    pad_top, pad_bot = 0, 0

  elif (saspect < aspect) or ((saspect == 1) and (aspect >= 1)):  # new vertical image
    new_w = sw
    new_h = np.round(float(new_w) / aspect).astype(int)
    pad_vert = float(sh - new_h) / 2
    pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
    pad_left, pad_right = 0, 0

  # set pad color
  if len(img.shape) == 3 and not isinstance(
    pad_color, (list, tuple, np.ndarray)
  ):  # color image but only one color provided
    pad_color = [pad_color] * 3

  # scale and pad
  scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
  scaled_img = cv2.copyMakeBorder(
    scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=pad_color
  )

  return scaled_img
