from webotsgym.config import WbtConfig

from webotsgym.env.reward.steppenalty import step_pen_04, step_pen_exp


class WbtReward():
    def __init__(self, env, config: WbtConfig = WbtConfig()):
        self.env = env
        self.config = config


class WbtRewardGrid(WbtReward):
    def __init__(self, env, config, max_time_steps=1000,
                 max_neg_reward=-1000, targetband=0.05):
        super(WbtRewardGrid, self).__init__(env, config)
        self.targetband = targetband

        def calc_reward(self):
            if self.env.get_target_distance() < self.targetband:
                reward = 10000
            else:
                reward = 0

                # step penalty
                target_distance = self.env.get_target_distance(normalized=True)
                reward += step_pen_exp(target_distance, lambda_=5)

                # visited count penalty


                distance = self.env.get_target_distance() + epsilon
                cost_distance = (distance**0.4) / (distance)
                reward_factor = -1
                reward = reward_factor * (cost_step * cost_distance)
                if self.env.state:
                    reward = reward - 10
            return reward

        def check_done(self):
            if self.com.time_steps == 1000:
                return True
            if self.total_reward < -1000:
                return True
            if self.gps_actual == self.gps_target:
                return True
            return False
