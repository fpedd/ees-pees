from gym.spaces import Box
import numpy as np

from webotsgym.action import WbtAct
from webotsgym.utils import add_tuples
from webotsgym.comm import ActionOut


class WbtActContinuous(WbtAct):
    def __init__(self, direction_type="heading", relative=False):
        self.action_space = Box(-1, 1, shape=(2,), dtype=np.float32)
        self.direction_type = direction_type
        self.relative = relative
        self.type = "normal"

    def map(self, action, pre_action):
        action = tuple(action)
        if self.relative is True:
            action = add_tuples(pre_action, action)
        action = ActionOut(action, direction_type=self.direction_type)
        return action
