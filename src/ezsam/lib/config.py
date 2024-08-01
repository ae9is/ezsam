import os


PYTHON_ENV = os.getenv('PYTHON_ENV', 'production')
LOG_LEVEL = 'debug' if PYTHON_ENV == 'development' else 'normal'
EXECUTABLE_NAME = 'ezsam'
