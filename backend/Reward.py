import numpy as np


class Reward(object):
    def __init__(self, env):
        self.env = env
        self.reward_range = (-100, 100)

    def calc(self):
        """Calculate reward."""
        # calculate base value for reward
        N = self.env.config.world_size
        base_v = np.sqrt(2) * N

        # get distance and crash penalties
        distance_penalty = self.env.get_target_distance()
        crash = self.env.state_object.touching

        val = base_v * (1 - crash) - distance_penalty
        return val * self.reward_range[1] / base_v


class Reward2(Reward):
    def __init__(self, env):
        super(Reward2, self).__init__(env)

    def calc(self):
        """This will overwrite calc function from Reward()."""
        pass
