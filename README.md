# Airsim_recoder
input trajectory, and output images
## Pre-requirement
- Airsim
- AirSim APIs (Python)
- python3
    - cv2
    - pandas
    - matplotlib
## Usage
- `recorder.py`
    - record image according to trajectory
    - usage:
        ```
        python recorder.py [trajectory file] [output image folder]
        ```
- `produce_trajectory.py`
    - produce sample trajectory
    - usage:
        ```
        python produce_trajectory.py
        ```
- `setup_path.py`
    - add Airsim module into PATH
    - necessary for running Airsim API

