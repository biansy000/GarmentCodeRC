import os
import yaml
import shutil

config_path = os.path.join('/is/cluster/fast/sbian/data/673889/GarmentCodeData/garments_5000_0/default_body/dataset_properties_default_body.yaml')
with open(config_path, 'r') as f:
    config_all = yaml.safe_load(f)

garment_types = config_all['generator']['stats']['garment_types']

cnt = 0
for k, v in garment_types.items():
    type = v['main']
    if type == 'upper_garment':
        original_path_design = f'/is/cluster/fast/sbian/data/673889/GarmentCodeData/garments_5000_0/default_body/{k}/{k}_design_params.yaml'
        original_path_img = f'/is/cluster/fast/sbian/data/673889/GarmentCodeData/garments_5000_0/default_body/{k}/{k}_render_front.png'

        saved_path = f'Logs/tmp_folders/{k}/'
        os.makedirs(saved_path, exist_ok=True)

        shutil.copy(original_path_design, saved_path)
        shutil.copy(original_path_img, saved_path)

        if cnt > 30:
            assert False