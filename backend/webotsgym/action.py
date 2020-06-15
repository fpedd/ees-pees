import numpy as np
from gym.spaces import Tuple, Box, Discrete

import webotsgym.utils as utils
from webotsgym.webot import WebotAction


class Action(object):
    def __init__(self):
        self.type = "normal"
    pass


# =========================================================================
# ==========================     WEBOT GRID      ==========================
# =========================================================================
class GridAction(Action):
    def __init__(self):
        self.action_space = Discrete(4)
        self.direction_type = "steering"  # just a dummy
        self.type = "grid"

    def map(self, action):
        # East
        if action == 0:
            return 4
        # South
        if action == 1:
            return 3
        # West
        if action == 2:
            return 2
        # North
        if action == 3:
            return 1
        return None


# =========================================================================
# =========================        DISCRETE       =========================
# =========================================================================
class DiscreteAction(Action):
    """
    Steps, Directions must be of the form 2k + 1, k >= 1
    ----------------------DIRECTIONS--------------------
    -    [0]                 [1]               [2]
    - [0] heading -= 0.2     ....              ....
    -     speed -= 0.2
    S
    P [1] left 36°        DO NOTHING           ....
    E     speed += 0
    E
    D [2] left 36°           ....              +36°
    S     speed += 0.2                     speed += 0.2
    -
    -

    Tuple: shape = (DIRECTIONS, STEPS)
    Flat: shape = DIRECTIONS * STEPS, Index to action:
        move cols first
        0: top left in above
        1: top second to the left
        ...
        -1: bottom right
    """

    def __init__(self, directions=3, speeds=3, dspeed=0.2, dhead=0.2,
                 mode="flatten", direction_type="heading", relative=False):
        self.type = "normal"
        self.mode = mode
        self.direction_type = direction_type
        self.relative = relative

        self.directions = directions
        self.speeds = speeds
        self.dhead = dhead
        self.dspeed = dspeed
        self.action_tuple = (directions, speeds)
        self._set_action_space()
        self._set_mapping_space()

    @property
    def number_of_actions(self):
        if self.mode == "flatten":
            return self.action_tuple[0] * self.action_tuple[1] + 1
        elif self.mode == "tuple":
            return self.action_tuple[0] * (self.action_tuple[1] + 1)

    def _set_action_space(self):
        if self.mode == "flatten":
            self.action_space = Discrete(self.action_tuple[0] *
                                         self.action_tuple[1])
        elif self.mode == "tuple":
            self.action_space = Tuple((Discrete(self.action_tuple[0]),
                                       Discrete(self.action_tuple[1])))

    def _set_mapping_space(self):
        each_dir = (self.directions - 1) / 2
        each_speed = (self.speeds - 1) / 2
        self.dirspace = np.linspace(-self.dhead * each_dir,
                                    self.dhead * each_dir,
                                    self.directions)
        self.speedspace = np.linspace(-self.dspeed * each_speed,
                                      self.dspeed * each_speed,
                                      self.speeds)

    def map(self, action, pre_action):
        if self.mode == "flatten":
            dir_idx = action % len(self.dirspace)
            speed_idx = int((action - dir_idx) / len(self.dirspace))
        elif self.mode == "tuple":
            dir_idx = action[0]
            speed_idx = action[1]

        action = (self.dirspace[dir_idx], self.speedspace[speed_idx])
        if self.relative is True:
            action = utils.add_tuples(pre_action, action)
        action = WebotAction(action)
        return action


# =========================================================================
# =========================       CONTINOUS        ========================
# =========================================================================
class ContinuousAction(Action):
    def __init__(self, direction_type="heading", relative=False):
        self.action_space = Box(-1, 1, shape=(2,), dtype=np.float32)
        self.direction_type = direction_type
        self.relative = relative
        self.type = "normal"

    def map(self, action, pre_action):
        action = tuple(action)
        if self.relative is True:
            action = utils.add_tuples(pre_action, action)
        action = WebotAction(action)
        return action
