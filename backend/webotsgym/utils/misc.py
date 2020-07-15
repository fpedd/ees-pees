import numpy as np


def euklidian_distance(source, target):
    """Calculate the euklidian distance from two points."""
    xs, ys = source
    xt, yt = target
    dx = xt - xs
    dy = yt - ys
    return np.sqrt(dx**2 + dy**2)


def exponential_decay(x, N0=1, lambda_=5):
    """Return exponential decay of lambda and base N0."""
    return N0 * np.exp(-lambda_ * x)


def add_tuples(t1, t2):
    """Add two tuples with each other."""
    arr1 = np.array(t1)
    arr2 = np.array(t2)
    arr = arr1 + arr2
    return tuple(arr)


def id_in_range(low, high, num_of_actions, value):
    """Find index of value between low and high."""
    bins = np.linspace(low, high, num_of_actions + 1)
    return np.digitize(value, bins) - 1
