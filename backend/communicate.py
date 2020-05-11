import socket
import struct
import time
import numpy as np

############## Settings ##############
IP = "127.0.0.1"
CONTROL_PORT = 6969
BACKEND_PORT = 6970
TIME_OFFSET_ALLOWED = 1.0  # in seconds
PACKET_SIZE = 1496   # (8 + 8 + 3*4 + 3*4 + 3*4 + DIST_VECS*4 + 4)
DIST_VECS = 360
sock = None


class WebotState(object):
    def __init__(self):
        self.gps_target = None
        self.gps_actual = None
        self.compass = None
        self.distance = None
        self.touching = None

    def fill_from_buffer(self, buffer):
        self.gps_target = struct.unpack('3f', buffer[16:28])
        self.gps_actual = struct.unpack('3f', buffer[28:40])
        self.compass = struct.unpack('3f', buffer[40:52])
        self.distance = struct.unpack("{}f".format(DIST_VECS), buffer[52:(52 + DIST_VECS * 4)])
        self.touching = struct.unpack("I", buffer[(52 + DIST_VECS * 4):(56 + DIST_VECS * 4)])[0]

    def get(self):
        arr = np.empty(0)
        for v in self.__dict__.values():
            arr = np.hstack((arr, np.array(v)))
        return arr


class Packet(object):
    def __init__(self):
        self.buffer = None
        self.time_in = None
        self.success = False

    @property
    def count(self):
        return struct.unpack('Q', self.buffer[0:8])[0]

    @property
    def time(self):
        return struct.unpack('d', self.buffer[8:16])[0]


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
        self.msg_cnt_in = 0
        self.msg_cnt_out = 1
        self.latency = None
        self.state = WebotState()
        self.packet = Packet()
        self.history = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((IP, BACKEND_PORT))
        self.recv()

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    def recv(self):
        self.packet.success = False

        t1 = time.time()
        self.packet.buffer, addr = self.sock.recvfrom(PACKET_SIZE)
        self.latency = t1 - time.time()

        self._update_history()
        self.msg_cnt_in += 2

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

        self.packet.success = True
        self.state.fill_from_buffer(self.packet.buffer)

    def send(self, action:WebotAction):
        data = struct.pack('Qdff', self.msg_cnt_out, time.time(),
                           action.heading, action.speed)
        ret = self.sock.sendto(data, (IP, CONTROL_PORT))
        if ret == len(data):
            self.msg_cnt_out += 2
        else:
            print("ERROR: could not send message, is ", ret, " should ", len(data))
