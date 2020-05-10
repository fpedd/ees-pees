import numpy as np
import abc
from pynput import keyboard
import time

import communicate
import environment

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


class WebotCtrAgent(Agent):
    def __init__(self):
        self.dheading = 3
        self.dspeed = 3
        self.env = environment.WebotsEnv()
        self._init_action()

    def _init_action(self):
        self.act = communicate.WebotAction()
        self.act.heading = np.random.randint(360)
        self.act.speed = np.random.random() * 200 - 100

    def action(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        condition = False
        if key == keyboard.Key.up:
            self.act.speed += self.dspeed
            condition = True
        if key == keyboard.Key.down:
            self.act.speed -= self.dspeed
            condition = True
        if key == keyboard.Key.left:
            self.act.heading -= self.dheading
            condition = True
        if key == keyboard.Key.right:
            self.act.heading += self.dheading
            condition = True
        if condition is True:
            self.env.step(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False
