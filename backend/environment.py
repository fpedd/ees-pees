import numpy as np
import matplotlib.pyplot as plt
import abc
import gym

import fakecom
import utils
from Action import DiscreteFlat4
from Reward import Reward


class MyGym(gym.Env):
    def __init__(self, seed):
        super(MyGym, self).__init__()
        self.seeds = self.set_seed(seed)
        self.reward_range = (-100, 100)

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def step(self):
        pass

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    def set_seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        if seed is None:
            seed = utils.set_random_seed()
        seeds = [seed]
        np.random.seed(seed)
        # TODO: utils.seed_list(seed)
        seeds.extend(utils.seed_list(seed, n=1000))
        return seeds

    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])


class WebotsBlue(MyGym):
    def __init__(self, seed, action, reward, observation):
        super(WebotsBlue, self).__init__(seed=seed)
        self.action = action
        self.reward = reward
        self.observation = observation

    def _init_act_rew_obs(self, env):
        # init if types
        if type(self.action) == type:
            self.action.__init__(self.action, env)
        if type(self.reward) == type:
            self.reward.__init__(self.reward, env)
        if type(self.observation) == type:
            self.observation.__init__(self.observation, env)

        # init with environment
        self.action._init(env)
        self.action_space = self.action.action_space

    def reset(self):
        self.com.reset()
        return self.state

    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        action = self.action_mapping(action)
        self.com.send(action)
        self.com.recv()
        reward = self.calc_reward()
        done = self.check_done()
        return self.state, reward, done, {}

    def close(self):
        pass

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    def calc_reward(self):
        return np.random.random()

    def check_done(self):
        if self.gps_actual == self.gps_target:
            return True
        return False

    @property
    def state(self):
        return self.com.state.get()

    @property
    def state_object(self):
        return self.com.state

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def gps_target(self):
        return self.com.state.gps_target


# class WebotsEnv(WebotsBlue):
#     def __init__(self, seed):
#         super(WebotsEnv, self).__init__(seed=seed)
#         self.com = communicate.Com(self.seeds)
#
#     def reset(self):
#         #  reset_environment in automate, wait and then grab ext ctrl info
#         pass


class WebotsFake(WebotsBlue):
    def __init__(self, seed, N, num_of_sensors, obstacles_each, action, reward,
                 observation):
        super(WebotsFake, self).__init__(seed=seed,
                                         action=action,
                                         reward=reward,
                                         observation=observation)
        self.com = fakecom.FakeCom(self.seeds, N, num_of_sensors, obstacles_each)
    #     self.num_of_sensors = num_of_sensors
    #
    #
    #
    #     # set observation and action space
    #     self.plotpadding = 1
    #
    # def reset(self):
    #     self.com.reset()
    #     return self.state

    def render(self):
        plt.figure(figsize=(10, 10))
        f = self.com.field.copy()
        rx, ry = self.gps_actual
        tx, ty = self.gps_target
        s = self.plotpadding
        r_minx = max(0, (rx - s))
        r_maxx = min(rx + s + 1, self.com.N)
        r_miny = max(0, (ry - s))
        r_maxy = min(ry + s + 1, self.com.N)

        t_minx = max(0, (tx - s))
        t_maxx = min(tx + s + 1, self.com.N)
        t_miny = max(0, (ty - s))
        t_maxy = min(ty + s + 1, self.com.N)

        f[t_minx:t_maxx, t_miny:t_maxy] = 4
        f[r_minx:r_maxx, r_miny:r_maxy] = 6
        plt.matshow(f)

    # @property
    # def field(self):
    #     return self.com.field


class WebotsFakeMini(WebotsFake):
    def __init__(self, N=10, num_of_sensors=4, obstacles_each=2, seed=None,
                 action=DiscreteFlat4):
        super(WebotsFakeMini, self).__init__(seed=seed,
                                             N=N,
                                             num_of_sensors=num_of_sensors,
                                             obstacles_each=obstacles_each,
                                             action=action,
                                             reward=Reward,
                                             observation=None)
        self.plotpadding = 0
        self.act_tpl = (4, 1)



