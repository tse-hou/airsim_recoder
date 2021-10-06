import csv
import os
import airsim
import msgpackrpc
import numpy as np
import cv2
import sys
import math
import json
from sys import argv
np.set_printoptions(threshold=sys.maxsize)
RESOLUTION = [1280, 720]


class Camera_pose:
    def __init__(self):
        self.name = ""
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.roll = 0


def convert_between_MIV_airsim_coordinate(input_camera_pose):
    '''
    Description: 
    convert MIV and airsim coordinate to each other
    @para input_camera_pose: input camera pose (type: Camera_pose)
    '''
    output_camera_pose = Camera_pose()
    output_camera_pose.x = input_camera_pose.x
    output_camera_pose.y = -input_camera_pose.y
    output_camera_pose.z = -input_camera_pose.z
    output_camera_pose.roll = input_camera_pose.roll
    output_camera_pose.pitch = -input_camera_pose.pitch
    output_camera_pose.yaw = -input_camera_pose.yaw
    return output_camera_pose


def import_cameras_pose(csvfile_path):
    '''
    Description: 
    read csv file to import .csv file of camera pose. 
    The csv file contains: camera_name,x,y,z,roll,pitch,yaw 
    The input camera pose is in Airsim coordinate system
    @para csvfile_path: the path of csv file (type: string)
    @return cameras_pose: return a set of camera poses (type: list), including all of camera pose in camera placement
    '''
    cameras_pose = []
    with open(csvfile_path, 'r') as csv_f:
        rows = csv.reader(csv_f)
        for row in rows:
            camera_pose = Camera_pose()
            camera_pose.name = row[0]
            position = [float(x) for x in row[1:4]]  # x, y, z
            rotation = [float(x) for x in row[4:7]]  # roll, pitch, yaw
            camera_pose.x = position[0]
            camera_pose.y = position[1]
            camera_pose.z = position[2]
            camera_pose.roll = rotation[0]
            camera_pose.pitch = rotation[1]
            camera_pose.yaw = rotation[2]
            cameras_pose.append(camera_pose)
    return cameras_pose


def set_camera_pose_to_airsim(client, camera_pose):
    '''
    Description: 
    set camera pose of vehicle in Airsim
    @para client: Airsim client
    @para camera_pose: camera pose in Airsim coordinate (type: Camera_pose)
    '''
    client.simSetCameraPose("front_center", airsim.Pose(
        airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0)))
    client.simSetVehiclePose(
        airsim.Pose(
            airsim.Vector3r(
                camera_pose.x, camera_pose.y, camera_pose.z),
            airsim.to_quaternion(
                camera_pose.pitch*math.pi/180, camera_pose.roll*math.pi/180, camera_pose.yaw*math.pi/180),
        ),
        True
    )


def request_video_from_airsim(client):
    '''
    Description: 
    get image responses from Airsim 
    @para client: Airsim client
    @return responses: a list contains all of requested image
    '''
    responses = client.simGetImages([
        airsim.ImageRequest(
            "front_center", airsim.ImageType.DisparityNormalized, True),
        # "0", airsim.ImageType.DepthPlanar, True),
        # "0", airsim.ImageType.DepthPerspective),
        airsim.ImageRequest(
            "front_center", airsim.ImageType.Scene, False, False)
    ])  # scene vision image in uncompressed RGB array
    return responses


def save_videos_from_responses(responses, camera_name, zmin, zmax):
    '''
    Description: 
    save requested image into video/image file
    it save different kind of image with different manner
    For example, for depth value, save it in raw video format (.yuv)
    @para responses: a list of reponse from Airsim 
    @para camera_name: the name of camera (type: string)
    @para zmin: the minimal depth value in all of depth maps (type: float)
    @para zmax: the maximal depth value in all of depth maps (type: float)
    '''
    print('Retrieved images: %d' % len(responses))
    for response_idx, response in enumerate(responses):
        filename = os.path.normpath(
            f"test_miv/{camera_name}/{response.image_type}_{response_idx}")

        if response.pixels_as_float:
            print("Type %d, size %d" %
                  (response.image_type, len(response.image_data_float)))
            print(response.height, response.width)
            response_float_data = response.image_data_float
            response_float_data = 0.125/np.array(response_float_data)
            response_float_data = response_float_data.flatten()
            depth_16bit = (((1/response_float_data-1/zmax) /
                           (1/zmin-1/zmax)) * 65535)
            depth_16bit = depth_16bit.astype(np.int16)
            yuv_frames = np.append(depth_16bit, np.full(
                int(len(depth_16bit)/2), 32768, dtype=np.int16))
            print(yuv_frames.dtype)
            print(yuv_frames.shape)
            fileobj = open(f"{filename}.yuv", mode='wb')
            yuv_frames.tofile(fileobj)
        elif response.compress:  # png format
            print("Type %d, size %d" %
                  (response.image_type, len(response.image_data_uint8)))
            airsim.write_file(filename + '.png',
                              response.image_data_uint8)
            # convert Depth video into yuv420p16le (monochrome)
            os.system(
                f"powershell ffmpeg -i {filename}.png -pix_fmt yuv420p16le {filename}.yuv")
            os.system(f"powershell rm {filename}.png")
        else:  # uncompressed array
            print("Type %d, size %d" %
                  (response.image_type, len(response.image_data_uint8)))
            img1d = np.fromstring(
                response.image_data_uint8, dtype=np.uint8)  # get numpy array
            # reshape array to 3 channel image array H X W X 3
            img_rgb = img1d.reshape(response.height, response.width, 3)
            cv2.imwrite(filename + '.png', img_rgb)  # write to png
            # convert RGB video into yuv420p10le
            if(response.image_type == 0):
                os.system(
                    f"powershell ffmpeg -i {filename}.png -pix_fmt yuv420p10le {filename}.yuv")
                os.system(f"powershell rm {filename}.png")


