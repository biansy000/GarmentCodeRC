import os
import shutil
from pygarment.meshgen.render.pythonrender2 import render_images

import trimesh

obj_path = '/is/cluster/fast/sbian/github/LLaVA/runs/try_7b_lr1e_4_v3_garmentcontrol_4h100_nodetail_2step_CLOSE_eva/vis_new/valid_garment_10011_2234/valid_garment_upper/valid_garment_upper/valid_garment_upper_sim.obj'
obj_pathbackup = obj_path.replace('.obj', '_backup.obj')

# copy
# shutil.copy(obj_path, obj_pathbackup)

with open(obj_path, 'r') as f:
    lines = f.readlines()

lin0 = lines[0]
lines[0] = lin0.strip().split(' ')
lines[0] = ' '.join([lines[0][0], '/is/cluster/fast/sbian/github/GarmentCodeV2/new_material.mtl\n'])

with open(obj_pathbackup, 'w') as f:
    f.writelines(lines)
    # f.write(lines)


obj_path = obj_pathbackup
body_path = 'assets/bodies/mean_all.obj'
saved_path = 'try_imgs/try.png'
bodymesh = trimesh.load(body_path)
render_images(bodymesh.vertices * 100, bodymesh.faces, obj_path, saved_path)