# class WebotsFakeMedium(WebotsFake):
#     def __init__(self, N=40, num_of_sensors=8, obstacles_each=3, seed=None,
#                  step_range=(1, 8), action_type="discrete",
#                  discrete_action_shaping="flatten"):
#         super(WebotsFakeMedium, self).__init__(seed, N, num_of_sensors,
#                                                obstacles_each, step_range,
#                                                action_type, discrete_action_shaping)
#         self.plotpadding = 0
#
#
# class WebotsFakeLarge(WebotsFake):
#     def __init__(self, N=500, num_of_sensors=16, obstacles_each=20, seed=None,
#                  step_range=(1, 50), action_type="discrete",
#                  discrete_action_shaping="flatten"):
#         super(WebotsFakeLarge, self).__init__(seed, N, num_of_sensors,
#                                               obstacles_each, step_range,
#                                               action_type, discrete_action_shaping)
#         self.plotpadding = 4
#
#
# class DQNEnv(WebotsFakeMini):
#     def __init__(self, seed=None):
#         super(DQNEnv, self).__init__(seed=seed)
#
#     def fields_around(self, radius):
#         n_f = radius * 2 + 1
#         fields = np.zeros(shape=(n_f, n_f))
#         pos = self.gps_actual
#         x = 0
#         y = 0
#         d = (0, 0)
#         for i in range(-radius, radius + 1):
#             y = 0
#             for j in range(-radius, radius + 1):
#                 d = (i, j)
#                 pt = tuple(map(lambda i, j: i + j, pos, d))
#                 if pt == pos:
#                     fields[x][y] = -1
#                 elif self.field[pt[0]][pt[1]] > 0:
#                     fields[x][y] = 1
#                 y += 1
#             x += 1
#
#         return fields
#
#     def step_f(self, action, radius):
#         done = False
#         crash = False
#         o_pos = self.gps_actual
#         direction, len_ = action
#         adj = (0, 0)
#         if direction == 1:
#             adj = (-1, 0)
#         elif direction == 2:
#             adj = (0, 1)
#         elif direction == 3:
#             adj = (1, 0)
#         elif direction == 4:
#             adj = (0, -1)
#         n_p = tuple(map(lambda i, j: i + j, o_pos, adj))
#         if self.field[n_p[0], n_p[1]] > 0:
#             crash = True
#         else:
#             self.com.state.gps_actual = n_p
#         if self.gps_actual == self.gps_target:
#             done = True
#         n_pos = self.gps_actual
#         state = (self.gps_actual, self.fields_around(radius))
#         reward = self.calc_reward(crash, done, o_pos, n_pos)
#         return state, reward, done, {}
#
#     def dist_reward(self, o_pos, n_pos):
#         d_reward = 0
#         t_pos = self.gps_target
#         dx_old = abs(o_pos[0] - t_pos[0])
#         dx_new = abs(n_pos[0] - t_pos[0])
#         dy_old = abs(o_pos[1] - t_pos[1])
#         dy_new = abs(n_pos[1] - t_pos[1])
#
#         if dx_old > dx_new:
#             d_reward = 20
#         if dx_old < dx_new:
#             d_reward = -20
#         if dy_old > dy_new:
#             d_reward = 20
#         if dy_old < dy_new:
#             d_reward = -20
#
#         return d_reward
#
#     def calc_reward(self, crash, done, o_pos, n_pos):
#         reward = 0
#         if done is True:
#             reward = reward + 1000
#         if crash is True:
#             reward = reward - 100
#         reward = reward + self.dist_reward(o_pos, n_pos)
#         reward = reward - 10
#         return reward
#
#     def plot(self):
#         self.render()
