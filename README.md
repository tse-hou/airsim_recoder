# Airsim_recoder

## Pre-requirement
- Airsim (https://github.com/microsoft/AirSim/tree/v1.5.0-linux)
- AirSim APIs (Python) (https://microsoft.github.io/AirSim/apis/)
- Creating and Setting Up Unreal Environment for Airsim (https://microsoft.github.io/AirSim/unreal_custenv/)
- python3
    - cv2
    - numpy
    - matplotlib
    - pandas
## Usage
- `setup_path.py`
    - add Airsim module into PATH
    - necessary for running Airsim API
- `recorder_for_MIV.py`
    - Capture source views for MIV:
        ```
        python recorder_for_MIV.py SV {camera_pose_csv} {num_frames}
        ```
    - Capture Ground truth video:
        ```
        python recorder_for_MIV.py GT {user_pose_csv}
        ```
    - Clean output folder:
        ```
        python recorder_for_MIV.py clean
        ```
- `recorder.py`
    - record image according to trajectory
    -
        ```
        python recorder.py [trajectory file] [output image folder]
        ```
- `produce_camera_pose.py` & `produce_user_pose.py`
    - generate trace 


