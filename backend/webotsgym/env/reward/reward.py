from webotsgym.config import WbtConfig
from webotsgym.env.reward.steppenalty import step_pen_exp
import webotsgym.utils as utils


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
        if self.env.steps_in_run % 2500 == 0:
            return True
        return False


class WbtRewardGrid(WbtReward):
    def __init__(self, env, config, targetband=0.05):
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
        if self.env.steps_in_run == 200:
            return True
        if self.env.total_reward < -1000:
            return True
        if self.env.get_target_distance() < self.targetband:
            return True
        return False


class WbtRewardContinuousV1(WbtReward):
    def __init__(self, env, config):
        super(WbtRewardContinuousV1, self).__init__(env, config)

    def calc_reward(self):
        target_distance = self.env.get_target_distance(False)
        if target_distance < 0.1:
            return 500 + 500 * (1 - abs(self.env.state.speed))
        else:
            reward = 0
            if self.env.steps_in_run > 1:
                reward += -1

                # get distance moved towards target in last step
                move_to_goal = self.env.distances[-2] - self.env.distances[-1]

                # calculate total distance moved in last step
                gps_current = self.env.history[-1].gps_actual
                gps_last = self.env.history[-2].gps_actual
                move_total = utils.euklidian_distance(gps_current, gps_last)

                # how much of our move got us closer to the goal
                move_diff_ratio = move_to_goal / move_total

                # compared to the start, how close are we to the goal
                diff_initial = self.env.distances[0]
                diff_ratio = abs(move_to_goal / diff_initial)

                # get closer, get reward. Move away, negative penalty.
                if move_total > 0:
                    diff_rew = 500 * diff_ratio * move_diff_ratio
                else:
                    diff_rew = 0

                reward += diff_rew

            if self.env.state.action_denied:
                reward += -1

            if self.env.state.touching:
                reward += -20
        return reward

    def check_done(self):
        if self.env.total_reward < -1000:
            return True

        if self.env.steps_in_run > 500:
            return True

        if self.env.get_target_distance(False) < 0.1:
            return True

        if self.env.total_reward > 2000:
            return True

        return False
