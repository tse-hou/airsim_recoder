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
import matplotlib.pyplot as plt
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
                camera_pose.position[0], -camera_pose.position[1], -camera_pose.position[2]),
            airsim.to_quaternion(
                -camera_pose.rotation[1]*math.pi/180, camera_pose.rotation[2]*math.pi/180, -camera_pose.rotation[0]*math.pi/180),
        ),
        True,
    )


def request_video_from_airsim(client):
    responses = client.simGetImages([
        airsim.ImageRequest(
            # "0", airsim.ImageType.DepthPerspective, True, False),
            "0", airsim.ImageType.DepthPlanar, True),
        # "0", airsim.ImageType.DepthPerspective),
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
    ])  # scene vision image in uncompressed RGB array
    return responses


def save_videos_from_responses(responses, camera_pose, zmin, zmax):
    print('Retrieved images: %d' % len(responses))
    for response_idx, response in enumerate(responses):
        filename = os.path.normpath(
            f"test_miv/{camera_pose.name}/{response.image_type}_{response_idx}")

        if response.pixels_as_float:
            print("Type %d, size %d" %
                  (response.image_type, len(response.image_data_float)))
            print(response.height, response.width)
            depth_img_in_meters = airsim.list_to_2d_float_array(
                response.image_data_float, response.width, response.height)
            depth_img_in_meters = depth_img_in_meters.reshape(
                response.height, response.width, 1)
            # depth_img_in_meters = np.reshape(
            #     response.image_data_float, (response.height, response.width))
            # depth_16bit = (1/(depth_img_in_meters * 10) * 65535).astype(int)
            depth_16bit = (((1/depth_img_in_meters-1/zmax) /
                           (1/zmin-1/zmax)) * 65535)
            print(depth_16bit.max())
            print(depth_16bit.min())
            print(depth_16bit.shape)
            # print(depth_16bit[0])
            # plt.bar(np.arange(len(depth_16bit.flatten())),
            #         depth_16bit.flatten())
            # plt.show()
            cv2.imwrite(f"{filename}.png", depth_16bit.astype('uint16'))
            os.system(
                f"powershell ffmpeg -i {filename}.png -pix_fmt yuv420p16le {filename}.yuv")
            # os.system(f"powershell rm {filename}.png")
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


def merge_yuv(camera_pose):
    os.system(
        f"type test_miv\{camera_pose.name}\*_0_1.yuv > test_miv\output\{camera_pose.name}_texture_480x270_yuv420p10le.yuv")
    os.system(
        f"type test_miv\{camera_pose.name}\*_1_0.yuv > test_miv\output\{camera_pose.name}_depth_480x270_yuv420p16le.yuv")


def duplicate_yuv(camera_pose, num_frame):
    for i in range(num_frame):
        print(f"{camera_pose.name} frame {i}")
        os.system(
            f"type test_miv\\{camera_pose.name}\\0_1.yuv >> test_miv\output\{camera_pose.name}_texture_480x270_yuv420p10le.yuv")
        os.system(
            f"type test_miv\\{camera_pose.name}\\1_0.yuv >> test_miv\output\{camera_pose.name}_depth_480x270_yuv420p16le.yuv")


def gernerate_camera_para_json(cameras_pose, num_frames, zmin, zmax):
    camera_parameter = {}
    camera_parameter["BoundingBox_center"] = [0, 0, 0]
    camera_parameter["Fps"] = 30
    camera_parameter["Content_name"] = "simple_dataset"
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
        camera["Position"] = camera_pose.position
        camera["Rotation"] = camera_pose.rotation
        camera["Resolution"] = [480, 270]
        camera["Projection"] = "Perspective"
        camera["HasInvalidDepth"] = False
        camera["Depthmap"] = 1
        camera["Background"] = 0
        # F = w / (2 * tan(FOV/2 * pi/180))
        camera["Focal"] = [
            camera["Resolution"][0] / (2 * math.tan(90/2 * math.pi/180)), camera["Resolution"][0] / (2 * math.tan(90/2 * math.pi/180))]
        # print(camera["Focal"])
        # w / 2, h / 2
        camera["Principle_point"] = [
            camera["Resolution"][0]/2, camera["Resolution"][1]/2]
        camera_parameter["cameras"].append(camera)
    out_file = open("test_miv/output/simple_dataset.json", "w")
    json.dump(camera_parameter, out_file)


def get_zmin_zmax(client):
    responses = client.simGetImages([
        airsim.ImageRequest(
            # "0", airsim.ImageType.DepthPerspective, True, False)
            "0", airsim.ImageType.DepthPlanar, True)
    ])
    response = responses[0]
    print(np.array(response.image_data_float).max())
    print(np.array(response.image_data_float).min())
    print(np.array(response.image_data_float).shape)
    return np.array(response.image_data_float).min(), np.array(response.image_data_float).max()


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
        os.system("powershell rm -r test_miv/GT")
        os.system("powershell rm test_miv/output/*")
        sys.exit()
    elif(argv[1] == "GT"):
        cameras_pose = import_cameras_pose(argv[2])
        num_frames = len(cameras_pose)
        return cameras_pose, num_frames
    else:
        # input camera postion and rotation from .csv
        cameras_pose = import_cameras_pose(argv[1])
        num_frames = int(argv[2])
        return cameras_pose, num_frames


def main():
    cameras_pose, num_frames = arg_parser()
    zmin = 99999999999.0
    zmax = 0.0
    # connect to airsim
    print(msgpackrpc.__version__)
    client = airsim.MultirotorClient()
    client.confirmConnection()
    for camera_pose in cameras_pose:
        set_camera_pose(client, camera_pose)
        lzmin, lzmax = get_zmin_zmax(client)
        if (zmin > lzmin):
            zmin = lzmin
        if (zmax < lzmax):
            zmax = lzmax
    print(zmin, zmax)
    # capture RGBD from various camera pose in Airsim
    for camera_pose in cameras_pose:
        set_camera_pose(client, camera_pose)
        os.system(f"powershell mkdir test_miv/{camera_pose.name}")
        responses = request_video_from_airsim(client)
        save_videos_from_responses(responses, camera_pose, zmin, zmax)

        duplicate_yuv(camera_pose, num_frames)
    # Generate camera parameter JSON file
    gernerate_camera_para_json(cameras_pose, num_frames, zmin, zmax)


def render_GT():
    cameras_pose, num_frames = arg_parser()
    print(msgpackrpc.__version__)
    client = airsim.MultirotorClient()
    client.confirmConnection()
    os.system(f"powershell mkdir test_miv/GT")
    for f_idx, camera_pose in enumerate(cameras_pose):
        set_camera_pose(client, camera_pose)
        responses = client.simGetImages([
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
        ])  # scene vision image in uncompressed RGB array
        filename = f"test_miv/GT/{f_idx}"
        for response in responses:
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
        os.system(
            f"type test_miv\GT\{f_idx}.yuv >> test_miv\GT\GT_texture_480x270_yuv420p10le.yuv")


if __name__ == "__main__":
    main()
