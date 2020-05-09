import numpy as np
import matplotlib.pyplot as plt
import abc

import communicate


class Env(abc.ABC):
    @abc.abstractmethod
    def step(self):
        pass
    def reward(self):
        pass


class WebotsEnv(Env):
    def __init__(self):
        self.com = communicate.Com()

    def step(self, action=None):
        a = self.random_action()
        self.com.send(a)
        self.com.recv()
        return self.state, 0, False, {}

    def random_action(self):
        action = communicate.WebotAction()
        action.heading = np.random.randint(360)
        action.speed = np.random.random() * 200 - 100
        return action

    def reward(self):
        pass

    @property
    def state(self):
        return self.com.state.get()


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
