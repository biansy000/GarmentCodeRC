import sys
import os
import yaml
from pathlib import Path
from collections import OrderedDict
import pickle as pkl
import argparse
import json
import re
import copy
import random

sys.path.insert(0, '/is/cluster/fast/sbian/github/GarmentCodeV2/')
sys.path.insert(1, '/is/cluster/fast/sbian/github/GarmentCodeV2/external/')

import numpy as np
from tqdm import tqdm
from easydict import EasyDict as edict
from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters


wb_config_name = 'waistband'
skirt_configs =  {
    'SkirtCircle': 'flare-skirt',
    'AsymmSkirtCircle': 'flare-skirt',
    'GodetSkirt': 'godet-skirt',
    'Pants': 'pants',
    'Skirt2': 'skirt',
    'SkirtManyPanels': 'flare-skirt',
    'PencilSkirt': 'pencil-skirt',
    'SkirtLevels': 'levels-skirt',
}
all_skirt_configs = ['skirt', 'flare-skirt', 'godet-skirt', 'pencil-skirt', 'levels-skirt', 'pants']


all_possible_changes = ['waistband', 'shirt', 'collar', 'sleeve', 'sleeve_cuff', 'left_shirt', 'left_collar', 'left_sleeve', 'left_sleeve_cuff', 
                        'skirt', 'flare-skirt', 'godet-skirt', 'pencil-skirt', 'levels-skirt',  'pants', 'pants_cuff', 'overall']

parser = argparse.ArgumentParser()
parser.add_argument("--index", type=int, required=True, help="path to the save resules shapenet dataset")
parser.add_argument("--summary", default=False, action='store_true')
args = parser.parse_args()


def ordered(d, desired_key_order):
    return OrderedDict([(key, d[key]) for key in desired_key_order])


def recursive_simplify_params(cfg, new_config, parent_path='design'):
    # change float to 4 decimal places
    if cfg is None:
        print(parent_path)

    cfg_new = {}
    if ('type' not in cfg) or not isinstance(cfg['type'], str):
        for subpattern_n, subpattern_cfg_new in new_config.items():
            if subpattern_n not in cfg:
                # print('subpattern_n', parent_path, subpattern_n)
                cfg[subpattern_n] = {
                    'type': 'bool',
                    'range': [True, False],
                    'v': False
                }
                # continue

            subconfig = recursive_simplify_params(cfg[subpattern_n], subpattern_cfg_new, parent_path=parent_path + '.' + subpattern_n)
            cfg_new[subpattern_n] = subconfig
    
    else:
        if new_config == "NotUsed":
            return cfg
        
        else:
            cfg['v'] = new_config
            return cfg

    return cfg_new


def get_extra_config(change_name):
    if change_name in ['shirt']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'left.enable_asym': [False],
            'meta.wb': [None],
            'meta.bottom': [None]
        }

    if change_name in ['collar', 'sleeve']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'left.enable_asym': [False],
        }

    if change_name in ['sleeve_cuff']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'left.enable_asym': [False],
            'sleeve.sleeveless': [False]
        }

    if change_name in ['left_shirt']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'left.enable_asym': [True],
            'meta.wb': [None],
            'meta.bottom': [None]
        }

    if change_name in ['left_collar', 'left_sleeve']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'left.enable_asym': [True]
        }

    if change_name in ['left_sleeve_cuff']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'left.enable_asym': [True],
            'sleeve.sleeveless': [False]
        }

    if change_name in ['waistband']:
        require_dict = {
            'meta.wb': ['StraightWB', 'FittedWB'],
        }

    if change_name in ['flare-skirt']:
        require_dict = {
            'meta.bottom': ['SkirtCircle', 'AsymmSkirtCircle', 'SkirtManyPanels'],
            'meta.upper': [None]
        }

    if change_name in ['godet-skirt']:
        require_dict = {
            'meta.bottom': ['GodetSkirt'],
            'meta.upper': [None]
        }

    if change_name in ['pencil-skirt']:
        require_dict = {
            'meta.bottom': ['PencilSkirt'],
            'meta.upper': [None]
        }

    if change_name in ['levels-skirt']:
        require_dict = {
            'meta.bottom': ['SkirtLevels'],
            'meta.upper': [None]
        }

    if change_name in ['pants', 'pants_cuff']:
        require_dict = {
            'meta.bottom': ['Pants'],
            'meta.upper': [None]
        }

    if change_name in ['skirt']:
        require_dict = {
            'meta.bottom': ['Skirt2'],
            'meta.upper': [None]
        }

    if change_name in ['overall']:
        require_dict = {
            'meta.upper': ['Shirt', 'FittedShirt'],
            'meta.wb': ['StraightWB', 'FittedWB'],
        }

    return require_dict


