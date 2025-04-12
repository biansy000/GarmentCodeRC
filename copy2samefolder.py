import subprocess
import argparse
import os
import shutil


all_paths = [
    '/is/cluster/fast/sbian/github/GarmentCodeV2/Logs/SKIRT_base_241114-10-15-33/SKIRT_base_sim.obj',
    '/is/cluster/fast/sbian/github/GarmentCodeV2/Logs/SKIRT_base_241114-10-13-25/SKIRT_base_sim.obj',
    '/is/cluster/fast/sbian/github/GarmentCodeV2/Logs/SHIRT_base_241114-10-21-15/SHIRT_base_sim.obj',
    '/is/cluster/fast/sbian/github/GarmentCodeV2/Logs/SHIRT_base_241114-10-19-29/SHIRT_base_sim.obj',
    '/is/cluster/fast/sbian/github/GarmentCodeV2/Logs/PANTS_base_241114-10-53-25/PANTS_base_sim.obj',
    '/is/cluster/fast/sbian/github/GarmentCodeV2/Logs/PANTS_base_241114-10-24-31/PANTS_base_sim.obj',

    '/is/cluster/fast/sbian/github/LLaVA/runs/try_v16_13b_lr1e_4_v3_garmentcontrol_4h100_openai_imgs_cropped_crop/vis_new/valid_garment_00148__Inner__Take1/valid_garment_wholebody/valid_garment_wholebody/valid_garment_wholebody_sim.obj',
    
    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_multiturn_close_skirt/vis_new/valid_garment_example_for_sgar/valid_garment_lower/valid_garment_lower/valid_garment_lower_sim.obj',
    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_multiturn_close_skirt/vis_new/valid_garment_example_for_sgar/valid_garment_modified_0/valid_garment_modified_0/valid_garment_modified_0_sim.obj',
    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_multiturn_close_skirt/vis_new/valid_garment_example_for_sgar/valid_garment_modified_1/valid_garment_modified_1/valid_garment_modified_1_sim.obj',
    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_multiturn_close_skirt/vis_new/valid_garment_example_for_sgar/valid_garment_modified_2/valid_garment_modified_2/valid_garment_modified_2_sim.obj',

    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_IMGmultiturn_close_skirt2/vis_new/valid_garment_example_for_sgar/valid_garment_modified_0/valid_garment_modified_0/valid_garment_modified_0_sim.obj',

    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_multiturn_close/vis_new/valid_garment_10036_3987/valid_garment_modified_0/valid_garment_modified_0/valid_garment_modified_0_sim.obj',
    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_multiturn_close/vis_new/valid_garment_10036_3987/valid_garment_modified_1/valid_garment_modified_1/valid_garment_modified_1_sim.obj',

    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_2step_CLose_eva/vis_new/valid_garment_10001_1938/valid_garment_upper/valid_garment_upper/valid_garment_upper_sim.obj',
    '/is/cluster/fast/sbian/github/LLaVA/runs/try_lr1e_4_wholebody_pose_v2_detailT2_upd_possibleDebug_v3_garmentcontrol_addFTdata_openai_imgwild_eva/vis_new/valid_garment_80141ce740f489f1d2f57a03f32c7577a28b62a6ac790a0d9ed8a18d961c2918/valid_garment_wholebody/valid_garment_wholebody/valid_garment_wholebody_sim.obj'
]

print(len(all_paths))
# assert False

# def get_command_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--index', '-i', help='index of the garment', type=int, default=0)
#     args = parser.parse_args()
#     return args

# args = get_command_args()

def call_ffmpeg(input_file, output_file):
    command = [
        "ffmpeg",
        "-framerate", "30",
        "-start_number", "0",
        "-i", input_file,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_file, '-y'
    ]
    subprocess.run(command, check=True)


# input_filename = 'try_imgs/try_%d.png'
# saved_path = 'animation_001.mp4'
# call_ffmpeg(input_filename, saved_path)
for index in range(15):
    obj_path = all_paths[index]

    obj_dir = os.path.dirname(obj_path)
    saved_dir = os.path.join(obj_dir, 'rounded_imgs')
    # if not os.path.exists(saved_dir):
    #     os.makedirs(saved_dir)
    # saved_path = os.path.join(saved_dir, 'try_%d.png')

    video_path = os.path.join(obj_dir, 'rounded_video.mp4')

    shutil.copy(video_path, os.path.join('summaryfolder', f'{index}.mp4'))