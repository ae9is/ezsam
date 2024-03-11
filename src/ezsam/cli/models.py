from enum import Enum

from ezsam.cli.config.defaults import DEFAULT_CACHE_FOLDER_LOCATION


class Model(str, Enum):
  vit_h = 'vit_h'
  vit_l = 'vit_l'
  vit_b = 'vit_b'
  hq_vit_h = 'hq_vit_h'
  hq_vit_l = 'hq_vit_l'
  hq_vit_b = 'hq_vit_b'
  hq_vit_tiny = 'hq_vit_tiny'
  gd = 'gd'


MODEL_URL = {
  Model.vit_h: 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth',
  Model.vit_l: 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth',
  Model.vit_b: 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth',
  Model.hq_vit_h: 'https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth',
  Model.hq_vit_l: 'https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_l.pth',
  Model.hq_vit_b: 'https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_b.pth',
  Model.hq_vit_tiny: 'https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_tiny.pth',
  Model.gd: 'https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth',
}

MODEL_FILE_BASENAME = {
  Model.vit_h: 'sam_vit_h_4b8939',
  Model.vit_l: 'sam_vit_l_0b3195',
  Model.vit_b: 'sam_vit_b_01ec64',
  Model.hq_vit_h: 'sam_hq_vit_h',
  Model.hq_vit_l: 'sam_hq_vit_l',
  Model.hq_vit_b: 'sam_hq_vit_b',
  Model.hq_vit_tiny: 'sam_hq_vit_tiny',
  Model.gd: 'groundingdino_swint_ogc',
}

MODEL_SEARCH_LOCATIONS = [
  DEFAULT_CACHE_FOLDER_LOCATION,
  '.',
]


def default_model_locations(model: Model) -> list[str]:
  return [f'{search_path}/models/{MODEL_FILE_BASENAME[model]}.pth' for search_path in MODEL_SEARCH_LOCATIONS]


def get_default_paths_from_model(model: Model) -> str:
  paths = default_model_locations(model)
  if not paths or len(paths) <= 0:
    raise ValueError(f'Invalid model: {model}')
  return paths
