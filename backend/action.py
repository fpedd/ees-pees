import numpy as np
from gym.spaces import Tuple, Box, Discrete


class Action(object):
    def __init__(self):
        self.action_space = None

    def map(self, action):
        return action


class DiscreteAction(Action):
    def __init__(self, env, mode="flatten"):
        super(DiscreteAction, self).__init__()
        self.env = env
        self.mode = mode
        self._set_action_space()

    def _set_action_space(self):
        if self.mode == "flatten":
            self.action_space = Discrete(self.env.act_tpl[0] *
                                         self.env.act_tpl[1])
        elif self.mode == "tuple":
            self.action_space = Tuple((Discrete(self.env.act_tpl[0]),
                                       Discrete(self.env.act_tpl[1])))


class DiscreteFlat4(DiscreteAction):
    def __init__(self, env):
        env.act_tpl = (4, 1)
        super(DiscreteFlat4, self).__init__(env)


class ContinuousAction(Action):
    def __init__(self, env):
        super(ContinuousAction, self).__init__()
        self.action_space = Box(-1, 1, shape=(2,), dtype=np.float32)

    # if type is fake then bla
    # def action_map(self, action):
    #     orientation, length = action
    #     orientation = utils.id_in_range(-1, 1, self.num_of_directions, orientation)
    #     length = utils.id_in_range(-1, 1, self.steps, length) + self.step_range[0]
    #     return orientation, length
