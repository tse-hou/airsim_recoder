# %%
import math
from numpy import RankWarning
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.proj3d import proj_transform
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib.text import Annotation


class Annotation3D(Annotation):

    def __init__(self, text, xyz, *args, **kwargs):
        super().__init__(text, xy=(0, 0), *args, **kwargs)
        self._xyz = xyz

    def draw(self, renderer):
        x2, y2, z2 = proj_transform(*self._xyz, self.axes.M)
        self.xy = (x2, y2)
        super().draw(renderer)


def _annotate3D(ax, text, xyz, *args, **kwargs):
    '''Add anotation `text` to an `Axes3d` instance.'''

    annotation = Annotation3D(text, xyz, *args, **kwargs)
    ax.add_artist(annotation)


setattr(Axes3D, 'annotate3D', _annotate3D)
pi = math.pi


def cal_yaw_pitch(x, y, z):
    # print(math.dist([x, y], [0, 0]))
    # yaw = math.degrees(math.asin(y/math.dist([x, y], [0, 0])))
    yaw = math.asin(y/math.dist([x, y], [0, 0]))
    # if(x < 0 and y > 0):
    #     yaw = 180 - yaw
    # elif(x < 0 and y < 0):
    #     yaw = -180 - yaw
    return yaw


def PointsInCircum(center_circle, r, n=100):
    x = [math.cos(2 * pi / n * i) * r + center_circle[0]
         for i in range(n + 1)]
    y = [math.sin(2 * pi / n * j) * r + center_circle[1]
         for j in range(n + 1)]
    z = [-1] * (n + 1)
    yaw_radian = math.asin(y[1]/math.dist([x[1], y[1]], [0, 0]))
    Yaw = [0.0]
    for k in range(1, n+1):
        Yaw.append(yaw_radian*k)
    Pitch = []
    Pitch = [0] * (n + 1)
    Roll = [0] * (n + 1)
    df = pd.DataFrame(data={"x": x[0:-1], "y": y[0:-1], "z": z[0:-1],
                      "Yaw": Yaw[0:-1], "Pitch": Pitch[0:-1], "Roll": Roll[0:-1]})
    return df


def label_point(x, y, z, val, Yaw, Pitch, Roll, ax):

    a = pd.concat({'x': x, 'y': y, 'z': z, 'Yaw': Yaw,
                  'Pitch': Pitch, 'Roll': Roll, 'val': val}, axis=1)
    for i, point in a.iterrows():
        # x = math.cos(point['Yaw'])*math.cos(point['Pitch'])
        # y = math.sin(point['Yaw'])*math.cos(point['Pitch'])
        # z = math.sin(point['Pitch'])
        # ax.annotate3D('', (point['x'], y, z),
        #               bbox=dict(boxstyle="round", fc="lightyellow"),
        #               arrowprops=dict(arrowstyle="-|>", ec='black', fc='white', lw=5))
        ax.text(point['x'], point['y'], point['z'], str(point['val']))


def produce_test_dataset_30views():
    point_df_list = []
    point_df_list.append(PointsInCircum((0.0, 0.0), 1, n=16))
    point_df_list.append(PointsInCircum((0.0, 0.0), 0.7, n=12))
    point_df_list.append(PointsInCircum((0.0, 0.0), 0.4, n=6))
    PC_df = pd.concat(point_df_list)
    views_name = []
    for i in range(PC_df.shape[0]):
        views_name.append(f"v{i}")
    PC_df["views_name"] = views_name
    # 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(PC_df["x"], PC_df["y"], PC_df["z"], marker="o")
    label_point(PC_df.x, PC_df.y, PC_df.z, PC_df.views_name,
                PC_df.Yaw, PC_df.Pitch, PC_df.Roll, ax)
    plt.show()
    # 2D scatter plot
    # fig = plt.figure()
    # ax = fig.add_subplot()
    # ax.scatter(PC_df["x"], PC_df["y"], marker="o")

    # label_point_arrow(PC_df["x"], PC_df["y"], PC_df["Yaw"],
    #                   PC_df["Pitch"], PC_df.views_name, ax)
    # plt.show()
    PC_df.to_csv("tmp.csv", index=False, header=False, columns=[
                 "views_name", "x", "y", "z", "Yaw", "Pitch", "Roll"])


