from ezsam.lib.config import LOG_LEVEL


def log(msg: str):
  print(msg)


def debug(msg: str):
  if LOG_LEVEL == 'debug':
    print(msg)


def error(msg: str):
  log(f'Error: {msg}')


def warn(msg: str):
  log(f'Warning: {msg}')
