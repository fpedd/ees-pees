import numpy as np


def euklidian_distance(source, target):
    """Calculate the euklidian distance from two points.

    Parameter:
    ---------
    source : float
        point/location in the webots world

    target : float
        point/location in the webots world

    Return:
    -------
    float
        euclidian distance between source and target location

    """
    xs, ys = source
    xt, yt = target
    dx = xt - xs
    dy = yt - ys
    return np.sqrt(dx**2 + dy**2)


def exponential_decay(x, N0=1, lambda_=5):
    """Return exponential decay of x with lambda and base N0.

    Parameter:
    ---------
    x : float
        number for which exponential decay is calculated

    lambda_ : integer
        factor in the exponential function with default 5

    NO : integer
        base for the exponential function with default 1

    Return:
    -------
    float
        calculated exponential decay for x

    """
    return N0 * np.exp(-lambda_ * x)


def add_tuples(t1, t2):
    """Add two tuples with each other.

    Parameter:
    ---------
    t1 : tuple
        first tuple

    t2 : tuple
        second tuple

    Return:
    -------
    tuple
        calculated tuple

    """
    arr1 = np.array(t1)
    arr2 = np.array(t2)
    arr = arr1 + arr2
    return tuple(arr)


def id_in_range(low, high, num_of_actions, value):
    """Find index of value between low and high.

    Parameter:
    ---------
    low : integer
        lower boundary for finding the index

    high : integer
        higher boundary for finding the index

    num_of_actions : integer
        number of action for which we want to find id in range

    value : integer
        the actual value

    Return:
    -------
    integer
        index found for value between the boundaries

    """
    bins = np.linspace(low, high, num_of_actions + 1)
    return np.digitize(value, bins) - 1
