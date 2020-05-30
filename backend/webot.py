import struct
import numpy as np

from config import WebotConfig


class WebotState(object):
    def __init__(self, config: WebotConfig = WebotConfig()):
        # meta
        self.config = config
        self.buffer = None

        # state
        self.sim_time = None
        self.speed = None
        self.gps_actual = None
        self.heading = None
        self.distance = None
        self.touching = None

    def fill_from_buffer(self, buffer):
        """Set state from buffer information in packet from external controller.

        Fills state information of transmission was success.
        """
        self.buffer = buffer
        if self.transmission_success:
            self.sim_time = struct.unpack('f', buffer[16:20])[0]
            self.speed = struct.unpack('f', buffer[20:24])[0]
            self.gps_actual = struct.unpack('2f', buffer[24:32])
            self.heading = struct.unpack('f', buffer[32:36])[0]
            self.touching = struct.unpack("I", buffer[36:40])[0]
            self.distance = struct.unpack("{}f".format(self.num_lidar), buffer[40: (40 + self.num_lidar*4)])

    def get(self):
        """Get webot state as numpy array."""
        # TODO: update here nur sim time, speed etc zu nehmen ...
        arr = np.empty(0)
        for v in self.__dict__.values():
            arr = np.hstack((arr, np.array(v)))
        return arr

    @property
    def num_lidar(self):
        return self.config.DIST_VECS

    @property
    def transmission_success(self):
        # TODO: abfangen in paket
        if len(self.buffer) == self.config.PACKET_SIZE:
            return True
        return False

    @property
    def pre_action(self):
        return (self.heading, self.speed)

    @property
    def crash(self) -> bool:
        if int(self.touching) == 1:
            return True
        return False

    @property
    def gps_size(self):
        if self.gps_actual is None:
            return None
        return len(self.gps_actual)

    @property
    def heading_size(self):
        if self.heading is None:
            return None
        return len(self.heading)

    # @property
    # def observation_shape(self):
    #     if self.state_filled:
    #         arr = self.get()
    #         return arr.shape
    #     return None


class WebotAction(object):
    def __init__(self, action=None):
        self._heading = None
        self._speed = None
        if isinstance(action, (np.ndarray, list, tuple)):
            self.heading = action[0]
            self.speed = action[1]

    def print(self):
        print("heading: ", self.heading)
        print("speed:\t ", self.speed)

    def _init_randomly(self):
        self.heading = np.random.random(2) - 1
        self.speed = np.random.random(2) - 1

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if value < -1:
            value = -1
        if value > 1:
            value = 1
        self._heading = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value < -1:
            value = -1
        if value > 1:
            value = 1
        self._speed = value
