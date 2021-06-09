import math
import pandas as pd
import matplotlib.pyplot as plt


def test_dataset_30views_exp2_line():
    x = []
    y = [0.0] * 90
    z = [-1.0] * 90
    for i in range(90):
        if (i == 0):
            x.append(-0.9)
            continue
        x.append(-0.9+0.02*i)
    rotation = [0]*90
    df = pd.DataFrame(data={"X": x, "Y": y, "Z": z,
                      "Yaw": rotation, "Pitch": rotation, "Roll": rotation})
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(df["X"], df["Y"], df["Z"], marker="o")
    plt.show()
    df.to_csv("test_dataset_30viewsp01.csv", index=False)


test_dataset_30views_exp2_line()
