import numpy as np

from webotsgym.config import WbtConfig, DirectionType


class WbtAct():
    """Create action class for webots.

    Parameter:
    ---------
    config : object
        config object created by the config class
        object class with all important information about
        the webots env and communication
        Default : none

    type : string
        action type to differentiate between action types (grid and continuous)

    relative : Boolean
        True : add mapped values of 'action' to the 'pre-action'
        Default : None

    Return:
    -------
    integer
        index found for value between the boundaries



    """
    def __init__(self, config=None):
        """Initializes the WbtAct class."""
        self.config = config
        self.type = "normal"
        self.relative = None

    def map(self, action, pre_action=None):
        """Map RL-agent action to webots action.

        If 'relative' is True, the mapped values of 'action' will be added
        to the 'pre-action', e.g. pre_action = (0.2, 0.3), action = (-0.1, 0.1)
        will result in (0.1, 0.4).

        Parameters:
        -----------
        action : int, tuple
            Action from RL-agent.
        pre_action : ActionOut
            Last action send to external controller.

        Returns:
        --------
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
        """Initialize the ActionOut class."""
        self.config = config
        self._dir = None
        self._speed = None
        if isinstance(action, (np.ndarray, list, tuple)):
            self.dir = action[0]
            self.speed = action[1]

    def print_action(self):
        """Print the direction and speed of an action."""
        print("dir: ", self.dir)
        print("speed:   ", self.speed)

    def _init_randomly(self):
        """Initialize a random action by setting random direction & speed."""
        self.dir = np.random.random() * 2 - 1
        self.speed = np.random.random() * 2 - 1

    @property
    def dir(self):
        """Get direction of robot."""
        return self._dir

    @dir.setter
    def dir(self, value):
        """Set direction depending on direction type and value.

        Parameter:
        ----------
        value : integer
            value to set the direction correctly depending of direction type

        Return:
        -------
        integer
            direction for the robot

        """
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
        """Get speed of robot."""
        return self._speed

    @speed.setter
    def speed(self, value):
        """Set speed depending on value.

        Parameter:
        ----------
        value : integer
            value to set speed between [-1, 1]

        Return:
        -------
        integer
            speed for the robot

        """
        if value < -1:
            value = -1
        if value > 1:
            value = 1
        self._speed = value
