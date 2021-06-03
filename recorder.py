# %%
import os
import airsim
import msgpackrpc
import numpy as np
import csv
import cv2
import argparse
import sys
from sys import argv
np.set_printoptions(threshold=sys.maxsize)


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
    parser.add_argument("trajectory_file", type=str,
                        help="trajectory of rendering path (.csv)")
    parser.add_argument("save_folder_path", type=str,
                        help="folder path for image saving")
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

        # get camera images from the car
        responses = client.simGetImages([
            # depth visualization image
            airsim.ImageRequest("0", airsim.ImageType.DepthVis),
            # depth in perspective projection
            airsim.ImageRequest("0", airsim.ImageType.DepthPerspective, True),
            # scene vision image in png format
            airsim.ImageRequest("0", airsim.ImageType.Scene),
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])  # scene vision image in uncompressed RGB array
        print('Retrieved images: %d' % len(responses))

        for response_idx, response in enumerate(responses):
            filename = f"{args.save_folder_path}/{idx}_{response.image_type}_{response_idx}"

            if response.pixels_as_float:
                print("Type %d, size %d" %
                      (response.image_type, len(response.image_data_float)))
                airsim.write_pfm(os.path.normpath(
                    filename + '.pfm'), airsim.get_pfm_array(response))
            elif response.compress:  # png format
                print("Type %d, size %d" %
                      (response.image_type, len(response.image_data_uint8)))
                airsim.write_file(os.path.normpath(
                    filename + '.png'), response.image_data_uint8)
            else:  # uncompressed array
                print("Type %d, size %d" %
                      (response.image_type, len(response.image_data_uint8)))
                img1d = np.fromstring(
                    response.image_data_uint8, dtype=np.uint8)  # get numpy array
                # reshape array to 3 channel image array H X W X 3
                img_rgb = img1d.reshape(response.height, response.width, 3)
                cv2.imwrite(os.path.normpath(filename + '.png'),
                            img_rgb)  # write to png
        # response = client.simGetImages(
        #     [airsim.ImageRequest("0", airsim.ImageType.Scene, False, False),
        #      airsim.ImageRequest("0", airsim.ImageType.DepthVis)]
        # )

        # for image in response:
        #     image_path = f"{args.save_folder_path}/{argv[1]}_{idx}line_{image.image_type}.png"
        #     # png format
        #     if image.compress:
        #         print(
        #             f"{image_path}, Type: {image.image_type}, Size: {len(image.image_data_uint8)}"
        #         )
        #         airsim.write_file(image_path, image.image_data_uint8)
        #         print(np.fromstring(image.image_data_uint8, dtype=np.uint8).shape)
        #     # uncompressed array, RGBA format
        #     else:
        #         print(
        #             f"{image_path}, Type: {image.image_type}, Size: {len(image.image_data_uint8)}"
        #         )
        #         # airsim.write_png(image_path, image.image_data_uint8)
        #         # string => int
        #         img1d = np.fromstring(image.image_data_uint8, dtype=np.uint8)
        #         print(img1d.shape)
        #         # reshape array to 4 channel image array H X W X 3 (RGB)
        #         img_rgb = img1d.reshape(image.height, image.width, 3)
        #         # write to png
        #         airsim.write_png(image_path, img_rgb)
    print("done")


if __name__ == "__main__":
    args = parse_arugment()
    main(args)
# %%
