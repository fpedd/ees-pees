import numpy as np
import matplotlib.pyplot as plt


def plot_lidar(x):
    """Plot lidar data."""
    x = np.flip(x)
    theta = np.linspace(0, 2 * np.pi, len(x), endpoint=False)
    ax = plt.subplot(111, projection='polar')
    bars = ax.bar(theta + np.pi / 2, x,
                  width=2 * np.pi / len(x),
                  bottom=0.0)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    for r, bar in zip(x, bars):
        bar.set_facecolor(plt.cm.winter(r / len(x)))
        bar.set_alpha(0.5)
    plt.show()
