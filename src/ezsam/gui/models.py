# Constants for selectable segmentation models and for gui logic to transform selectable variable into 
#  --model and --hq parameters for ezsam cli.

HQ_MODEL_PREFIX = 'hq_'
_HQ = HQ_MODEL_PREFIX
MODEL_NAME_TO_TYPE = {
  'SAM Huge': 'vit_h',
  'SAM Large': 'vit_l',
  'SAM Base': 'vit_b',
  'SAM-HQ Huge': _HQ + 'vit_h',
  'SAM-HQ Large': _HQ + 'vit_l',
  'SAM-HQ Base': _HQ + 'vit_b',
  'SAM-HQ Tiny': _HQ + 'vit_tiny',
}
