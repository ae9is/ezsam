import gc
import torch


def attempt_gpu_cleanup():
  if torch.cuda.is_available():
    print('Attempting GPU memory cleanup ...')
    torch.cuda.empty_cache()
    gc.collect()
