import numpy as np
import matplotlib.pyplot as plt
import abc
import gym

import utils
import communicate

from Action import DiscreteAction, ContinuousAction
from Reward import Reward
from Observation import observation_std


class MyGym(gym.Env):
    def __init__(self, seed):
        super(MyGym, self).__init__()
        self.seeds = self.set_seed(seed)

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
    def __init__(self, seed, action_class, reward_class, observation_func):
        super(WebotsBlue, self).__init__(seed=seed)
        self.action_class = action_class
        self.reward_class = reward_class
        self.observation_func = observation_func
        self.i = 0
        self.history = {}

    def _update_history(self):
        self.history[self.i] = self.state
        self.i += 1

    def _init_act_rew_obs(self, env):
        # type to instance
        if type(self.action_class) == type:
            self.action_class = (self.action_class)()
        if type(self.reward_class) == type:
            self.reward_class = (self.reward_class)(env)

        self.action_space = self.action_class.action_space
        self.reward_range = self.reward_class.reward_range

    def reset(self):
        self.com.reset()
        # return self.state
        return self.observation

    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        action = self.action_class.map(action, self.state_object)
        self.send(action)
        self.recv()
        reward = self.calc_reward()
        done = self.check_done()

        # return self.state, reward, done, {}
        return self.observation, reward, done, {}

    def send(self, action):
        self.com.send(action)

    def recv(self):
        self.com.recv()
        self._update_history()

    def close(self):
        pass

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    def calc_reward(self):
        return self.reward_class.calc()

    def check_done(self):
        if self.gps_actual == self.gps_target:
            return True
        return False

    @property
    def observation(self):
        return self.observation_func(self)

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


class WebotsEnv(WebotsBlue):
    def __init__(self, seed=None, action_class=DiscreteAction,
                 reward_class=Reward, observation_func=observation_std):
        super(WebotsEnv, self).__init__(seed=seed,
                                        action_class=action_class,
                                        reward_class=reward_class,
                                        observation_func=observation_func)
        self.com = communicate.Com(self.seeds)
        self.config = self.com.config
        self._init_act_rew_obs(self)

    def reset(self):
        #  reset_environment in automate, wait and then grab ext ctrl info
        pass
