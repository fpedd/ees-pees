from env.spaces import Discrete
from webotsgym.env.webot import WbtAction


class WbtActionGrid(WbtAction):
    """Map proposed fake environment moves to webots.

    0: Right -> Up    (1)
    1: Down  -> Left  (2)
    2: Left  -> Down  (3)
    3: Up    -> Right (4)
    """
    def __init__(self):
        self.action_space = Discrete(4)
        self.direction_type = "steering"  # just a dummy
        self.type = "grid"

    def map(self, action):
        return int(action + 1)
    pass