def check_valid_changes(change_names, cfg):
    # cfg = edict(cfg)
    possible_names = []
    for change_name in change_names:
        request_dict = get_extra_config(change_name)
        flag = True
        for key, values in request_dict.items():
            myvalue = get_value_from_path(cfg, key)
            if myvalue['v'] not in values:
                flag = False
        if flag:
            possible_names.append(change_name)

    return possible_names
        

def get_value_from_path(nested_dict, path):
    keys = path.split(".")
    value = nested_dict
    for key in keys:
        value = value[key]
    return value


def get_changes_by_name(garment_path):
    garment_name = garment_path.split('/')[-1]
    new_config_path = os.path.join(garment_path, f'{garment_name}_design_params.yaml')

    if not os.path.exists(new_config_path):
        print('new_config_path', new_config_path)
        return None, False

    with open(new_config_path, 'r') as f:
        new_config = yaml.safe_load(f)

    flag = True
    new_config = new_config['design']

    ################ get unused_configs
    valid_changes = check_valid_changes(all_possible_changes, new_config)
    # print('valid_changes', valid_changes)

    return valid_changes, flag


body = BodyParameters('/is/cluster/fast/sbian/github/GarmentCodeV2/assets/bodies/mean_all.yaml')
def serialize_config(design, output_path, garment_name):
    config = {'design': design}
    if not os.path.exists(os.path.join(output_path, f'valid_garment_{garment_name}')):
        os.makedirs(os.path.join(output_path, f'valid_garment_{garment_name}'))

    with open(os.path.join(output_path, f'valid_garment_{garment_name}', 'design.yaml'), 'w') as f:
        yaml.dump(config, f)
        
    test_garment = MetaGarment('valid_garment', body, design)

    pattern = test_garment.assembly()
    if test_garment.is_self_intersecting():
        print(f'{test_garment.name} is Self-intersecting')
        return False

    # Save as json file
    folder = pattern.serialize(
        output_path, 
        tag=garment_name, 
        to_subfolder=True, 
        with_3d=False, with_text=False, view_ids=False)

    return True


def run_simultion_warp(pattern_spec, sim_config, output_path):
    from pygarment.meshgen.boxmeshgen import BoxMesh
    from pygarment.meshgen.simulation import run_sim
    import pygarment.data_config as data_config
    from pygarment.meshgen.sim_config import PathCofig
    
    props = data_config.Properties(sim_config) 
    props.set_section_stats('sim', fails={}, sim_time={}, spf={}, fin_frame={}, body_collisions={}, self_collisions={})
    props.set_section_stats('render', render_time={})

    spec_path = Path(pattern_spec)
    garment_name, _, _ = spec_path.stem.rpartition('_')  # assuming ending in '_specification'

    paths = PathCofig(
        in_element_path=spec_path.parent,  
        out_path=output_path, 
        in_name=garment_name,
        body_name='mean_all',    # 'f_smpl_average_A40'
        smpl_body=False,   # NOTE: depends on chosen body model
        add_timestamp=False,
        system_path='/is/cluster/fast/sbian/github/GarmentCodeV2/system.json'
    )

    # Generate and save garment box mesh (if not existent)
    print(f"Generate box mesh of {garment_name} with resolution {props['sim']['config']['resolution_scale']}...")
    print('\nGarment load: ', paths.in_g_spec)

    garment_box_mesh = BoxMesh(paths.in_g_spec, props['sim']['config']['resolution_scale'])
    garment_box_mesh.load()
    garment_box_mesh.serialize(
        paths, store_panels=False, uv_config=props['render']['config']['uv_texture'])

    props.serialize(paths.element_sim_props)

    run_sim(
        garment_box_mesh.name, 
        props, 
        paths,
        save_v_norms=False,
        store_usd=False,  # NOTE: False for fast simulation!
        optimize_storage=False,   # props['sim']['config']['optimize_storage'],
        verbose=False
    )
    
    props.serialize(paths.element_sim_props)


