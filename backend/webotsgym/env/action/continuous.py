from gym.spaces import Box
import numpy as np

from webotsgym.env.action.action import WbtAct


class WbtActContinuous(WbtAct):
    """Continuous action class.

    Parameters
    ----------
    config : WbtConfig
    bounds : tuple (direction, speed)
        Restrict the possbile action space symmetrically. For example setting
        bounds = (0.7, 0.3) will yield action space with possbile direction
        moves in [-0.7, 0.7] and speeds in [-0.3, 0.3]. Property is only used
        in relative actions. For absolute actions bounds are overwritten to
        (1, 1).
    relative : bool
        Relative (accumulating) or absolute action.

    Attributes
    ----------
    action_space : gym.Box
    type : str
        Type of action.
    config: WbtConfig
    bounds: see parameter bounds
    relative: see parameter relative

    """
    def __init__(self, config, bounds=(1, 1), relative=False):
        super(WbtActContinuous, self).__init__()
        self.config = config
        if relative is False:
            bounds = (1, 1)
        self.bounds = bounds
        self.action_space = Box(low=np.array([-bounds[0], -bounds[1]]),
                                high=np.array([bounds[0], bounds[1]]))
        self.relative = relative
        self.type = "normal"
