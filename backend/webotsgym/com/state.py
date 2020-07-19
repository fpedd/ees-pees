import numpy as np

from webotsgym.env.action import ActionOut
from webotsgym.config import DirectionType


class WbtState():
    """Current state of Webots robot.

    Attributes
    ----------
    valid
    packet
    count
    time_in
    sim_time
    speed
    gps_actual
    heading
    steering
    _touching
    action_denied
    discrete_action_done
    distance

    """

    def __init__(self, config, packet_in):
        """Initialize WbtState class."""
        self.config = config
        self.valid = False
        self.packet = packet_in
        self.count = None
        self.time_in = None
        self.sim_time = None
        self.speed = None
        self.gps_actual = None
        self.heading = None
        self.steering = None
        self._touching = None
        self.action_denied = None
        self.discrete_action_done = None
        self.distance = None

        if packet_in.error.value == 0:
            # get all attributes of packet
            for attr_k, attr_v in packet_in.__dict__.items():
                if hasattr(self, attr_k):
                    setattr(self, attr_k, attr_v)
            self.valid = True

    def get_grid_distances(self, num):
        """Get lidar data for amount of actions in grid action class."""
        every = int(360 / num)
        return self.lidar_absolute[0:-1:every]

    def get_pre_action(self):
        """Get previous value for direction and speed.

        Returns
        -------
        ActionOut
            Previous (direction, speed) tuple for relative actions.

        """
        act = ActionOut()
        act.speed = self.speed
        if self.config.direction_type == DirectionType.HEADING:
            act.dir = self.heading
        elif self.config.direction_type == DirectionType.STEERING:
            act.dir = self.steering
        return act

    def mean_lidar(self, bins=12, relative=False):
        """Get mean lidar data.

        Parameters
        ----------
        bins : int
            Number of bins for lidar data to calculate mean.
        relative : bool
            Bin relative or absolute lidar data.

        Returns
        -------
        lidar_binned
            Binned mean lidar data.

        """
        every = int(360 / bins)
        if relative is True:
            x = self.lidar_relative
        else:
            x = self.lidar_absolute
        x = x.reshape((-1, every))
        return np.mean(x, axis=1)

    @property
    def touching(self):
        """Get info if obstacle was hit with helper function."""
        if self._touching != 0:
            return True
        return False

    @property
    def lidar_absolute(self):
        """Get lidar data in absolute values."""
        return np.roll(self.distance, self.heading_idx)

    @property
    def lidar_relative(self):
        """Get lidar data in relative values."""
        return self.distance

    @property
    def heading_idx(self):
        """Get index of heading in distance values."""
        if self.heading > 0:
            idx = self.heading * 180
        else:
            idx = 360 + self.heading * 180
        return int(idx - 1)

    @property
    def crash(self) -> bool:
        """Get information if we crashed into an obstacle."""
        if int(self.touching) == 1:
            return True
        return False
