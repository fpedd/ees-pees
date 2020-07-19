import numpy as np
from gym import spaces


class WbtObs():
    """Create observation space for continuous action space.

    Description:
    ------------
    WbtObs creates the default observation space in the continous env.
    The lidar data is mapped from 360 to only 12 data points
    to reduce complexity so that the observation space has a shape of 22.

    sim_time:   1  -> current simulation time to adjust accordingly
    gps_actual: 2  -> gps from current position
    gps_target: 2  -> gps of target zone
    speed:      1  -> current speed of the robot
    heading:    1  -> info about the heading of the robot
    steering:   1  -> info about the steering of the robot
    touching:   1  -> flag if the robot touched a wall or obstacle
    act_denied: 1  -> flag to give feedback if action was denied
    lidar:     12  -> mapped from originally 360 to 12 data points to
                          reduce complexity for RL in continuous action space
    -------------
    total:     22

    """

    def __init__(self, env):
        """Initialize WbtObsGrid class with created environment."""
        self.env = env

    @property
    def observation_space(self):
        """Create observation space shape for openai gym alignment."""
        return spaces.Box(-np.inf, np.inf, shape=(22,), dtype=np.float32)

    def get(self):
        """Get standard observation in continuous action space."""
        arr = np.empty(0)
        arr = np.hstack((arr, np.array(self.env.state.sim_time)))
        arr = np.hstack((arr, np.array(self.env.state.gps_actual)))
        arr = np.hstack((arr, np.array(self.env.gps_target)))
        arr = np.hstack((arr, np.array(self.env.state.speed)))
        arr = np.hstack((arr, np.array(self.env.state.heading)))
        arr = np.hstack((arr, np.array(self.env.state.steering)))
        arr = np.hstack((arr, np.array(self.env.state.touching)))
        arr = np.hstack((arr, np.array(self.env.state.action_denied)))
        mean_binned_lidar = self.env.state.mean_lidar(bins=12, relative=False)
        arr = np.hstack((arr, mean_binned_lidar))
        return arr
