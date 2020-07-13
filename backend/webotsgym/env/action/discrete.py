from gym.spaces import Discrete, Tuple
import numpy as np

from webotsgym.env.action.action import WbtAct


class WbtActDiscrete(WbtAct):
    """Discrete action class.

    Generate matrix of possible actions. Rows are possible speeds, columns
    possible directions. With dirs=5, ddir=0.15, speeds=3, dspeed=0.1:
                            DIRECTIONS
            +------+ +------+-------+---+------+-----+
            |      | | -0.3 | -0.15 | 0 | 0.15 | 0.3 |
        S   +------+ +------+-------+---+------+-----+
        P   +------+ +------+-------+---+------+-----+
        E   | -0.1 | | 0    | 1     | 2 | 3    | 4   |
        E   +------+ +------+-------+---+------+-----+
        D   | 0    | | 5    | ...   |   |      |     |
        S   +------+ +------+-------+---+------+-----+
            | 0.1  | |      |       |   |      |     |
            +------+ +------+-------+---+------+-----+
            Example: RL-agent action = 4 is mapped to (0.3, -0.1).
    """

    def __init__(self, config, dirs=3, speeds=3, dspeed=0.1, ddir=0.1,
                 mode="flatten", relative=True):
        super(WbtActDiscrete, self).__init__()
        self.config = config
        self.type = "normal"
        self.mode = mode
        self.relative = relative

        self.dirs = dirs
        self.ddir = ddir
        self.dirspace = None
        self.speeds = speeds
        self.dspeed = dspeed
        self.speedspace = None
        self._set_mapping_space()

        self.action_tuple = (dirs, speeds)
        self._set_action_space()

    @property
    def number_of_actions(self):
        if self.mode == "flatten":
            return self.action_tuple[0] * self.action_tuple[1] + 1
        if self.mode == "tuple":
            return self.action_tuple[0] * (self.action_tuple[1] + 1)
        return None

    def _set_action_space(self):
        if self.mode == "flatten":
            self.action_space = Discrete(self.action_tuple[0]
                                         * self.action_tuple[1])  # noqa W503
        elif self.mode == "tuple":
            self.action_space = Tuple((Discrete(self.action_tuple[0]),
                                       Discrete(self.action_tuple[1])))

    def _set_mapping_space(self):
        each_dir = (self.dirs - 1) / 2
        each_speed = (self.speeds - 1) / 2
        self.dirspace = np.linspace(-self.ddir * each_dir,
                                    self.ddir * each_dir,
                                    self.dirs)
        self.speedspace = np.linspace(-self.dspeed * each_speed,
                                      self.dspeed * each_speed,
                                      self.speeds)

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
        if self.mode == "flatten":
            dir_idx = action % len(self.dirspace)
            speed_idx = int((action - dir_idx) / len(self.dirspace))
        elif self.mode == "tuple":
            dir_idx = action[0]
            speed_idx = action[1]

        action = (self.dirspace[dir_idx], self.speedspace[speed_idx])
        return super().map(action, pre_action)
