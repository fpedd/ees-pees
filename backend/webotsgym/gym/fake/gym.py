from gym import spaces
import numpy as np


from webotsgym.gym.fake import FakeState, FakeAction

WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class WbtGymFake(gym.Env):
    def __init__(self, seed=None, N=10, num_of_sensors=4, obstacles_each=4, step_range=(1, 1), obs=FakeState, obs_len=1):
        super(WbtGymFake, self).__init__()

        self.history = {}

        self.action_mapper = FakeAction(4, step_range)

        self.seed(seed)
        self.reward_range = (-100, 100)
        self.action_mapping = self.action_mapper.action_map
        self.action_space = self.action_mapper.action_space

        self.com_inits = (N, num_of_sensors, obstacles_each, obs_len)
        self.com = FakeCom(self.seeds, self.com_inits[0], self.com_inits[1],
                           self.com_inits[2], self.com_inits[3])
        self.plotpadding = 0
        self.visited_count = np.zeros(self.com.field.shape)

        if type(obs) == type:
            self.obs = (obs)(self)
        else:
            self.obs = obs
        self.observation_space = spaces.Box(0, np.inf, shape=self.obs.shape(),
                                            dtype=np.float32)

        self.total_reward = 0
