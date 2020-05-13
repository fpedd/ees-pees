import socket
import struct
import time
import numpy as np
import configparser
from enum import Enum


class Config(configparser.ConfigParser):
    def __init__(self, config_file="config.ini"):
        super(Config, self).__init__()
        self.read(config_file)

    @property
    def success(self):
        if len(self.sections()) > 0:
            return True
        return False

    @property
    def IP(self):
        if self.success is True:
            return self.get('Network', 'IP')
        else:
            return "127.0.0.1"

    @property
    def CONTROL_PORT(self):
        if self.success is True:
            return int(self.get('Network', 'CONTROL_PORT'))
        else:
            return 6969

    @property
    def BACKEND_PORT(self):
        if self.success is True:
            return int(self.get('Network', 'BACKEND_PORT'))
        else:
            return 6970

    @property
    def TIME_OFFSET_ALLOWED(self):
        if self.success is True:
            return float(self.get('Packet', 'TIME_OFFSET_ALLOWED'))
        else:
            return 1.0

    @property
    def PACKET_SIZE(self):
        if self.success is True:
            return int(self.get('Packet', 'PACKET_SIZE'))
        else:
            return 1496

    @property
    def DIST_VECS(self):
        if self.success is True:
            return int(self.get('Packet', 'DIST_VECS'))
        else:
            return 360

    @property
    def MAX_DISTANCE(self):
        if self.success is True:
            return float(self.get('Webot', 'MAX_DISTANCE'))
        else:
            return 100


class WebotState(object):
    def __init__(self):
        self.gps_target = None
        self.gps_actual = None
        self.compass = None
        self.distance = None
        self.touching = None

    def fill_from_buffer(self, buffer, DIST_VECS):
        self.gps_target = struct.unpack('3f', buffer[16:28])
        self.gps_actual = struct.unpack('3f', buffer[28:40])
        self.compass = struct.unpack('3f', buffer[40:52])
        self.distance = struct.unpack("{}f".format(DIST_VECS), buffer[52:(52 + DIST_VECS * 4)])
        self.touching = struct.unpack("I", buffer[(52 + DIST_VECS * 4):(56 + DIST_VECS * 4)])[0]
        self._to_array()

    def _to_array(self):
        for v in self.__dict__.values():
            v = np.array(v)

    def get(self):
        arr = np.empty(0)
        for v in self.__dict__.values():
            arr = np.hstack((arr, v))
        return arr

    def describe(self):
        strr = "[0, 1]: "

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
        self.conf = Config()
        self.msg_cnt_in = 0
        self.msg_cnt_out = 1
        self.latency = None
        self.state = WebotState()
        self.packet = Packet()
        self.history = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.conf.IP, self.conf.BACKEND_PORT))
        self.recv()

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    def recv(self):
        t1 = time.time()
        self.packet.buffer, addr = self.sock.recvfrom(self.conf.PACKET_SIZE)
        self.latency = t1 - time.time()

        self._update_history()
        self.msg_cnt_in += 2

        if self.conf.PACKET_SIZE < len(self.packet.buffer):
            self.packet.error = PacketError.SIZE
            print("ERROR: recv did not get full packet", len(self.packet.buffer))
            return

        if self.conf.IP != addr[0]:
            self.packet.error = PacketError.IP
            print("ERROR: recv did from wrong address", addr)
            return

        # if self.packet.count != self.msg_cnt_in:
        #     self.packet.error = PacketError.COUNT
        #     print("ERROR: recv wrong msg count, is ", self.packet.count, " should ", self.msg_cnt_in)
        #     self.msg_cnt_in = self.packet.count
        #     return

        if abs(time.time() - self.packet.time) > self.conf.TIME_OFFSET_ALLOWED:
            self.packet.error = PacketError.TIME
            print("ERROR: recv time diff to big local ", time.time()," remote ",
                  self.packet.time, " diff ", abs(time.time() - self.packet.time))
            return

        self.state.fill_from_buffer(self.packet.buffer, self.conf.DIST_VECS)
        return self.state

    def send(self, action:WebotAction):
        data = struct.pack('Qdff', self.msg_cnt_out, time.time(),
                           action.heading, action.speed)
        ret = self.sock.sendto(data, (self.conf.IP, self.conf.CONTROL_PORT))
        if ret == len(data):
            self.msg_cnt_out += 2
        else:
            print("ERROR: could not send message, is ", ret, " should ", len(data))
