import os
import sys
import argparse
import json
from pathlib import Path
import shutil

# from llava.garment_utils_v2 import run_simultion_warp
sys.path.append('/is/cluster/fast/sbian/github/GarmentCodeV2/')
from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters

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


parser = argparse.ArgumentParser()
parser.add_argument("--garment_json_path", type=str, default='', help="path to the save resules shapenet dataset")
parser.add_argument("--garment_parent_path", type=str, default='', help="path to the save resules shapenet dataset")
parser.add_argument("--json_spec_file", type=str, default='', help="path to the save resules shapenet dataset")

args = parser.parse_args()

if len(args.garment_json_path) == 0 and len(args.garment_parent_path) > 1:
    args.garment_json_path = os.path.join(args.garment_parent_path, 'vis_new/all_json_spec_files.json')

    with open(args.garment_json_path) as f:
        garment_json = json.load(f)

elif len(args.json_spec_file) > 0:
    garment_json = [args.json_spec_file]

else:
    with open(args.garment_json_path) as f:
        garment_json = json.load(f)

print(len(garment_json))
# assert False

for json_spec_file in garment_json:
    print(json_spec_file)
    json_spec_file = json_spec_file.replace('validate_garment', 'valid_garment')
    saved_folder = os.path.dirname(json_spec_file)
    try:
        run_simultion_warp(
                json_spec_file,
                'assets/Sim_props/default_sim_props.yaml',
                saved_folder
            )
    except Exception as e:
        print(e)
        print('Error in running simulation for ', json_spec_file)
        continue
