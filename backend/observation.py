import numpy as np


class Observation():
    def __init__(self, env):
        self.env = env

    @property
    def observation_space(self):
        return (20, )

    def get(self):
        return self.env.state.get()
