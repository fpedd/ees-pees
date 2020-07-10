import numpy as np

from webotsgym.env import WbtGym
from webotsgym.env.grid.action import WbtActGrid
from webotsgym.env.grid.observation import WbtObsGrid
from webotsgym.config import WbtConfig
from webotsgym.env.reward import WbtRewardGrid


class WbtGymGrid(WbtGym):
    def __init__(self, seed=None, gps_target=(1, 1),
                 train=False, evaluate_class=WbtRewardGrid,
                 config: WbtConfig = WbtConfig()):
        config.world_scaling = 0.5
        super(WbtGymGrid, self).__init__(seed=seed,
                                         gps_target=gps_target,
                                         train=train,
                                         action_class=WbtActGrid,
                                         evaluate_class=evaluate_class,
                                         observation_class=WbtObsGrid,
                                         config=config)
        len = int(config.world_size * config.world_scaling) * 2 + 1
        self.visited_count = np.zeros((len, len))
        self.time_steps = 0

    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        if self.action_class.type != "grid":
            raise TypeError("WebotsGrid need grid action class.")

        self.state.action_denied = 0
        if self.observation_class.lidar[action] < 1:  # safety :D
            self.state.action_denied = 1
        else:
            action = self.action_class.map(action)
            self.com.send_grid_move(action)
            self.com._wait_for_grid_done()

        self.visited_count[self.gps_actual_scaled] += 1
        reward = self.calc_reward()
        self.rewards.append(reward)
        done = self.check_done()

        # logging, printing
        self.rewards.append(reward)
        self.distances.append(self.get_target_distance())
        self.time_steps += 1
        return self.observation, reward, done, {}

    def reset(self, seed=None):
        super().reset(seed)
        self.time_steps = 0

        len = int(self.config.world_size * self.config.world_scaling) * 2 + 1
        self.visited_count = np.zeros((len, len))
        return self.observation

    @property
    def gps_visited_count(self):
        return self.visited_count[self.gps_actual_scaled]

    @property
    def gps_actual_scaled(self):
        return tuple(np.round(0.5 + np.array(self.gps_actual) * 2).astype(int))
