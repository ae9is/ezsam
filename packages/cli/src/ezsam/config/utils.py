# Convenience function to clone a copy of config/GroundingDINO_SwinT_OGC.py 
#  for grounding.dino.inference.Model's constructor

import os

from ezsam.config.defaults import (
  DEFAULT_GROUNDING_DINO_CONFIG_PATH_TMP,
)


def create_gdconfig_tmpfile(src=DEFAULT_GROUNDING_DINO_CONFIG_PATH_TMP):
  print(f'Creating temp GroundingDINO config file at: {src} ...')
  with open(src, 'w') as f:
    f.write(str(DEFAULT_GD_CONFIG))
    f.close()
  if not os.path.isfile(src):
    raise Exception(f'Could not create temp file: {DEFAULT_GROUNDING_DINO_CONFIG_PATH_TMP}')
  return src


def cleanup_gdconfig_tmpfile(src=DEFAULT_GROUNDING_DINO_CONFIG_PATH_TMP):
  print(f'Cleaning up temp GroundingDINO config file at: {src} ...')
  if os.path.isfile(src):
    os.remove(src)


DEFAULT_GD_CONFIG = '''
batch_size = 1
modelname = 'groundingdino'
backbone = 'swin_T_224_1k'
position_embedding = 'sine'
pe_temperatureH = 20
pe_temperatureW = 20
return_interm_indices = [1, 2, 3]
backbone_freeze_keywords = None
enc_layers = 6
dec_layers = 6
pre_norm = False
dim_feedforward = 2048
hidden_dim = 256
dropout = 0.0
nheads = 8
num_queries = 900
query_dim = 4
num_patterns = 0
num_feature_levels = 4
enc_n_points = 4
dec_n_points = 4
two_stage_type = 'standard'
two_stage_bbox_embed_share = False
two_stage_class_embed_share = False
transformer_activation = 'relu'
dec_pred_bbox_embed_share = True
dn_box_noise_scale = 1.0
dn_label_noise_ratio = 0.5
dn_label_coef = 1.0
dn_bbox_coef = 1.0
embed_init_tgt = True
dn_labelbook_size = 2000
max_text_len = 256
text_encoder_type = 'bert-base-uncased'
use_text_enhancer = True
use_fusion_layer = True
use_checkpoint = True
use_transformer_ckpt = True
use_text_cross_attention = True
text_dropout = 0.0
fusion_dropout = 0.0
fusion_droppath = 0.1
sub_sentence_present = True
'''