from gym.spaces import Box
import numpy as np

from webotsgym.env.action import WbtAct
from webotsgym.com import ActionOut


class WbtActContinuous(WbtAct):
    def __init__(self, config, bound=1, relative=False):
        self.config = config
        if relative is False:
            bound = 1
        self.bound = bound
        self.action_space = Box(-bound, bound, shape=(2,), dtype=np.float32)
        self.relative = relative
        self.type = "normal"

    def map(self, action, pre_action):
        dir, speed = action
        if self.relative is True:
            dir_pre, speed_pre = pre_action.dir, pre_action.speed
            dir += dir_pre
            speed += speed_pre
        action = ActionOut(self.config, (dir, speed))
        return action
