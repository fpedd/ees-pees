import struct
import time
from enum import IntEnum
import numpy as np

from webotsgym.env.action import ActionOut


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
    GRID_MOVE = 4


class SafetyType(IntEnum):
    ON = 0
    OFF = 1


class PacketIn():
    """Packet received from the external controller.

    Attributes
    ----------
    error
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

    def _unpack_distance(self, buffer, start=40):
        """Get distance data from buffer, roll to have at heading first."""
        to = start + self.config.DIST_VECS * 4
        N = self.config.DIST_VECS
        self.distance = np.array(struct.unpack("{}f".format(N),
                                               buffer[start: to]))
        self.distance = np.roll(self.distance, 180)

    def _check_success(self):
        self.error = PacketError.NO_ERROR
        if len(self.buffer) != self.config.PACKET_SIZE:
            self.error = PacketError.SIZE


class PacketOut():
    """Packet send to external controller.

    Parameters
    ----------
    msg_cnt : int
    every_x : int
        Receive state data after every_x webots timesteps.
    disable_safety: (int, SafetyType)
    packet_type : (int, PacketType)
    discrete_move : (int, DiscreteMove)
    direction_type : (int, DirectionType)
    action : ActionOut

    """
    def __init__(self, msg_cnt, every_x, disable_safety, packet_type, discrete_move,
                 direction_type, action: ActionOut = ActionOut(action=(0, 0))):
        self.msg_cnt = msg_cnt
        self.every_x = every_x
        self.disable_safety = int(disable_safety)
        self.packet_type = int(packet_type)
        self.discrete_move = int(discrete_move)
        self.direction_type = int(direction_type)
        self.action = action

    def pack(self):
        data = struct.pack('Qdiiiiiff',
                           self.msg_cnt,
                           time.time(),
                           self.every_x,
                           int(self.disable_safety),
                           int(self.packet_type),
                           int(self.discrete_move),
                           int(self.direction_type),
                           self.action.dir,
                           self.action.speed)
        return data
