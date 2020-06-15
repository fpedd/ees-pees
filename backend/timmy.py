import abc
from pynput import keyboard
import numpy as np
import time

import webotsgym.communicate as communicate
import webotsgym.environment as environment
from webotsgym.action import ContinuousAction
from webotsgym.webot import WebotAction


class Agent(abc.ABC):
    def __init__(self):
        self.history = []

    @abc.abstractmethod
    def action(self):
        pass


class Agent(Agent):
    def __init__(self, direction_type="heading"):
        self.dheading = 0.05
        self.dspeed = 0.05
        action_class = ContinuousAction(direction_type=direction_type)
        self.env = environment.WebotsEnv(action_class=action_class)
        self._init_action()

    def _init_action(self):
        self.act = WebotAction()
        self.act.speed = 0
        self.act.heading = 0

    def action(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.up:
            move = 1
        elif key == keyboard.Key.down:
            move = 3
        elif key == keyboard.Key.left:
            move = 2
        elif key == keyboard.Key.right:
            move = 4
        else:
            return
        print(move)
        self.env.send_discrete_move(move)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    james = Agent(direction_type="heading")
    james.action()
