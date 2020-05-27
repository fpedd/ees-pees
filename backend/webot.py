import struct
import numpy as np


class WebotState(object):
    def __init__(self):
        self.sim_time = None
        self.sim_speed = None
        self.gps_target = None
        self.gps_actual = None
        self.compass = None
        self.distance = None
        self.touching = None

    def fill_from_buffer(self, buf, dv):
        self.sim_time = struct.unpack('f', buf[16:20])[0]
        self.sim_speed = struct.unpack('f', buf[20:24])[0]
        self.gps_target = struct.unpack('2f', buf[24:32])
        self.gps_actual = struct.unpack('2f', buf[32:40])
        self.compass = struct.unpack('f', buf[40:44])[0]
        self.touching = struct.unpack("I", buf[44:48])[0]
        self.distance = struct.unpack("{}f".format(dv), buf[48:(48 + 4 * dv)])

    def get(self):
        """Get webot state as numpy array."""
        arr = np.empty(0)
        for v in self.__dict__.values():
            arr = np.hstack((arr, np.array(v)))
        return arr

    @property
    def pre_action(self):
        return (self.compass, self.speed)

    @property
    def observation_shape(self):
        if self.state_filled:
            arr = self.get()
            return arr.shape
        return None

    @property
    def state_filled(self):
        if self.gps_actual is not None:
            return True
        return False

    @property
    def num_of_sensors(self):
        if self.distance is None:
            return None
        return len(self.distance)

    @property
    def gps_size(self):
        if self.gps_actual is None:
            return None
        return len(self.gps_actual)

    @property
    def compass_size(self):
        if self.compass is None:
            return None
        return len(self.compass)


class WebotAction(object):
    def __init__(self, action=None):
        self._heading = None
        self._speed = None
        if isinstance(action, tuple):
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
