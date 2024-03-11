import os
from enum import Enum

import filetype


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
      # Workaround: treat all input GIFs as video, animated GIFs are much more important to support
      #  and OpenCV image read doesn't support still image GIF anyways
      if kind.mime == 'image/gif':
        print(f'Treating file as video GIF: {file}')
        input_mode = InputMode.video
      else:
        input_mode = InputMode.image
    elif kind.mime.startswith('video'):
      input_mode = InputMode.video
    else:
      input_mode = InputMode.other
  else:
    raise ValueError(f'Input is not a file: {file}')
  if input_mode == InputMode.other:
    raise ValueError(f'Can only process videos and images, skipping input: {file}')
  return input_mode
