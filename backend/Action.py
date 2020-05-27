import numpy as np
from gym.spaces import Tuple, Box, Discrete

import utils
from webot import WebotState, WebotAction


class Action(object):
    def __init__(self):
        self.action_space = None

    def map(self, action):
        return action


class DiscreteAction(Action):
    """
    Steps, Directions must be of the form 2k + 1, k>=1
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

    Tuple: (DIRECTIONS, STEPS)
    Flat: DIRECTIONS * STEPS
    """

    def __init__(self, directions=3, speeds=3, dspeed=0.2, dhead=0.2,
                 mode="flatten"):
        super(DiscreteAction, self).__init__()
        self.mode = mode
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
                                         self.action_tuple[1] + 1)
        elif self.mode == "tuple":
            self.action_space = Tuple((Discrete(self.action_tuple[0]),
                                       Discrete(self.action_tuple[1] + 1)))

    def _set_mapping_space(self):
        each_dir = (self.directions - 1) / 2
        each_speed = (self.speeds - 1) / 2
        self.dirspace = np.linspace(-self.dhead * each_dir,
                                    self.dhead * each_dir,
                                    self.directions)
        self.speedspace = np.linspace(-self.dspeed * each_speed,
                                      self.dspeed * each_speed,
                                      self.speeds)

    def map(self, action, state: WebotState):
        if self.mode == "flatten":
            if not isinstance(action, int):
                raise TypeError("Action must be int.")
            dir_idx = action % len(self.dirspace)
            speed_idx = int((action - dir_idx) / len(self.speedspace))
        elif self.mode == "tuple":
            dir_idx = action[0]
            speed_idx = action[1]

        # get action difference and add to base action = latest state info
        action_dx = (self.dirspace[dir_idx], self.speedspace[speed_idx])
        action = utils.add_tuples(state.pre_action, action_dx)
        return WebotAction(action)


class ContinuousAction(Action):
    def __init__(self):
        super(ContinuousAction, self).__init__()
        self.action_space = Box(-1, 1, shape=(2,), dtype=np.float32)

    def map(self, action_dx, state: WebotState):
        # TODO: relative, absolute
        action_dx = tuple(action_dx)
        action = utils.add_tuples(state.pre_action, action_dx)
        return WebotAction(action)
