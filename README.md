# Airsim_recoder

## Pre-requirement
- Airsim (https://github.com/microsoft/AirSim/tree/v1.5.0-linux)
- AirSim APIs (Python) (https://microsoft.github.io/AirSim/apis/)
- Creating and Setting Up Unreal Environment for Airsim (https://microsoft.github.io/AirSim/unreal_custenv/)
- ffmpeg
- python3
    - cv2
    - numpy
    - matplotlib
    - pandas
## Usage
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
- convert user trace from airsim coordinate to MIV coordinate
    ```
    python {input_pose_trace_path} {output_pose_trace_path}
    ```