def get_target_str_by_name(garment_path, config_changes, idx, change_name):
    garment_name = garment_path.split('/')[-1]
    # print('garment_path', garment_path)
    new_config_path = os.path.join(garment_path, f'{garment_name}_design_params.yaml')

    if not os.path.exists(new_config_path):
        print('new_config_path', new_config_path)
        return None, False
    
    config_changes = copy.deepcopy(config_changes)
    with open(new_config_path, 'r') as f:
        new_config = yaml.safe_load(f)

    flag = True
    new_config = new_config['design']

    ################ get unused_configs
    unused_configs = []
    ub_garment = new_config['meta']['upper']['v']
    if ub_garment is None:
        unused_configs += ['shirt', 'collar', 'sleeve', 'left']
    else:
        use_left = new_config['left']['enable_asym']['v']
        if not use_left:
            unused_configs += ['left']
    
    wb_garment = new_config['meta']['wb']['v']
    if not wb_garment:
        unused_configs.append(wb_config_name)
    
    lower_garment = new_config['meta']['bottom']['v']
    assert lower_garment != 'null', (garment_path, lower_garment)
    if lower_garment is None:
        unused_configs += all_skirt_configs
    else:
        unused_configs += copy.deepcopy(all_skirt_configs)
        unused_configs.remove(skirt_configs[lower_garment])

        if 'base' in new_config[skirt_configs[lower_garment]]:
            base_garment = new_config[skirt_configs[lower_garment]]['base']['v']
            unused_configs.remove(skirt_configs[base_garment])
    
    new_config = recursive_simplify_params(new_config, config_changes)

    saved_folder = '/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures/new_garments'
    garment_name_new = f'{garment_name}__{idx}__{change_name}'
    try:
    # if True:
        flag = serialize_config(new_config, saved_folder, garment_name_new)
        path_dir = os.path.join(saved_folder, f'valid_garment_{garment_name_new}')
        paths = [item for item in os.listdir(path_dir) if item.endswith('_specification.json')]

        path = paths[0]
        path = os.path.join(path_dir, path)
        
        run_simultion_warp(
            path,
            '/is/cluster/fast/sbian/github/GarmentCodeV2/assets/Sim_props/default_sim_props.yaml',
            path_dir
        )

    except:
        flag = False
    
    return new_config, flag




def extract_all_floats(answerdata):
    #### get all floats
    left_bracket = [m.start() for m in re.finditer("'<", answerdata)]
    right_bracket = [m.start() for m in re.finditer(">'", answerdata)]

    all_floats = []
    answer_data_processed = ''
    last_end = 0
    for start_idx, end_idx in zip(left_bracket, right_bracket):
        float_str = answerdata[start_idx+2:end_idx-1]
        all_floats.append(float(float_str))

        answer_data_processed = answer_data_processed + answerdata[last_end:start_idx] + '[SEG]'
        last_end = end_idx + 2
    
    answer_data_processed = answer_data_processed + answerdata[last_end:]

    return answer_data_processed, all_floats


def extract_all_floats_wfloats(answerdata):
    #### get all floats
    left_bracket = [m.start() for m in re.finditer("'<", answerdata)]
    right_bracket = [m.start() for m in re.finditer(">'", answerdata)]


    answer_data_processed = ''
    last_end = 0
    for start_idx, end_idx in zip(left_bracket, right_bracket):
        float_str = answerdata[start_idx+2:end_idx-1]
        float_str_new = f'{float(float_str):.3f}'

        answer_data_processed = answer_data_processed + answerdata[last_end:start_idx] + float_str_new
        last_end = end_idx + 2
    
    answer_data_processed = answer_data_processed + answerdata[last_end:]

    return answer_data_processed


def get_all_paths_garmentcode():
    motion_dir = "/is/cluster/fast/sbian/data/bedlam_motion_for_blender/"
    saved_folder = '/ps/scratch/ps_shared/sbian/hood_simulation_garmentcode_v2'
    # saved_folder = '/is/cluster/fast/sbian/data/hood_simulation_garmentcode'

    saved_folder_final = '/ps/scratch/ps_shared/sbian/hood_simulation_garmentcode_v2'
    sampled_clothes_list_path = '/is/cluster/fast/sbian/github/GET3D/exp/aaa_mesh_registrarion/sampled_clothes_motion_list_train_v2.pkl'
    with open(sampled_clothes_list_path, 'rb') as f:
        sampled_clothes_list = pkl.load(f)

    return motion_dir, saved_folder, saved_folder_final, sampled_clothes_list


def process_summary_dict(summary_dict):
    summary_dict_new = {}
    for change, my_list in summary_dict.items():
        summary_dict_new[change] = my_list * 8

    return summary_dict_new