def duplicate_yuv(camera_name, num_frame, output_dataset_name):
    '''
    Description: 
    duplicate frame to produce video
    usually, we only capture single frame from Airsim because capture depth map need a lot of time
    so we duplicate it to produce video if we need video to conduct experiment
    @para camera_name: the name of camera (type: string)
    @para num_frame: number of frame of output video (type: int)
    @para output_dataset_name: the output dataset name (type: string)
    '''
    for i in range(num_frame):
        print(f"{camera_name} frame {i}")
        os.system(
            f"type test_miv\\{camera_name}\\0_1.yuv >> test_miv\{output_dataset_name}\{camera_name}_texture_{RESOLUTION[0]}x{RESOLUTION[1]}_yuv420p10le.yuv")
        os.system(
            f"type test_miv\\{camera_name}\\4_0.yuv >> test_miv\{output_dataset_name}\{camera_name}_depth_{RESOLUTION[0]}x{RESOLUTION[1]}_yuv420p16le.yuv")


def gernerate_camera_para_json(cameras_pose, num_frames, zmin, zmax, output_dataset_name):
    '''
    Description: 
    generate json file of camera parameter for MIV codec
    @para cameras_pose: a list of camera poses
    @para num_frames: number of frame of video (type: int)
    @para zmin: the minimal depth value in all of depth maps (type: float)
    @para zmax: the maximal depth value in all of depth maps (type: float)
    @para output_dataset_name: the output dataset name (type: string)
    '''
    camera_parameter = {}
    camera_parameter["BoundingBox_center"] = [0, 0, 0]
    camera_parameter["Fps"] = 30
    camera_parameter["Content_name"] = output_dataset_name
    camera_parameter["Frames_number"] = num_frames
    camera_parameter["lengthsInMeters"] = True
    camera_parameter["sourceCameraNames"] = [
        camera_pose.name for camera_pose in cameras_pose]
    camera_parameter["cameras"] = []
    for camera_pose in cameras_pose:
        camera = {}
        camera["BitDepthColor"] = 10
        camera["BitDepthDepth"] = 16
        camera["Name"] = camera_pose.name
        camera["Depth_range"] = [zmin, zmax]
        camera["DepthColorSpace"] = "YUV420"
        camera["ColorSpace"] = "YUV420"
        MIV_camera_pose = convert_between_MIV_airsim_coordinate(
            camera_pose)
        camera["Position"] = [MIV_camera_pose.x,
                              MIV_camera_pose.y, MIV_camera_pose.z]  # x, y, z
        camera["Rotation"] = [MIV_camera_pose.yaw,
                              MIV_camera_pose.pitch, MIV_camera_pose.roll]  # yaw, pitch, roll
        camera["Resolution"] = RESOLUTION
        camera["Projection"] = "Perspective"
        camera["HasInvalidDepth"] = False
        camera["Depthmap"] = 1
        camera["Background"] = 0
        # F = w / (2 * tan(FOV/2))
        camera["Focal"] = [
            camera["Resolution"][0] / (2 * math.tan(90/2 * math.pi/180)), camera["Resolution"][0] / (2 * math.tan(90/2 * math.pi/180))]
        # print(camera["Focal"])
        # w / 2, h / 2
        camera["Principle_point"] = [
            camera["Resolution"][0]/2, camera["Resolution"][1]/2]
        camera_parameter["cameras"].append(camera)
    viewport_parameter = camera_parameter["cameras"][0].copy()
    viewport_parameter["Name"] = "viewport"
    viewport_parameter["Position"] = [0.0, 0.0, 0.0]
    viewport_parameter["Rotation"] = [0.0, 0.0, 0.0]
    viewport_parameter["HasInvalidDepth"] = True
    camera_parameter["cameras"].append(viewport_parameter)

    out_file = open(
        f"test_miv/{output_dataset_name}/{output_dataset_name}.json", "w")
    json.dump(camera_parameter, out_file)


