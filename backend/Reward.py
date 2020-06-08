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
    def __init__(self.env):
        self.env = env
        self.reward_range = {100,-100}

    def calc(self):
        if self.gps_actual == self.gps_target:
            reward = 100
        else:
            #distance reward
            dist_max = np.sqrt(2)*self.com.N
            dist_penalty = self.get_target_distance()
            dist_reward = -(dist_penalty/dist_max)**0.4

            #obstacle punishment
            radius = 3
            #if the target is too near to an obstacle
            if self.get_target_distance() < radius:
                obstacle_reward = 0
            else:
                obst_dist = np.min(self.env.distance_sensor()[1])
                if obst_dist < radius:
                    obstacle_reward = 1-(dist_penalty/radius)**0.4
                else:
                    obstacle_reward = 0
            

            reward = dist_max*(dist_reward - obstacle_reward)
            #crash
            if self.env.state_object.touching:
                reward = reward - 100

        return reward


class Reward3(Reward):
    def __init__(self, env):
        super(Reward2, self).__init__(env)
        self.reward_range = (-100, 100)
    

    def calc(self):
        if self.gps_actual == self.gps_target:
            reward = 100
        else:
            #distance reward
            dist_max = np.sqrt(2)*self.com.N
            dist_penalty = self.get_target_distance()
            dist_reward = - (dist_penalty/dist_max)**0.4

            #obstacle punishment
            radius = 3
            #if the target is too near to an obstacle
            if self.get_target_distance() < radius:
                obstacle_reward = 0
            else:
                obst_dist = np.min(self.env.distance_sensor()[1])
                radius = 3
                if obst_dist < radius:
                    obstacle_reward = 1-(dist_penalty/radius)**0.4
                else:
                    obstacle_reward = 0

            #reward to help round the huge obstacle
            factor = 0.1
            anchor = self.env.distance_sensor()[0]
            diff = np.diff(self.env.distance_sensor()[1])
            dist_anchor = utils.euklidian_distance(self.gps_actual,anchor[np.argmax(diff)])
            diff_reward = - factor * (dist_anchor/dist_max)**0.4

            reward = dist_max*(dist_reward - obstacle_reward + diff_reward)
            #crash
            if self.env.state_object.touching:
                reward = reward - 100

        return reward


