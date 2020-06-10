import numpy as np
from gym import spaces


class Observation():
    def __init__(self, env):
        self.env = env

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(367,), dtype=np.float32)

    def get(self):
        return self.env.state.get()
