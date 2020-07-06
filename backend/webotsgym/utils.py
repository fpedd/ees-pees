import numpy as np
import matplotlib.pyplot as plt
import pickle
import time


def set_random_seed(apply=False):
    """Use current time to set seed to something random."""
    t = 1000 * time.time()
    seed = int(t) % 2**16
    if apply is True:
        np.random.seed(seed)
    else:
        return seed


def seed_list(seed, n=100, low=0, high=10**6):
    """Create a list of n seeds."""
    np.random.seed(seed)
    seeds = list(set(np.random.randint(low, high, n)))
    return seeds


# =========================================================================
# ==========================      SAVE/LOAD       =========================
# =========================================================================
def save_object(obj, path):
    """Save object via pickle."""
    filehandler = open(path, 'wb')
    pickle.dump(obj, filehandler)


def load_object(path):
    """Load object via pickle."""
    filehandler = open(path, 'rb')
    return (pickle.load(filehandler))


# =========================================================================
# ==========================      PLOTTING        =========================
# =========================================================================
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


# =========================================================================
# ==========================         MISC         =========================
# =========================================================================
def euklidian_distance(source, target):
    xs, ys = source
    xt, yt = target
    dx = xt - xs
    dy = yt - ys
    return np.sqrt(dx**2 + dy**2)


def add_tuples(t1, t2):
    arr1 = np.array(t1)
    arr2 = np.array(t2)
    arr = arr1 + arr2
    return tuple(arr)


# =========================================================================
# ==========================   FAKE ENVIRONMENT   =========================
# =========================================================================
def id_in_range(low, high, num_of_actions, value):
    """Find index of value between low and high."""
    bins = np.linspace(low, high, num_of_actions + 1)
    return np.digitize(value, bins) - 1