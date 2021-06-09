# %%
import math
import pandas as pd
import matplotlib.pyplot as plt

pi = math.pi


def PointsInCircum(center_circle, r, n=100):
    x = [math.cos(2 * pi / n * i) * r + center_circle[0]
         for i in range(0, n + 1)]
    y = [math.sin(2 * pi / n * j) * r + center_circle[1]
         for j in range(0, n + 1)]
    z = [-1] * (n + 1)
    x_ro = [0] * (n + 1)
    y_ro = [0] * (n + 1)
    z_ro = [0] * (n + 1)
    df = pd.DataFrame(data={"x": x, "y": y, "z": z,
                      "x_ro": x_ro, "y_ro": y_ro, "z_ro": z_ro})
    # fig = plt.figure()
    # ax = fig.add_subplot(projection="3d")
    # ax.scatter(df["x"], df["y"], df["z"], marker="o")
    # plt.show()
    return df


def label_point(x, y, z, val, ax):
    a = pd.concat({'x': x, 'y': y, 'z': z, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'], point['y'], point['z'], str(point['val']))


def produce_test_dataset_30views():
    point_df_list = []
    point_df_list.append(PointsInCircum((0.0, 0.0), 1, n=9))
    point_df_list.append(PointsInCircum((0.0, 0.0), 0.7, n=9))
    point_df_list.append(PointsInCircum((0.0, 0.0), 0.4, n=9))
    PC_df = pd.concat(point_df_list)
    views_name = []
    for i in range(PC_df.shape[0]):
        views_name.append(f"v{i}")
    PC_df["views_name"] = views_name
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(PC_df["x"], PC_df["y"], PC_df["z"], marker="o")
    label_point(PC_df.x, PC_df.y, PC_df.z, PC_df.views_name, ax)
    plt.show()
    PC_df.to_csv("tmp.csv", index=False, header=False, columns=[
                 "views_name", "x", "y", "z", "x_ro", "y_ro", "z_ro"])


if __name__ == "__main__":
    produce_test_dataset_30views()
