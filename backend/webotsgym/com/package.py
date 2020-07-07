from enum import IntEnum
import time
import numpy as np
import struct


class PacketError(IntEnum):
    UNITILIZED = -1
    NO_ERROR = 0
    SIZE = 1
    IP = 2
    COUNT = 3
    TIME = 4


class PacketType(IntEnum):
    UNDEF = 0
    COM = 1
    REQ = 2
    COM_REQ = 3


class PacketIn():
    def __init__(self, config, buffer=None):
        self.config = config
        self.buffer = buffer
        self.error = PacketError.UNITILIZED
        self._check_success()
        if self.error == PacketError.NO_ERROR:
            self.count = struct.unpack('Q', buffer[0:8])[0]
            self.time_in = struct.unpack('d', buffer[8:16])[0]
            self.sim_time = struct.unpack('f', buffer[16:20])[0]
            self.speed = struct.unpack('f', buffer[20:24])[0]
            self.gps_actual = struct.unpack('2f', buffer[24:32])
            self.heading = struct.unpack('f', buffer[32:36])[0]
            self.steering = struct.unpack('f', buffer[36:40])[0]
            self._touching = struct.unpack("I", buffer[40:44])[0]
            self.action_denied = struct.unpack("I", buffer[44:48])[0]
            self.discrete_action_done = struct.unpack("I", buffer[48:52])[0]
            self._unpack_distance(buffer, start=52)

    def _check_success(self):
        self.error = PacketError.NO_ERROR
        if len(self.buffer) == self.config.PACKET_SIZE:
            self.error = PacketError.SIZE
        # if IP != addr[0]:
        #     print("ERROR: recv did from wrong address", addr)
        #     return
        #
        # if self.packet.count != self.packet.msg_cnt_in:
        #     print("ERROR: recv wrong msg count, is ", self.packet.count, " should ",
        #           self.packet.msg_cnt_in)
        #     self.packet.msg_cnt_in = self.packet.count
        #     return
        #

    def _unpack_distance(self, buffer, start=40):
        """Get distance data from buffer, roll to have at heading first."""
        to = start + self.config.DIST_VECS * 4
        N = self.config.DIST_VECS
        self.distance = np.array(struct.unpack("{}f".format(N),
                                               buffer[start: to]))
        self.distance = np.roll(self.distance, 180)


class ActionOut():
    def __init__(self, action=None, direction_type="heading"):
        self.direction_type = direction_type
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


class PacketOut():
    def __init__(self, msg_cnt, packet_type, discrete_move, direction_type,
                 action: ActionOut = ActionOut(action=(0, 0))):
        self.msg_cnt = msg_cnt
        self.packet_type = int(packet_type)
        self.discrete_move = int(discrete_move)
        self.direction_type = int(direction_type)
        self.action = action

    def pack(self):
        data = struct.pack('Qdiiiff',
                           self.msg_cnt,
                           time.time(),
                           self.packet_type,
                           int(self.discrete_move),
                           int(self.direction_type),
                           self.action.heading,
                           self.action.speed)
        return data
