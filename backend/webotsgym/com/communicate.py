import socket
import time
import numpy as np

from webotsgym.config import WbtConfig, SimSpeedMode, DiscreteMove, DirectionType
from webotsgym.com import PacketIn, PacketOut, WbtState, PacketType  # noqa E501


class Communication():
    def __init__(self, config: WbtConfig = WbtConfig()):
        self.config = config
        self.msg_cnt = 0
        self.latency = None
        self.state = WbtState(config)
        self.packet = None
        self.history = []
        self._set_sock()

        if config.direction_type == "steering":
            self.dir_type = DirectionType.STEERING
        else:
            self.dir_type = DirectionType.HEADING

    # ------------------------------  SETUPS  ---------------------------------
    def _set_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.config.IP, self.config.BACKEND_PORT))

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    # -------------------------------  RECV -----------------------------------
    def recv(self):
        buffer, addr = self.sock.recvfrom(self.config.PACKET_SIZE)
        self.packet = PacketIn(self.config, buffer)
        if self.packet.count != self.msg_cnt:
            print("ERROR: recv msg count, is ", self.packet.count, " should ",
                  self.msg_cnt)
            self.msg_cnt = self.packet.count

        self.msg_cnt += 1
        self.state = WbtState(self.config, self.packet)

    # def recv(self):
    #     self._recv()
    #     if hasattr(self, "last_sim_time") is False:
    #         self.last_sim_time = self.packet.sim_time
    #     cnt = 0
    #     while True:
    #         time_diff = (self.packet.sim_time - self.last_sim_time) * 1
    #         if time_diff >= self.config.sim_time_wait / 1000:
    #             break
    #         self.send_data_request()
    #         self._recv()
    #         cnt += 1
    #     print("took     ", cnt)
    #     print("time_diff", time_diff)
    #     self.last_sim_time = self.packet.sim_time
    #
    #     self.state = WbtState(self.config, self.packet)

    # -------------------------------  SEND -----------------------------------
    def send(self, pack_out):
        """Send packet to external controller, increment message count."""
        data = pack_out.pack()
        ret = self.sock.sendto(data, (self.config.IP,
                                      self.config.CONTROL_PORT))
        if ret != len(data):
            print("ERROR: send message, is ", ret, " should ", len(data))
            return

        self.msg_cnt += 1

    def send_data_request(self):
        pack_out = PacketOut(self.msg_cnt, PacketType.REQ, DiscreteMove.NONE, self.dir_type)
        self.send(pack_out)

    def get_data(self):
        self.send_data_request()
        self.recv()

    def send_command(self, action):
        pack_out = PacketOut(self.msg_cnt, PacketType.COM, DiscreteMove.NONE, self.dir_type, action)
        self.send(pack_out)

    def send_command_and_data_request(self, action):
        pack_out = PacketOut(self.msg_cnt, PacketType.COM_REQ, DiscreteMove.NONE, self.dir_type, action)
        self.send(pack_out)
        # time.sleep(self.wait_time)
        self.recv()

    def send_discrete_move(self, move):
        # TODO: incorporate wait for execution -> PacketType.COM_REQ
        pack_out = PacketOut(self.msg_cnt, PacketType.COM, move, 0)
        self.send(pack_out)

    def _wait_for_discrete_done(self, wait_time=0.01):
        # give controller some time to update internal data
        time.sleep(wait_time)
        self.get_data()
        while self.state.discrete_action_done != 1:
            self.get_data()
            time.sleep(wait_time)

    @property
    def wait_time(self):
        divider = 1
        if not (self.config.sim_mode is SimSpeedMode.NORMAL):
            divider = 3
        return self.config.send_recv_wait_time / 1000 / divider
