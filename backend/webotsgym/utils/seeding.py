import numpy as np
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
