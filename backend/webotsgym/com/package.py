from enum import Enum
import time
import numpy as np
import struct

from webotsgym.config import WbtConfig



class PacketError(Enum):
    UNITILIZED = -1
    NO_ERROR = 0
    SIZE = 1
    IP = 2
    COUNT = 3
    TIME = 4


class PacketType(Enum):
    UNDEF = 0
    COM = 1
    REQ = 2
    COM_REQ = 3


class PacketIn():
    def __init__(self, config: WbtConfig = WbtConfig()):
        self.config = config
        self.time_in = None
        self.error = PacketError.UNITILIZED

    @property
    def count(self):
        return struct.unpack('Q', self.buffer[0:8])[0]

    @property
    def time(self):
        return struct.unpack('d', self.buffer[8:16])[0]

    @property
    def success(self):
        if self.error == PacketError.UNITILIZED:
            return None
        elif self.error == PacketError.NO_ERROR:
            return True
        return False


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
        self.time = time.time()

        if isinstance(packet_type, int):
            self.packet_type = packet_type
        else:
            self.packet_type = packet_type.value

        if isinstance(discrete_move, int):
            self.discrete_move = discrete_move
        else:
            self.discrete_move = discrete_move.value

        if isinstance(direction_type, int):
            self.direction_type = direction_type
        else:
            self.direction_type = direction_type.value

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
