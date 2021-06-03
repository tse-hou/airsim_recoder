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
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(df["x"], df["y"], df["z"], marker="o")
    plt.show()
    return df


if __name__ == "__main__":
    PC_df = PointsInCircum((0.0, 0.0), 1.0, n=10)
    PC_df.to_csv("tmp.csv", index=False)


# %%
