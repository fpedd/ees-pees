import numpy as np
from gym import spaces


class WbtObs():
    def __init__(self, env):
        self.env = env

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(20,), dtype=np.float32)

    def get(self):
        """Get standard observation.

        sim_time:   1
        gps_actual: 2
        gps_target: 2
        heading:    1
        steering:   1
        touching:   1
        lidar:     12
        -------------
        total:     20
        """
        arr = np.empty(0)
        arr = np.hstack((arr, np.array(self.env.state.sim_time)))
        arr = np.hstack((arr, np.array(self.env.state.gps_actual)))
        arr = np.hstack((arr, np.array(self.env.gps_target)))
        arr = np.hstack((arr, np.array(self.env.state.heading)))
        arr = np.hstack((arr, np.array(self.env.state.steering)))
        arr = np.hstack((arr, np.array(self.env.state.touching)))
        mean_binned_lidar = self.env.state.mean_lidar(bins=12, relative=False)
        arr = np.hstack((arr, mean_binned_lidar))
        return arr
