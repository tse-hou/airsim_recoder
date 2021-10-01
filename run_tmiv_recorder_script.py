import os

camera_settings = ['6x6', '9x4', '12x3', '18x2']
# camera_settings = ['18x2']
dataset_name_list = ["ArchVizInterior",
                     "LightroomInteriorDayLight",
                     'office',
                     'RealisticRendering',
                     'XoioBerlinFlat']
dataset_name = dataset_name_list[0]
for camera_setting in camera_settings:
    os.system(
        f"powershell python recorder_for_MIV.py SV TMIV_camera_position\camera_pose\{dataset_name}\{camera_setting}_camera_array.csv 1 {camera_setting}_{dataset_name}")
    os.system("powershell python recorder_for_MIV.py clean")
