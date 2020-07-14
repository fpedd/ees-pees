import numpy as np


def id_in_range(low, high, num_of_actions, value):
    """Find index of value between low and high."""
    bins = np.linspace(low, high, num_of_actions + 1)
    return np.digitize(value, bins) - 1