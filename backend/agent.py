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
        action._init_randomly()
        return action


class WebotCtrAgent(Agent):
    def __init__(self):
        self.dheading = 3
        self.dspeed = 3
        self.env = environment.WebotsEnv()
        self._init_action()

    def _init_action(self):
        self.act = communicate.WebotAction()
        self.act._init_randomly()

    def action(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.up:
            self.act.speed += self.dspeed
        elif key == keyboard.Key.down:
            self.act.speed -= self.dspeed
        elif key == keyboard.Key.left:
            self.act.heading -= self.dheading
        elif key == keyboard.Key.right:
            self.act.heading += self.dheading
        else:
            return
        self.env.step(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False
