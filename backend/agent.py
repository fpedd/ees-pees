import numpy as np
import abc

import communicate

class Agent(abc.ABC):
    # @abc.abstractmethod
    # def train(self):
    #     pass
    @abc.abstractmethod
    def action(self):
        pass


class RndWebotAgent(Agent):
    def __init__(self):
        pass

    def action(self):
        action = communicate.WebotAction()
        action.heading = np.random.randint(360)
        action.speed = np.random.random() * 200 - 100
        return action
