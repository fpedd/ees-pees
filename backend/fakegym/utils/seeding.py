import numpy as np
import time


def np_random_seed(set=True):
    """Use current time to set seed to something random."""
    t = 1000 * time.time()
    seed = int(t) % 2**32
    if set is True:
        np.random.seed(seed)
    else:
        return seed


def seed_list(seed, n=100, low=0, high=10**6):
    """Create a list of n seeds."""
    np.random.seed(seed)
    seeds = list(set(np.random.randint(low, high, n)))
    return seeds