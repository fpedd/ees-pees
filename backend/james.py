import abc
from pynput import keyboard
import numpy as np
import time

import communicate
# import environment
from Action import ContinuousAction
from webot import WebotAction


class Agent(abc.ABC):
    def __init__(self):
        self.history = []

    @abc.abstractmethod
    def action(self):
        pass


class RndWebotAgent(Agent):
    def __init__(self):
        self.com = communicate.Com()

    def action(self):
        action = WebotAction()
        self.com.recv()
        print("current state")
        print(self.com.state.gps_actual)
        action.heading = np.random.random() * 2 - 1
        action.speed = np.random.random() * 2 - 1
        time.sleep(0.2)
        action.print()
        self.com.send(action)

#
# class WebotCtrAgent(Agent):
#     def __init__(self):
#         self.dheading = 0.05
#         self.dspeed = 0.05
#         self.env = environment.WebotsEnv(action_class=ContinuousAction)
#         self.env.recv()
#         self._init_action()
#
#     def _init_action(self):
#         self.act = WebotAction()
#         self.act.speed = 0
#         self.act.heading = 0
#
#     def action(self):
#         with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
#             listener.join()
#
#     def on_press(self, key):
#         if key == keyboard.Key.up:
#             self.act.speed += self.dspeed
#         elif key == keyboard.Key.down:
#             self.act.speed -= self.dspeed
#         elif key == keyboard.Key.left:
#             self.act.heading -= self.dheading
#         elif key == keyboard.Key.right:
#             self.act.heading += self.dheading
#         else:
#             return
#         self.env.step((self.act.heading, self.act.speed))
#
#     def on_release(self, key):
#         if key == keyboard.Key.esc:
#             return False
#
#
# if __name__ == "__main__":
#     james = WebotCtrAgent()
#     james.action()
