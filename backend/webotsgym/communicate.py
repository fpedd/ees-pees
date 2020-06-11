import socket
import struct
import time
from enum import Enum

from webotsgym.config import WebotConfig
from webotsgym.webot import WebotState, WebotAction


# =========================================================================
# ==========================   INCOMING PACKET   ==========================
# =========================================================================
class PacketError(Enum):
    UNITILIZED = -1
    NO_ERROR = 0
    SIZE = 1
    IP = 2
    COUNT = 3
    TIME = 4


class Packet(object):
    def __init__(self, config: WebotConfig = WebotConfig()):
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


# =========================================================================
# ==========================   OUTGOING PACKET   ==========================
# =========================================================================
class PacketType(Enum):
    COM = 1
    REQ = 2
    COM_REQ = 3


class DirectionType(Enum):
    STEERING = 0
    HEADING = 1


class OutgoingPacket():
    def __init__(self, msg_cnt, packet_type, direction_type,
                 action: WebotAction = WebotAction(action=(0, 0))):
        self.msg_cnt = msg_cnt
        self.time = time.time()
        if isinstance(packet_type, int):
            self.packet_type = packet_type
        else:
            self.packet_type = packet_type.value

        if isinstance(direction_type, int):
            self.direction_type = direction_type
        else:
            self.direction_type = direction_type.value

        self.action = action

    def pack(self):
        data = struct.pack('Qdiff',
                           self.msg_cnt,
                           time.time(),
                           self.packet_type,
                           self.action.heading,
                           self.action.speed)
        return data


# =========================================================================
# ==========================    COMMUNICATION    ==========================
# =========================================================================
class Com(object):
    def __init__(self, gps_target, config: WebotConfig = WebotConfig()):
        self.config = config
        self.msg_cnt_in = 0
        self.msg_cnt_out = 1
        self.latency = None
        self.state = WebotState(gps_target, config)
        self.packet = Packet(config)
        self.history = []
        self._set_sock()
        if config.direction_type == "steering":
            self.dir_type = DirectionType.STEERING
        else:
            self.dir_type = DirectionType.HEADING

        if config.fast_simulation is True:
            print("USE FAST MODE")

    # ------------------------------  SETUPS  ---------------------------------
    def _set_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.config.IP, self.config.BACKEND_PORT))

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    def recv(self):
        self.packet.buffer, addr = self.sock.recvfrom(self.config.PACKET_SIZE)
        self.state.fill_from_buffer(self.packet.buffer)

    # -------------------------------  SEND -----------------------------------
    def send(self, pack_out):
        data = pack_out.pack()
        ret = self.sock.sendto(data, (self.config.IP,
                                      self.config.CONTROL_PORT))
        if ret == len(data):
            self.msg_cnt_out += 2
        else:
            print("ERROR: could not send message, is ", ret, " should ",
                  len(data))

    def send_data_request(self):
        pack_out = OutgoingPacket(self.msg_cnt_out, PacketType.REQ,
                                  self.dir_type)
        self.send(pack_out)
        time.sleep(self.wait_time)
        self.recv()

    def send_command(self, action):
        pack_out = OutgoingPacket(self.msg_cnt_out, PacketType.COM,
                                  self.dir_type, action)
        self.send(pack_out)

    def send_command_and_data_request(self, action):
        pack_out = OutgoingPacket(self.msg_cnt_out, PacketType.COM_REQ,
                                  self.dir_type, action)
        self.send(pack_out)
        self.recv()

    @property
    def wait_time(self):
        divider = 1
        if self.config.fast_simulation is True:
            divider = 3
        return self.config.send_wait_time / 1000 / divider

# if PACKET_SIZE < len(self.packet.buffer):
#     print("ERROR: recv did not get full packet", len(self.packet.buffer))
#     return
#
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
