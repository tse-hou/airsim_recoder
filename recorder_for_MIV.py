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


class Camera_pose:
    def __init__(self):
        self.name = ""
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]


def import_cameras_pose(csvfile_PATH):
    cameras_pose = []
    with open(csvfile_PATH, 'r') as csv_f:
        rows = csv.reader(csv_f)
        for row in rows:
            camera_pose = Camera_pose()
            camera_pose.name = row[0]
            camera_pose.position = [float(x) for x in row[1:4]]
            camera_pose.rotation = [float(x) for x in row[4:7]]
            cameras_pose.append(camera_pose)
    return cameras_pose


def set_camera_pose(client, camera_pose):
    client.simSetVehiclePose(
        airsim.Pose(
            airsim.Vector3r(
                camera_pose.position[0], camera_pose.position[1], camera_pose.position[2]),
            airsim.to_quaternion(
                camera_pose.rotation[0], camera_pose.rotation[1], camera_pose.rotation[2]),
        ),
        True,
    )


def request_video_from_airsim(client):
    responses = client.simGetImages([
        airsim.ImageRequest(
            "0", airsim.ImageType.DepthPerspective),
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])  # scene vision image in uncompressed RGB array
    return responses


def save_videos_from_responses(responses, camera_pose, frame_idx):
    print('Retrieved images: %d' % len(responses))
    for response_idx, response in enumerate(responses):
        filename = os.path.normpath(
            f"test_miv/{camera_pose.name}/{frame_idx}_{response.image_type}_{response_idx}")

        if response.pixels_as_float:
            print("Type %d, size %d" %
                  (response.image_type, len(response.image_data_float)))
            print(np.array(response.image_data_float).max())
            print(np.array(response.image_data_float).min())
            print(np.array(response.image_data_float).shape)
            airsim.write_pfm(filename + '.pfm',
                             airsim.get_pfm_array(response))
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
            os.system(
                f"powershell ffmpeg -i {filename}.png -pix_fmt yuv420p10le {filename}.yuv")
            os.system(f"powershell rm {filename}.png")


def merge_yuv(camera_pose):
    os.system(
        f"type test_miv\{camera_pose.name}\*_0_1.yuv > test_miv\output\{camera_pose.name}_texture_1920x1080_yuv420p10le.yuv")
    os.system(
        f"type test_miv\{camera_pose.name}\*_2_0.yuv > test_miv\output\{camera_pose.name}_depth_1920x1080_yuv420p16le.yuv")


def gernerate_camera_para_json(cameras_pose, num_frames):
    camera_parameter = {}
    camera_parameter["Content_name"] = "test"
    camera_parameter["Frames_number"] = num_frames
    camera_parameter["lengthsInMeters"] = True
    camera_parameter["sourceCameraNames"] = [
        camera_pose.name for camera_pose in cameras_pose]
    camera_parameter["cameras"] = []
    for camera_pose in cameras_pose:
        camera = {}
        camera["BoundingBox_center"] = [0, 0, 0]
        camera["Fps"] = 30
        camera["BitDepthColor"] = 10
        camera["BitDepthDepth"] = 16
        camera["Name"] = camera_pose.name
        camera["Depth_range"] = [0.1, 1000]
        camera["DepthColorSpace"] = "YUV420"
        camera["ColorSpace"] = "YUV420"
        camera["Position"] = camera_pose.position
        camera["Rotation"] = camera_pose.rotation
        camera["Resolution"] = [1920, 1080]
        camera["Projection"] = "Perspective"
        camera["HasInvalidDepth"] = False
        camera["Depthmap"] = 1
        camera["Background"] = 0
        # f = w / 2 x tan(FoV / 2)
        camera["Focal"] = [1920/2*math.tan(90/2), 1920/2*math.tan(90/2)]
        # w / 2, h / 2
        camera["Principle_point"] = [960, 540]
        camera_parameter["cameras"].append(camera)
    out_file = open("test_miv/output/test.json", "w")
    json.dump(camera_parameter, out_file)


def arg_parser():
    if(len(argv) == 1 or argv[1] == "h"):
        print("********** Usage *************")
        print("Capture dataset for MIV:")
        print("- python recorder_for_MIV.py {camera_pose_csv} {num_frames}")
        print("Clean output folder:")
        print("- python recorder_for_MIV.py q")
        sys.exit()
    elif(argv[1] == "q"):
        os.system("powershell rm -r test_miv/v*")
        os.system("powershell rm test_miv/output/*")
        sys.exit()

    # input camera postion and rotation from .csv
    cameras_pose = import_cameras_pose(argv[1])
    num_frames = int(argv[2])
    return cameras_pose, num_frames


def main():
    cameras_pose, num_frames = arg_parser()
    # connect to airsim
    print(msgpackrpc.__version__)
    client = airsim.MultirotorClient()
    client.confirmConnection()
    # capture RGBD from various camera pose in Airsim
    for camera_pose in cameras_pose:
        set_camera_pose(client, camera_pose)
        os.system(f"powershell mkdir test_miv/{camera_pose.name}")
        for frame_idx in range(num_frames):
            responses = request_video_from_airsim(client)
            save_videos_from_responses(responses, camera_pose, frame_idx)
        merge_yuv(camera_pose)
    # Generate camera parameter JSON file
    gernerate_camera_para_json(cameras_pose, num_frames)


if __name__ == "__main__":
    main()
