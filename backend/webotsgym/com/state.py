import numpy as np

from webotsgym.config import WbtConfig


class WbtState():
    def __init__(self, config: WbtConfig = WbtConfig(), packet_in=None):
        self.config = config
        self.valid = False
        self.packet = packet_in
        if packet_in is not None and packet_in.error.value == 0:
            # get all attributes of packet
            for attr_k, attr_v in packet_in.__dict__.items():
                setattr(self, attr_k, attr_v)
            self.valid = True

    def get_pre_action(self, direction_type="heading"):
        if direction_type == "heading":
            return (self.heading, self.speed)
        else:
            return (self.steering, self.speed)

    def get_grid_distances(self, num):
        every = int(360 / num)
        return self.lidar_absolute[0:-1:every]

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
        if self._touching != 0:
            return True
        return False

    @property
    def lidar_absolute(self):
        return np.roll(self.distance, self.heading_idx)

    @property
    def lidar_relative(self):
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
        if int(self.touching) == 1:
            return True
        return False