def produce_test_dataset_planar_25views():
    pose_dict = {'views_name': [], 'x': [], 'y': [], 'z': [],
                 'yaw': [0]*25, 'pitch': [0]*25, 'roll': [0]*25}
    for i in range(5):
        for j in range(5):
            view_name = f"v{i*5+j}"
            pos = [0, -0.4+j*0.2, 1.4-i*0.2]
            pose_dict['views_name'].append(view_name)
            pose_dict['x'].append(pos[0])
            pose_dict['y'].append(pos[1])
            pose_dict['z'].append(pos[2])
    df = pd.DataFrame(data=pose_dict)
    df.to_csv("tmp.csv", index=False, header=False, columns=[
        "views_name", "x", "y", "z", "yaw", "pitch", "roll"])
    # 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(df["x"], df["y"], df["z"], marker="o")
    label_point(df.x, df.y, df.z, df.views_name,
                df.yaw, df.pitch, df.roll, ax)
    plt.show()


def produce_test_dataset_planar_25views_closer():
    pose_dict = {'views_name': [], 'x': [], 'y': [], 'z': [],
                 'yaw': [0]*25, 'pitch': [0]*25, 'roll': [0]*25}
    for i in range(5):
        for j in range(5):
            view_name = f"v{i*5+j}"
            pos = [0, -0.2+j*0.1, 1.2-i*0.1]
            pose_dict['views_name'].append(view_name)
            pose_dict['x'].append(pos[0])
            pose_dict['y'].append(pos[1])
            pose_dict['z'].append(pos[2])
    df = pd.DataFrame(data=pose_dict)
    df.to_csv("tmp.csv", index=False, header=False, columns=[
        "views_name", "x", "y", "z", "yaw", "pitch", "roll"])
    # 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(df["x"], df["y"], df["z"], marker="o")
    label_point(df.x, df.y, df.z, df.views_name,
                df.yaw, df.pitch, df.roll, ax)
    plt.show()


def produce_simple_test_dataset():
    pose_dict = {'views_name': [], 'x': [0]*2, 'y': [], 'z': [0.6]*2,
                 'yaw': [0]*2, 'pitch': [0]*2, 'roll': [0]*2}
    pose_dict['views_name'].append('v1')
    pose_dict['y'].append(0.5)
    pose_dict['views_name'].append('v2')
    pose_dict['y'].append(-0.5)
    df = pd.DataFrame(data=pose_dict)
    df.to_csv("tmp.csv", index=False, header=False, columns=[
        "views_name", "x", "y", "z", "yaw", "pitch", "roll"])
    # 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(df["x"], df["y"], df["z"], marker="o")
    label_point(df.x, df.y, df.z, df.views_name,
                df.yaw, df.pitch, df.roll, ax)
    plt.show()


def produce_test_dataset_planar_25views_closer_shpere_scene():
    pose_dict = {'views_name': [], 'x': [], 'y': [], 'z': [],
                 'yaw': [0]*25, 'pitch': [0]*25, 'roll': [0]*25}
    for i in range(5):
        for j in range(5):
            view_name = f"v{i*5+j}"
            pos = [0, -0.2+j*0.1, 1.2-i*0.1]
            pose_dict['views_name'].append(view_name)
            pose_dict['x'].append(pos[0])
            pose_dict['y'].append(pos[1])
            pose_dict['z'].append(pos[2])
    df = pd.DataFrame(data=pose_dict)
    df.to_csv("tmp.csv", index=False, header=False, columns=[
        "views_name", "x", "y", "z", "yaw", "pitch", "roll"])
    # 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(df["x"], df["y"], df["z"], marker="o")
    label_point(df.x, df.y, df.z, df.views_name,
                df.yaw, df.pitch, df.roll, ax)
    plt.show()


if __name__ == "__main__":
    produce_test_dataset_planar_25views_closer_shpere_scene()
    # print(cal_yaw_pitch(-3, -4, 0))