def get_garment_possible_changes():
    motion_dir, saved_folder, saved_folder_final, sampled_clothes_list = get_all_paths_garmentcode()

    new_folders_len = 10000
    all_indices = np.arange(new_folders_len)
    all_processed_indeces = all_indices

    garment_summary_dict = {}

    for idx in tqdm(all_processed_indeces, dynamic_ncols=True):
        sampled_clothes_dict = sampled_clothes_list[idx]

        if 'upper_garment' in sampled_clothes_dict:
            upper_garment_path = sampled_clothes_dict['upper_garment']
            changes_upper, valid_flag1 = get_changes_by_name(upper_garment_path)

            lower_garment_path = sampled_clothes_dict['lower_garment']
            changes_lower, valid_flag2 = get_changes_by_name(lower_garment_path)

            if not valid_flag1 or not valid_flag2:
                continue

            for change in changes_upper:
                if change not in garment_summary_dict:
                    garment_summary_dict[change] = []
                garment_summary_dict[change].append( (idx, 'upper_garment') )
            
            for change in changes_lower:
                if change not in garment_summary_dict:
                    garment_summary_dict[change] = []
                garment_summary_dict[change].append( (idx, 'lower_garment') )
            
            
        else:
            garment_path = sampled_clothes_dict['whole_garment']
            changes, valid_flag = get_changes_by_name(garment_path)

            if not valid_flag:
                continue

            for change in changes:
                if change not in garment_summary_dict:
                    garment_summary_dict[change] = []
                garment_summary_dict[change].append( (idx, 'whole_garment') )

    with open('/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures/garment_summary_dict.pkl', 'wb') as f:
        pkl.dump(garment_summary_dict, f)
    
    for change, change_indices in garment_summary_dict.items():
        print(change, len(change_indices))


def main():
    motion_dir, saved_folder, saved_folder_final, sampled_clothes_list = get_all_paths_garmentcode()
    with open('/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures/garment_summary_dict.pkl', 'rb') as f:
        garment_summary_dict = pkl.load(f)
    
    with open('/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures/summary_dict.json', 'r') as f:
        summary_dict = json.load(f)
    
    # print(list(summary_dict.keys()))
    # assert False
    final_saved_path = '/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures'


    random.seed(9 * args.index)
    cnt = 0
    for change, change_indices in summary_dict.items():
        if change == 'left':
            continue

        garment_list = garment_summary_dict[change]

        change_indices_len = len(change_indices) // 100 + 1
        change_indices = change_indices[change_indices_len*args.index : change_indices_len*(args.index+1)]
        succcess_cnt = 0
        for change_index in change_indices:
            cnt += 1
            print('cnt', cnt)
            configure_change_path = os.path.join(final_saved_path, f'changed_config_{change_index}_{change}.yaml')
            if not os.path.exists(configure_change_path):
                continue

            with open(configure_change_path, 'r') as f:
                change_config = yaml.safe_load(f)

            if change == 'shirt' and isinstance(change_config['shirt']['openfront'], bool) and change_config['shirt']['openfront']:
                choosed_indices = random.sample(garment_list, 16)
            else:
                choosed_indices = random.sample(garment_list, 8)

            # print('succcess_cnt', succcess_cnt)
            succcess_cnt = 0
            for choosed_idx, name in choosed_indices:
                garment_path = sampled_clothes_list[int(choosed_idx)][name]
                _, flag = get_target_str_by_name(garment_path, change_config, change_index, change)

                if flag:
                    succcess_cnt += 1
                    if succcess_cnt >= 4:
                        break
            
            print('succcess_cnt', succcess_cnt, change, change_index)


def summary_folders():
    saved_parent_folder = "/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures/new_garments"
    all_folders = os.listdir(saved_parent_folder)
    all_folders = [item for item in all_folders if os.path.isdir(os.path.join(saved_parent_folder, item))]
    all_folders = sorted(all_folders)

    print('all_folders', len(all_folders))

    summary_dict = {}
    for folder in all_folders:
        change_name = folder.split('__')[-1]
        change_idx = folder.split('__')[-2]
        if change_idx not in summary_dict:
            summary_dict[change_idx] = []
        summary_dict[change_idx].append(folder)
    
    with open('/is/cluster/fast/sbian/data/blender_simulation_garmentcode_llava_labels/random_configures/summary_dict_newgarments.json', 'w') as f:
        json.dump(summary_dict, f)


if __name__ == "__main__":
    # get_garment_possible_changes()
    if args.summary:
        summary_folders()
    else:
        main()
    # # summary_folders()
