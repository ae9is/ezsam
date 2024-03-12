# Build an executable using py2exe, Windows only.
#
# ref: https://github.com/py2exe/py2exe/blob/master/docs/py2exe.freeze.md

import datetime as dt
import sys
import argparse

import py2exe

from ezsam.gui.config import COLOR_THEME


DEFAULT_NAME = 'ezsam'
DEFAULT_VERSION = '0.0.0'
CLI_PATH = 'src/ezsam/cli/app.py'
GUI_PATH = 'src/ezsam/gui/app.py'
ASSETS = [
  COLOR_THEME,
]
DESCRIPTION = 'ezsam is a tool to extract objects from images or video via text prompt'
COMMENTS = 'info at https://www.ezsam.org'


def main(argv=None):
  parser = argparse.ArgumentParser('make-exe', add_help=True)
  parser.add_argument(
    '-n', '--name', type=str, default=DEFAULT_NAME, required=True, help='Name of executable to create'
  )
  parser.add_argument('-v', '--version', type=str, default=DEFAULT_VERSION, required=True, help='Version string')
  args = parser.parse_args(argv)
  name = args.name
  version = args.version
  print(f'Creating {name}-{version} at {dt.datetime.now()} ...')
  data_files = {path: path for path in ASSETS}
  version_info = {
    'product_name': name,
    'product_version': version,
    'version': version,
    'description': DESCRIPTION,
    'comments': COMMENTS,
  }
  options = {
    #'compressed': 1,
    #'optimize': 2,
    #'bundle_files': 0,
  }
  py2exe.freeze(
    # console=[{ 'script': CLI_PATH }],
    windows=[{'script': GUI_PATH}],
    data_files=data_files,
    version_info=version_info,
    options=options,
    zipfile='lib.zip',
  )
  print(f'Finished creating {name}-{version} at {dt.datetime.now()}')


if __name__ == '__main__':
  main(sys.argv[1:])
