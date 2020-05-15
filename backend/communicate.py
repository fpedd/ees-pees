import socket
import struct
import time
import numpy as np
from enum import Enum

import config


class WebotState(object):
    def __init__(self):
        self.sim_time = None
        self.sim_speed = None
        self.gps_target = None
        self.gps_actual = None
        self.compass = None
        self.distance = None
        self.touching = None

    def fill_from_buffer(self, buffer, DIST_VECS):
        self.sim_time = struct.unpack('f', buffer[16:20])[0]
        self.sim_speed = struct.unpack('f', buffer[20:24])[0]
        self.gps_target = struct.unpack('2f', buffer[24:32])
        self.gps_actual = struct.unpack('2f', buffer[32:40])
        self.compass = struct.unpack('f', buffer[40:44])[0]
        self.touching = struct.unpack("I", buffer[44:48])[0]
        self.distance = struct.unpack("{}f".format(DIST_VECS), buffer[48:(48 + DIST_VECS * 4)])
        self._to_array()

    def _to_array(self):
        for v in self.__dict__.values():
            v = np.array(v)

    def get(self):
        arr = np.empty(0)
        for v in self.__dict__.values():
            arr = np.hstack((arr, v))
        return arr

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


class PacketError(Enum):
    UNITILIZED = -1
    NO_ERROR = 0
    SIZE = 1
    IP = 2
    COUNT = 3
    TIME = 4


class Packet(object):
    def __init__(self):
        self.buffer = None
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


class WebotAction(object):
    def __init__(self):
        self._heading = None
        self._speed = None

    def _init_randomly(self):
        self.heading = np.random.randint(360)
        self.speed = np.random.random() * 200 - 100

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if value < 0:
            value = 0
        if value > 360:
            value = 360
        # if value < 0 or value > 360:
        #     raise ValueError("Value invalid", value)
        self._heading = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value < -100:
            value = -100
        if value > 100:
            value = 100
        # if value < -100 or value > 100:
        #     raise ValueError("Value invalid", value)
        self._speed = value


class Com(object):
    def __init__(self):
        self.conf = config.WebotConfig()
        self.msg_cnt_in = 0
        self.msg_cnt_out = 1
        self.latency = None
        self.state = WebotState()
        self.packet = Packet()
        self.history = []
        self.sock = None

    def _set_sock(self):
        if self.sock is not None:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # reuse socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set buffer size to packet size to store only latest package
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,
                             self.conf.PACKET_SIZE)
        self.sock.bind((self.conf.IP, self.conf.BACKEND_PORT))

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    def recv(self):
        self._set_sock()
        self.packet.buffer, addr = self.sock.recvfrom(self.conf.PACKET_SIZE)
        self.state.fill_from_buffer(self.packet.buffer, self.conf.DIST_VECS)
        # if PACKET_SIZE < len(self.packet.buffer):
        #     print("ERROR: recv did not get full packet", len(self.packet.buffer))
        #     return
        #
        # if IP != addr[0]:
        #     print("ERROR: recv did from wrong address", addr)
        #     return
        #
        # if self.packet.count != self.packet.msg_cnt_in:
        #     print("ERROR: recv wrong msg count, is ", self.packet.count, " should ", self.packet.msg_cnt_in)
        #     self.packet.msg_cnt_in = self.packet.count
        #     return
        #
        # if abs(time.time() - self.packet.time) > TIME_OFFSET_ALLOWED:
        #     print("ERROR: recv time diff to big local ", time.time()," remote ",
        #           self.packet.time, " diff ", abs(time.time() - self.packet.time))
        #     return


    def send(self, action:WebotAction):
        self._set_sock()
        data = struct.pack('Qdff', self.msg_cnt_out, time.time(),
                           action.heading, action.speed)
        # ret = self.sock.sendto(data, (IP, CONTROL_PORT))
        ret = self.sock.sendto(data, (self.conf.IP, self.conf.CONTROL_PORT))
        if ret == len(data):
            self.msg_cnt_out += 2
        else:
            print("ERROR: could not send message, is ", ret, " should ", len(data))
