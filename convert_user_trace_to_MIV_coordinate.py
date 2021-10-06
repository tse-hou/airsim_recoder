import pandas as pd


class Camera_pose:
    def __init__(self):
        self.name = ""
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]


def convert_airsim_coordinate_to_MIV_coordinate(airsim_camera_pose):
    MIV_camera_pose = Camera_pose()
    MIV_camera_pose.position = [
        airsim_camera_pose.position[0], -airsim_camera_pose.position[1], -airsim_camera_pose.position[2]]
    MIV_camera_pose.rotation = [
        -airsim_camera_pose.rotation[2], -airsim_camera_pose.rotation[1], airsim_camera_pose.rotation[0]]
    return MIV_camera_pose


df = pd.read_csv("pose.csv")
df['y'] = -df['y']
df['z'] = -df['z']
df['yaw'] = -df['yaw']
df['pitch'] = -df['pitch']
df = df.drop(columns=['t', 'valid'])

new_df = pd.DataFrame(data={'X': df['x'].values, 'Y': df['y'].values, 'Z': df['z'].values,
                            'Yaw': df['yaw'].values, 'Pitch': df['pitch'].values, 'Roll': df['roll'].values})
new_df.to_csv("converted_pose.csv", index=False)
