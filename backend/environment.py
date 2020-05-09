import numpy as np
import matplotlib.pyplot as plt
import abc

import com


class Env(abc.ABC):
    @abc.abstractmethod
    def step(self):
        pass
    def reward(self):
        pass


class WebotState(object):
    def __init__(self):
        self.buffer = None
        # self.msg_cnt_in = 0
        # self.time_in = None
        self.gps_target = None
        self.gps_actual = None
        self.compass = None
        self.distance = None
        self.touching = None

    def fill_from_buffer(self):
        pass

    def get(self):
        # TODO return state as numpy array
        pass


class WebotAction(object):
    def __init__(self):
        self.heading = None
        self.speed = None

    def send(self):
        # TODO: com.send(stuff)
        pass


class WebotsEnv(Env):
    def __init__(self):
        self.state = None
        self.action = None

    def step(self, action):
        pass

    def random_action(self):
        pass

    def reward(self):
        pass

    @property
    def state_arr(self):
        return self.state.get()


WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class FakeEnvironment(Env):
    def __init__(self, N, num_of_sensors=4, startpos=None, target_pos=None):
        self.N = N
        self.offset = int(2*N)

    def setup_fields(self):
        self.grid = np.zeros((self.total_len, self.total_len))
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)

        # set up walls
        self.field[0: WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL
