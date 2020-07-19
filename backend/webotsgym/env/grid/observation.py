from gym import spaces
import numpy as np

from webotsgym.env.observation import WbtObs


class WbtObsGrid(WbtObs):
    """Create observation class for grid environment.

    Description:
    ------------
    The grid environment has different observation space as the continuous.
    The lidar data is mapped to the for action direction
    and the observation space has a shape of 10.

    gps_actual:         2  -> gps from current position
    gps_target:         2  -> gps of target zone
    lidar:              4  -> lidar mapped from 360 to the 4 directions
    act_denied:         1  -> flag to give feedback if action was denied
    visited_count:      1  -> count for how often position was visited already
    ---------------------
    total:             10

    """

    def __init__(self, env):
        """Initialize WbtObsGrid class with created environment."""
        super(WbtObsGrid, self).__init__(env)

    @property
    def observation_space(self):
        """Create observation space shape for openai gym alignment."""
        return spaces.Box(-np.inf, np.inf, shape=(10,),
                          dtype=np.float32)

    @property
    def lidar(self):
        """Map lidar data from webots to the smaller format in grid."""
        dists = self.env.state.get_grid_distances(4)
        dists = np.flip(dists)
        roll = int(len(dists) / 4)
        dists = np.roll(dists, roll)
        dists = (dists - 0.2) / 0.5
        return np.round(dists)

    @property
    def gps_actual(self):
        """Get current gps position of robot."""
        return np.round(0.5 + np.array(self.env.state.gps_actual) * 2)

    @property
    def gps_target(self):
        """Get gps position of target zone."""
        return np.round(0.5 + np.array(self.env.gps_target) * 2)

    def get(self):
        """Get observation space of 10."""
        arr = np.empty(0)
        arr = np.hstack((arr, self.gps_actual))
        arr = np.hstack((arr, self.gps_target))
        arr = np.hstack((arr, self.lidar))
        arr = np.hstack((arr, np.array(self.env.state.action_denied)))
        arr = np.hstack((arr, np.array(self.env.gps_visited_count)))
        return arr
