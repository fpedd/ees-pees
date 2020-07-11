from gym.spaces import Discrete
from webotsgym.env.action import WbtAct


class WbtActGrid(WbtAct):
    """Map proposed fake environment moves to webots.

    0: Right -> Up    (1)
    1: Down  -> Left  (2)
    2: Left  -> Down  (3)
    3: Up    -> Right (4)
    """
    def __init__(self, config=None):
        self.config = config
        self.action_space = Discrete(4)
        self.direction_type = "steering"  # just a dummy
        self.type = "grid"

    def map(self, action):
        return int(action + 1)
