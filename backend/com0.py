import socket
import struct
import time

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
        # TODO return state as numpy array
        pass


class Packet(object):
    def __init__(self):
        self.buffer = None
        self.msg_cnt_in = 0
        self.time_in = None
        self.success = False

    @property
    def count(self):
        return struct.unpack('Q', self.buffer_in[0:8])[0]

    @property
    def time(self):
        return struct.unpack('d', self.buffer_in[8:16])[0]


class WebotAction(object):
    def __init__(self):
        self.heading = None
        self.speed = None


class Com(object):
    def __init__(self):
        self.state = WebotState()
        self.packet = Packet()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, BACKEND_PORT))

    def recv(self):
        self.packet.success = False
        self.packet.buffer_in, addr = sock.recvfrom(PACKET_SIZE)

        if PACKET_SIZE < len(self.packet.buffer_in):
            print("ERROR: recv did not get full packet", len(self.packet.buffer_in))
            return

        if IP != addr[0]:
            print("ERROR: recv did from wrong address", addr)
            return

        self.packet.msg_cnt_in += 2
        if self.packet.count != self.packet.msg_cnt_in:
            print("ERROR: recv wrong msg count, is ", self.packet.count, " should ", self.packet.msg_cnt_in)
            self.packet.msg_cnt_in = self.packet.count
            return

        if abs(time.time() - self.packet.time) > TIME_OFFSET_ALLOWED:
            print("ERROR: recv time diff to big local ", time.time()," remote ",
                  self.packet.time, " diff ", abs(time.time() - self.packet.time))
            return
        self.packet.success = True
        self.state.fill_from_buffer(self.state.buffer_in)

    def send(self, action:WebotAction):
        #TODO
        self.action.send()
        pass
