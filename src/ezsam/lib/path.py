# Abstract paths to work in both development and inside of pyinstaller binaries.
# Needed only for non-code files for example JSON.

import os
import sys


# ref: https://stackoverflow.com/a/13790741
def resource_path(relative_path: str) -> str:
  """
  Get absolute path to resource, works for dev and for PyInstaller
  """
  # PyInstaller creates a temp folder and stores path in _MEIPASS
  base_path = getattr(sys, '_MEIPASS', os.getcwd())
  return os.path.normpath(os.path.join(base_path, relative_path))
