# Abstract paths to work in both development and inside of binaries.
# Needed only for non-code files, for example JSON.

import os
import sys
import tempfile

from ezsam.lib.logger import debug, warn


# ref: https://stackoverflow.com/a/13790741
def resource_path(relative_path: str) -> str:
  """
  Try to get absolute path to resource, whether in development or in standalone/one-file executables for Nuitka or PyInstaller.
  """
  # Note:
  # - PyInstaller creates a temp folder and stores that path in sys._MEIPASS
  # - Nuitka build creates temp folder at --onefile-tempdir-spec=$tempdir
  #    The default tempdir is: {TEMP}/onefile_{PID}_{TIME}
  #    For this project's build it's set to: {TEMP}/ezsam
  #    Another example, using persistence: {CACHE_DIR}/{PRODUCT}/{VERSION}
  try:
    temp = tempfile.gettempdir()
    base_path = f'{temp}/ezsam'
    path = os.path.normpath(os.path.join(base_path, relative_path))
    open(path)
  except FileNotFoundError:
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__) + '/../../../')
    try:
      path = os.path.normpath(os.path.join(base_path, relative_path))
      open(path)
    except FileNotFoundError:
      warn(f'Could not find file at {relative_path}, returning {path} anyways ...')
  debug(f'Converted {relative_path} to {path}')
  return path
