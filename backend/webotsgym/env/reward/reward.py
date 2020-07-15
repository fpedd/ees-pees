from webotsgym.config import WbtConfig

from webotsgym.env.reward.steppenalty import step_pen_exp


class WbtReward():
    def __init__(self, env, config: WbtConfig = WbtConfig()):
        self.env = env
        self.config = config
        self.targetband = 0.05

    def calc_reward(self):
        if self.env.get_target_distance() < self.targetband:
            reward = 10000
        else:
            reward = -1
        return reward

    def check_done(self):
        if self.env.get_target_distance() < self.targetband:
            return True
        if self.env.steps_in_run % 100000 == 0:
            return True
        return False


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
            reward += step_pen_exp(target_distance, step_penalty=-1,
                                   lambda_=5)

            # visited count penalty
            vc = self.env.gps_visited_count
            if vc > 3:
                reward += -0.2 * (vc - 2)**2

            # touching penalty
            if self.env.state.touching is True:
                reward -= 500

        return reward

    def check_done(self):
        if self.env.time_steps == 200:
            return True
        if self.env.total_reward < -1000:
            return True
        if self.env.get_target_distance() < self.targetband:
            return True
        return False
