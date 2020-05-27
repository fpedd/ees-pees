import numpy as np


class Reward(object):
    def __init__(self, env):
        self.env = env
        self.range = (-100, 100)

    def calc(self):
        """Calculate reward."""
        # calculate base value for reward
        N = self.env.config.length
        base_v = np.sqrt(2) * N

        # get distance and crash penalties
        distance_penalty = self.env.get_target_distance()
        crash = self.env.state_object.touching

        val = base_v * (1 - crash) - distance_penalty
        return val * 100 / base_v
