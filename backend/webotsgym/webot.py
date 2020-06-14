import struct
import numpy as np

from webotsgym.config import WebotConfig


# =========================================================================
# ==============================    STATE    ==============================
# =========================================================================
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
        self.steering = None
        self.distance = None
        self._touching = None

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
            self.steering = struct.unpack('f', buffer[36:40])[0]
            self._touching = struct.unpack("I", buffer[40:44])[0]
            self._unpack_distance(buffer, start=44)

    def _unpack_distance(self, buffer, start=40):
        to = start + self.num_lidar * 4
        N = self.num_lidar
        self.distance = np.array(struct.unpack("{}f".format(N),
                                               buffer[start: to]))

    def get_pre_action(self, direction_type="heading"):
        if direction_type == "heading":
            return (self.heading, self.speed)
        else:
            return (self.steering, self.speed)

    @property
    def touching(self):
        if any(self.distance < 0.1):
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
    def num_lidar(self):
        return self.config.DIST_VECS

    @property
    def transmission_success(self):
        if len(self.buffer) == self.config.PACKET_SIZE:
            return True
        return False


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


# =========================================================================
# ==============================    ACTION   ==============================
# =========================================================================
class WebotAction(object):
    def __init__(self, action=None):
        self._heading = None
        self._speed = None
        if isinstance(action, (np.ndarray, list, tuple)):
            self.heading = action[0]
            self.speed = action[1]

    def print(self):
        print("heading: ", self.heading)
        print("speed:   ", self.speed)

    def _init_randomly(self):
        self.heading = np.random.random() * 2 - 1
        self.speed = np.random.random() * 2 - 1

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if value < -1:
            value = 2 + value
        elif value > 1:
            value = -2 + value
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
