#%%
import os
import airsim
import msgpackrpc
import numpy as np
import csv
import cv2
import argparse
from sys import argv


def input_trajectory(filename):
    csv_data = []
    with open(filename, "r") as csv_f:
        rows = csv.reader(csv_f)
        for idx, row in enumerate(rows):
            if idx == 0:
                continue
            row = [float(x) for x in row]
            csv_data.append(row)
    return csv_data


def parse_arugment():
    parser = argparse.ArgumentParser(description="render image from airsim")
    parser.add_argument("trajectory_file", type=str, help="trajectory of rendering path (.csv)")
    parser.add_argument("save_folder_path", type=str, help="folder path for image saving")
    args = parser.parse_args()
    return args


def main(args):
    # argument processing
    trajectory = input_trajectory(args.trajectory_file)
    os.system(f"powershell mkdir {args.save_folder_path}")
    # connect to airsim
    print(msgpackrpc.__version__)
    client = airsim.MultirotorClient()
    client.confirmConnection()
    # captrue image using trajectory
    for idx, pose in enumerate(trajectory):
        client.simSetVehiclePose(
            airsim.Pose(
                airsim.Vector3r(pose[0], pose[1], pose[2]),
                airsim.to_quaternion(pose[3], pose[4], pose[5]),
            ),
            True,
        )
        response = client.simGetImages(
            [airsim.ImageRequest(0, airsim.ImageType.Scene, False, False)]
        )
        # save image
        image_path = f"{args.save_folder_path}/{argv[1]}_{idx}line.png"
        # png format
        if response[0].compress:
            print(
                f"{image_path}, Type: {response[0].image_type}, Size: {len(response[0].image_data_uint8)}"
            )
            airsim.write_file(image_path, response[0].image_data_uint8)
        # uncompressed array, RGBA format
        else:
            print(
                f"{image_path}, Type: {response[0].image_type}, Size: {len(response[0].image_data_uint8)}"
            )
            # string => int
            img1d = np.fromstring(response[0].image_data_uint8, dtype=np.uint8)
            # reshape array to 4 channel image array H X W X 3 (RGB)
            img_rgb = img1d.reshape(response[0].height, response[0].width, 3)
            # write to png
            cv2.imwrite(image_path, img_rgb)
    print("done")


if __name__ == "__main__":
    args = parse_arugment()
    main(args)
# %%