def get_zmin_zmax(responses):
    '''
    Description: 
    calculate zmin and zmax from requested depth map from Airsim
    @para responses: a list of requested depth map
    '''
    response = responses[0].image_data_float
    response = 0.125/np.array(response)
    print(response.max())
    print(response.min())
    print(response.shape)
    return response.min(), response.max()


def argparser():
    '''
    entry point 
    '''
    if(len(argv) == 1 or argv[1] == "-h"):
        print("********** Usage *************")
        print("Capture source views for MIV:")
        print("- python recorder_for_MIV.py SV {camera_pose_csv} {num_frames}")
        print("Capture Ground truth video:")
        print("- python recorder_for_MIV.py GT {user_pose_csv}")
        print("Clean output folder:")
        print("- python recorder_for_MIV.py clean")
        sys.exit()
    elif(argv[1] == "clean"):
        os.system("powershell rm -r test_miv/v*")
        os.system("powershell rm -r test_miv/GT_tmp")
        sys.exit()
    elif(argv[1] == "GT"):
        cameras_pose = import_cameras_pose(argv[2])
        num_frames = len(cameras_pose)
        GT_main(cameras_pose, num_frames)
    elif(argv[1] == "SV"):
        # input camera postion and rotation from .csv
        cameras_pose = import_cameras_pose(argv[2])
        num_frames = int(argv[3])
        output_dataset_name = argv[4]
        SV_main(cameras_pose, num_frames, output_dataset_name)


def SV_main(cameras_pose, num_frames, output_dataset_name):
    '''
    Description:
    main function for capturing source view
    @para camera_pose: camera pose of each source views (read from .csv file)
    @para num_frames: num. of frame of source views
    @para output_dataset_name: output dataset name
    '''
    # Connect to airsim
    print(msgpackrpc.__version__)
    client = airsim.MultirotorClient()
    client.confirmConnection()
    all_SV_responses = []
    # Get SV data
    for camera_pose in cameras_pose:
        print(camera_pose.name)
        set_camera_pose_to_airsim(client, camera_pose)
        responses = request_video_from_airsim(client)
        all_SV_responses.append(responses)
    # Find zmin, zmax
    zmin = 999999999.0
    zmax = 0.0
    for responses in all_SV_responses:
        lzmin, lzmax = get_zmin_zmax(responses)
        if (zmin > lzmin):
            zmin = lzmin
        if (zmax < lzmax):
            zmax = lzmax
    print("zmin, zmax:", zmin, zmax)
    os.system(f"powershell mkdir test_miv/{output_dataset_name}")
    # Save video file
    for idx, responses in enumerate(all_SV_responses):
        os.system(f"powershell mkdir test_miv/{cameras_pose[idx].name}")
        save_videos_from_responses(responses, cameras_pose[idx], zmin, zmax)
        duplicate_yuv(cameras_pose[idx].name, num_frames, output_dataset_name)
    # Generate camera parameter JSON file
    gernerate_camera_para_json(
        cameras_pose, num_frames, zmin, zmax, output_dataset_name)


def GT_main(cameras_pose):
    '''
    Description:
    main function for capturing ground truth
    @para camera_pose: user pose of each frame (read from .csv)
    '''
    # Connect to airsim
    print(msgpackrpc.__version__)
    client = airsim.MultirotorClient()
    client.confirmConnection()

    # create tmp folder
    os.system(f"powershell mkdir test_miv/GT_tmp")
    # Get GT data
    for f_idx, camera_pose in enumerate(cameras_pose):
        set_camera_pose_to_airsim(client, camera_pose)
        responses = client.simGetImages([
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
        ])
        filename = f"test_miv/GT_tmp/{f_idx}"
        for response in responses:
            print("Type %d, size %d" %
                  (response.image_type, len(response.image_data_uint8)))
            img1d = np.fromstring(
                response.image_data_uint8, dtype=np.uint8)  # get numpy array
            # reshape array to 3 channel image array H X W X 3
            img_rgb = img1d.reshape(response.height, response.width, 3)
            cv2.imwrite(filename + '.png', img_rgb)  # write to png
            # convert RGB video into yuv420p10le
            os.system(
                f"powershell ffmpeg -i {filename}.png -pix_fmt yuv420p10le {filename}.yuv")
            os.system(f"powershell rm {filename}.png")
        # save captured frame into GT file
        os.system(
            f"type test_miv\GT_tmp\{f_idx}.yuv >> test_miv\GT\GT_texture_{RESOLUTION[0]}x{RESOLUTION[1]}_yuv420p10le.yuv")
    # delete tmp folder
    os.system("powershell rm -r test_miv/GT_tmp")


if __name__ == "__main__":
    argparser()
