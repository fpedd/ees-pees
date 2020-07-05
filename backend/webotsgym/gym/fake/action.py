from env import spaces


class FakeAction():
    def __init__(self, num_of_directions, step_range):
        super(FakeAction, self).__init__()
        self.num_of_directions = num_of_directions
        self.step_range = step_range
        self.steps = step_range[1] - step_range[0] + 1
        self.action_space = spaces.Discrete(num_of_directions * self.steps)

    def action_map(self, action):
        orientation = action % self.num_of_directions
        step_length = int((action - orientation) / self.num_of_directions)
        return (orientation, step_length + self.step_range[0])
