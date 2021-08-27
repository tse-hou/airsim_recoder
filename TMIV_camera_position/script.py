import os
import move_camera_array
camera_center_ArchVizInterior = ['usr', 0, 0, 1, 0, 0, 0]
camera_center_LightroomInteriorDayLight = ['usr', 0, -5, 1.5, 90, 0, 0]
camera_center_office = ['usr', 2.6, -2.5, 1.3, 90, 0, 0]
camera_center_RealisticRendering = ['usr', 0, 2.7, 1.1, 270, 0, 0]
camera_center_XoioBerlinFlat = ['usr', 0.9, 0.8, 1.2, 180, 0, 0]

camera_centers = [["ArchVizInterior", camera_center_ArchVizInterior],
                  ["LightroomInteriorDayLight",
                      camera_center_LightroomInteriorDayLight],
                  ['office', camera_center_office],
                  ['RealisticRendering', camera_center_RealisticRendering],
                  ['XoioBerlinFlat', camera_center_XoioBerlinFlat]]

camera_settings = ['6x6', '9x4', '12x3', '18x2']

for camera_center in camera_centers:
    os.system(
        f'powershell mkdir TMIV_camera_position\camera_pose\{camera_center[0]}')
    for camera_setting in camera_settings:
        move_camera_array.main(camera_center[1], f'TMIV_camera_position\camera_setting\{camera_setting}_camera_array.csv',
                               f'TMIV_camera_position\camera_pose\{camera_center[0]}\{camera_setting}_camera_array.csv')
