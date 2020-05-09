import numpy as np
import matplotlib.pyplot as plt
import abc


class Env(abc.ABC):
    @abc.abstractmethod
    def step(self):
        pass
    def reward(self):
        pass
