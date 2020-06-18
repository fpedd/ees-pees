import numpy as np
from gym import spaces


class Observation():
    def __init__(self, env):
        self.env = env

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(368,), dtype=np.float32)

    def get(self):
        """Get standard observation.

        sim_time:   1
        gps_actual: 2
        gps_target: 2
        heading:    1
        steering:   1
        touching:   1
        lidar:    360
        -------------
        total:    368
        """
        arr = np.empty(0)
        arr = np.hstack((arr, np.array(self.env.state.sim_time)))
        arr = np.hstack((arr, np.array(self.env.state.gps_actual)))
        arr = np.hstack((arr, np.array(self.env.gps_target)))
        arr = np.hstack((arr, np.array(self.env.state.heading)))
        arr = np.hstack((arr, np.array(self.env.state.steering)))
        arr = np.hstack((arr, np.array(self.env.state.touching)))
        arr = np.hstack((arr, np.array(self.env.state.lidar_absolute)))
        return arr


class GridObservation(Observation):
    def __init__(self, env):
        super(GridObservation, self).__init__(env)

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(8,), dtype=np.float32)

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
        # arr = np.hstack((arr, np.array(self.env.state.action_denied)))
        return arr
