from enum import Enum


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


DEFAULT_MODEL_LOCATION = {
  Model.vit_h: './models/sam_vit_h_4b8939.pth',
  Model.vit_l: './models/sam_vit_l_0b3195.pth',
  Model.vit_b: './models/sam_vit_b_01ec64.pth',
  Model.hq_vit_h: './models/sam_hq_vit_h.pth',
  Model.hq_vit_l: './models/sam_hq_vit_l.pth',
  Model.hq_vit_b: './models/sam_hq_vit_b.pth',
  Model.hq_vit_tiny: './models/sam_hq_vit_tiny.pth',
  Model.gd: './models/groundingdino_swint_ogc.pth',
}


def get_default_path_from_model(model: Model) -> str:
  path = DEFAULT_MODEL_LOCATION[model]
  if not path:
    raise ValueError(f'Invalid model: {model}')
  return path
