import math
from matplotlib import colors
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# edit


def Normalize(data, center):
    return data[1]-center[0], data[2]-center[1], data[3]-center[2]

# yaw, row, pitch to vector


def YRPtoVectorDir(yaw, pitch, row):
    x_dir = math.cos(yaw)*math.cos(pitch)
    y_dir = math.sin(yaw)*math.cos(pitch)
    z_dir = math.sin(pitch)
    return x_dir, y_dir, z_dir

# u: usr
# c: camera


def Rotate(u_data, c_data):
    c_xyz = np.array([[c_data[1]],
                      [c_data[2]],
                      [c_data[3]]])
    u_y, u_p, u_r = u_data[4]*math.pi/180, u_data[5] * \
        math.pi/180, u_data[6]*math.pi/180

    # roll rotate x, pitch rotate y, yaw rotate z
    yaw_mat = np.array([[math.cos(u_y), -(math.sin(u_y)), 0],
                        [math.sin(u_y), math.cos(u_y), 0],
                        [0, 0, 1]])

    new_xyz = np.dot(yaw_mat, c_xyz)

    new_y = c_data[4] + u_data[4]
    new_p = c_data[5] + u_data[5]
    new_r = c_data[6] + u_data[6]

    return round(new_xyz[0][0], 2), round(new_xyz[1][0], 2), round(new_xyz[2][0], 2), round(new_y, 2), round(new_p, 2), round(new_r, 2)


def Move(u_data, c_data):
    return float(c_data[1])+u_data[1], float(c_data[2])+u_data[2], float(c_data[3])+u_data[3]


# camera_center = ['usr', 0.9, 0.8, 1.2, 180, 0, 0]
# file_name = 'TMIV_camera_position/6x6_camera_array.csv'
# output_name = 'TMIV_camera_position/6x6_camera_array_XoioBerlinFlat.csv'

def main(camera_center, file_name, output_name):
    # read data
    df = pd.read_csv(file_name)
    # values in pandas module will automatic change array into numpy array
    datas = df.values

    tmp_center = [float(datas[0][1]), float(datas[0][2]), float(datas[0][3])]

    for data in datas:
        data[1], data[2], data[3] = Normalize(data, tmp_center)

    for data in datas:
        # rotate
        data[1], data[2], data[3], data[4], data[5], data[6] = Rotate(
            camera_center, data)
        # move
        data[1], data[2], data[3] = Move(camera_center, data)

    # write csv
    pd.DataFrame(datas[1:]).to_csv(output_name, index=False,
                                   float_format='{:f}'.format, header=False, encoding='utf-8')

    for data in datas:
        # [name, x, y, z, y, r, p] to [name, x, y, z, x_dir, y_dir, z_dir]
        data[4], data[5], data[6] = YRPtoVectorDir(float(
            data[4])*math.pi/180, float(data[5])*math.pi/180, float(data[6])*math.pi/180)

    center = [float(datas[0][1]), float(datas[0][2]), float(datas[0][3])]
    datas = np.delete(datas, 0, 0)
    nums_datas = np.shape(datas)[0]

    x = []
    y = []
    z = []
    x_dir = []
    y_dir = []
    z_dir = []

    for data in datas:
        x.append(float(data[1]))
        y.append(float(data[2]))
        z.append(float(data[3]))
        x_dir.append(float(data[4]))
        y_dir.append(float(data[5]))
        z_dir.append(float(data[6]))

    # plot
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    cols = ['r', 'g', 'b']

    # center point
    ax.scatter(center[0], center[1], center[2], c="red")
    # cameras
    quivers = ax.quiver(x, y, z, x_dir, y_dir, z_dir)

    # UI
    ax.set_xlim3d([-5.0, 5.0])
    ax.set_xlabel('X')

    ax.set_ylim3d([-5.0, 5.0])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-5.0, 5.0])
    ax.set_zlabel('Z')

    # plt.show()
