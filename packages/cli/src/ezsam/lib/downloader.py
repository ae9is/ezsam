import os
import shutil
import requests

from ezsam.lib.date import now


# Download a file from a given URL to the specified directory
def download(url: str, outdir: str):
  print(f'{now()}: Downloading {url} to {outdir} ...')
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  file_name = os.path.basename(url)
  file_path = os.path.join(outdir, file_name)
  response = requests.get(url, stream=True)
  with open(file_path, 'wb') as file:
    shutil.copyfileobj(response.raw, file)
