from gym import spaces
import numpy as np

from webotsgym.env.observation import WbtObs


class WbtObsGrid(WbtObs):
    def __init__(self, env):
        super(WbtObsGrid, self).__init__(env)

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(10,),
                          dtype=np.float32)

    @property
    def lidar(self):
        dists = self.env.state.get_grid_distances(4)
        dists = np.flip(dists)
        roll = int(len(dists) / 4)
        dists = np.roll(dists, roll)
        dists = (dists - 0.2) / 0.5
        return np.round(dists)

    @property
    def gps_actual(self):
        return np.round(0.5 + np.array(self.env.state.gps_actual) * 2)

    @property
    def gps_target(self):
        return np.round(0.5 + np.array(self.env.gps_target) * 2)

    def get(self):
        arr = np.empty(0)
        arr = np.hstack((arr, self.gps_actual))
        arr = np.hstack((arr, self.gps_target))
        arr = np.hstack((arr, self.lidar))
        arr = np.hstack((arr, np.array(self.env.state.action_denied)))
        arr = np.hstack((arr, np.array(self.env.gps_visited_count)))
        return arr
