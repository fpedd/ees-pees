import numpy as np


class Evaluate(object):
    def __init__(self, env):
        self.env = env
        self.reward_range = (-100, 100)

    def calc_reward(self):
        """Calculate reward."""
        # calculate base value for reward
        N = self.env.config.world_size
        base_v = np.sqrt(2) * N

        # get distance and crash penalties
        distance_penalty = self.env.get_target_distance()
        crash = self.env.state.touching

        val = base_v * (1 - crash) - distance_penalty
        return val * self.reward_range[1] / base_v

    def check_done(self):
        if self.env.iterations == 10**6:
            return True
        if self.env.get_target_distance() < 0.1:
            return True
        return False


class EvaluateMats(Evaluate):
    def __init__(self, env):
        super(EvaluateMats, self).__init__(env)

    def calc_reward(self):
        """Calculate reward function.

        Idea(Mats):
        - negative reward for normal move so that james moves faster to goal
        - still lower negative reward if james gets closer to goal
        - high positive award for reaching it
        - high negative award to hitting a wall
        - epsilon only to divide never by 0

        """
        if self.env.get_target_distance() < 0.1:
            reward = 1000
        else:
            epsilon = 10**-5
            cost_step = 1
            distance = self.get_target_distance() + epsilon
            cost_distance = (distance**0.4) / (distance)
            reward_factor = -1
            reward = reward_factor * (cost_step * cost_distance)
            if self.state:
                reward = reward - 10
        return reward
