import numpy as np

from webotsgym.config import WbtConfig, DirectionType


class WbtAct():
    def __init__(self, config=None):
        self.config = config
        self.type = "normal"
        self.relative = None

    def map(self, action, pre_action=None):
        """Map RL-agent action to webots action.

        If 'relative' is True, the mapped values of 'action' will be added
        to the 'pre-action', e.g. pre_action = (0.2, 0.3), action = (-0.1, 0.1)
        will result in (0.1, 0.4).

        Parameters
        ----------
        action : int, tuple
            Action from RL-agent.
        pre_action : ActionOut
            Last action send to external controller.

        Returns
        -------
        ActionOut
            New action to be send to external controller.

        """
        dir, speed = action
        if self.relative is True and pre_action is not None:
            dir_pre, speed_pre = pre_action.dir, pre_action.speed
            dir += dir_pre
            speed += speed_pre
        action = ActionOut(self.config, (dir, speed))
        return action


class ActionOut():
    """Class that is basis for action to be send to external controller.

    Handles some cases to stay in the action limits [-1, 1] x [-1, 1].
    """
    def __init__(self, config=WbtConfig(), action=None):
        self.config = config
        self._dir = None
        self._speed = None
        if isinstance(action, (np.ndarray, list, tuple)):
            self.dir = action[0]
            self.speed = action[1]

    def print_action(self):
        print("dir: ", self.dir)
        print("speed:   ", self.speed)

    def _init_randomly(self):
        self.dir = np.random.random() * 2 - 1
        self.speed = np.random.random() * 2 - 1

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, value):
        if self.config.direction_type == DirectionType.HEADING:
            if value < -1:
                value = 2 + value
            elif value > 1:
                value = -2 + value
        elif self.config.direction_type == DirectionType.STEERING:
            if value < -1:
                value = -1
            if value > 1:
                value = 1
        else:
            raise ValueError("Invalid direction_type.")
        self._dir = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value < -1:
            value = -1
        if value > 1:
            value = 1
        self._speed = value
