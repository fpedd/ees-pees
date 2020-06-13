import numpy as np
import abc

from webotsgym.config import WebotConfig


class Evaluate(object):
    def __init__(self, env, config: WebotConfig = WebotConfig()):
        self.env = env
        self.config = config
        self.reward_range = (-100, 100)

    @abc.abstractmethod
    def calc_reward(self):
        pass

    @abc.abstractmethod
    def check_done(self):
        pass


class EvaluateMats(Evaluate):
    def __init__(self, env, config: WebotConfig = WebotConfig()):
        super(EvaluateMats, self).__init__(env, config)
        self.reward_range = (-2000, 2000)

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
            distance = self.env.get_target_distance() + epsilon
            cost_distance = (distance**0.4) / (distance)
            reward_factor = -1
            reward = reward_factor * (cost_step * cost_distance)
            if self.env.state:
                reward = reward - 10
        return reward

    def check_done(self):
        if self.env.iterations % self.config.reset_env_after == 0:
            return True
        if self.env.get_target_distance() < 0.1:
            return True
        return False


class EvaluatePJ0(Evaluate):
    def __init__(self, env, config: WebotConfig = WebotConfig()):
        super(EvaluatePJ0, self).__init__(env, config)
        self.reward_range = (-100, 100)

    def calc_reward(self):
        if self.env.get_target_distance() < 0.1:
            return self.reward_range[1]
        else:
            dist = self.env.get_target_distance()
            denom = self.env.max_distance / 2
            return -1 * np.tanh(dist / denom)

    def check_done(self):
        if self.env.iterations % self.config.reset_env_after == 0:
            return True
        if self.env.get_target_distance() < 0.1:
            return True
        return False
