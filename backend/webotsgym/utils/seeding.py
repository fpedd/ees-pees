import time
import numpy as np


def set_random_seed(apply=False):
    """Use current time to set seed to something random.

    Parameter:
    ---------
    apply : boolean
        Boolean to randomize created seed
        Default : False -> seed doesn't get randomized

    Return:
    -------
    integer
        created seed (randomized or not depending on apply)

    """
    t = 1000 * time.time()
    seed = int(t) % 2**16
    if apply is True:
        np.random.seed(seed)
    return seed


def seed_list(seed, n=100, low=0, high=10**6):
    """Create a list of n seeds."""
    np.random.seed(seed)
    seeds = list(set(np.random.randint(low, high, n)))
    return seeds
