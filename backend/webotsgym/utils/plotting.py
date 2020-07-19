import numpy as np
import matplotlib.pyplot as plt


def plot_lidar(x):
    """Plot lidar data.

    Description:
    -----------
    Plotfunction for the lidar data from the webots env.

    Parameter:
    ----------
    x : array
        lidar data of up to 360 data points

    """
    x = np.flip(x)
    theta = np.linspace(0, 2 * np.pi, len(x), endpoint=False)
    ax = plt.subplot(111, projection='polar')
    bars = ax.bar(theta + np.pi / 2, x,
                  width=2 * np.pi / len(x),
                  bottom=0.0)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    for r, bar_ in zip(x, bars):
        bar_.set_facecolor(plt.cm.winter(r / len(x)))
        bar_.set_alpha(0.5)
    plt.show()
