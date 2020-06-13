import numpy as np
from gym import spaces


class Observation():
    def __init__(self, env):
        self.env = env

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(367,), dtype=np.float32)

    def get(self):
        """Get standard observation.

        sim_time:   1
        gps_actual: 2
        gps_target: 2
        heading:    1
        touching:   1
        lidar:    360
        -------------
        total:    367
        """
        arr = np.empty(0)
        arr = np.hstack((arr, np.array(self.env.state.sim_time)))
        arr = np.hstack((arr, np.array(self.env.state.gps_actual)))
        arr = np.hstack((arr, np.array(self.env.gps_target)))
        arr = np.hstack((arr, np.array(self.env.state.heading)))
        arr = np.hstack((arr, np.array(self.env.state.touching)))
        arr = np.hstack((arr, np.array(self.env.state.lidar_absolute)))
        return arr
