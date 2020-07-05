from webotsgym.config import WbtConfig

from webotsgym.env.reward.steppenalty import step_penalty_04, step_penalty_tanh


class WbtReward():
    def __init__(self, env, config: WbtConfig = WbtConfig()):
        super(WbtReward, self).__init__(env, config)
        # self.reward_range = (-2000, 2000)

    def calc_reward(self):
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
