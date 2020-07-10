import socket
import time

from webotsgym.config import WbtConfig, DiscreteMove
from webotsgym.com import PacketIn, PacketOut, WbtState, PacketType


class Communication():
    def __init__(self, config: WbtConfig = WbtConfig()):
        self.config = config
        self.msg_cnt = 0
        self.packet = None
        self.history = []
        self._set_sock()

    # ------------------------------  SETUPS  ---------------------------------
    def _set_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.config.IP, self.config.BACKEND_PORT))

    def _update_history(self):
        self.history.append([self.packet.time, self.packet])

    # -------------------------------  RECV -----------------------------------
    def recv(self):
        """Receive package (blocking) from external controller."""
        buffer, addr = self.sock.recvfrom(self.config.PACKET_SIZE)
        self.packet = PacketIn(self.config, buffer)
        if self.packet.count != self.msg_cnt:
            print("ERROR: recv msg count, is ", self.packet.count, " should ",
                  self.msg_cnt)
            self.msg_cnt = self.packet.count

        self.msg_cnt += 1
        self.state = WbtState(self.config, self.packet)

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
        """Send request for current webots data to external controller."""
        pack_out = PacketOut(self.msg_cnt, 0, PacketType.REQ,
                             DiscreteMove.NONE, self.config.direction_type)
        self.send(pack_out)

    def get_data(self):
        """Send data request to external controller and receive response."""
        self.send_data_request()
        self.recv()

    def send_command(self, action):
        """Send command only to external controller."""
        pack_out = PacketOut(self.msg_cnt, 0, PacketType.COM,
                             DiscreteMove.NONE, self.config.direction_type,
                             action)
        self.send(pack_out)

    def send_command_and_data_request(self, action):
        """Send action to external controller and get current state.

        Main communication method. External controller will respond with new
        data after (sim_step_every_x * 32) webots-ms."""
        pack_out = PacketOut(self.msg_cnt, self.config.sim_step_every_x,
                             PacketType.COM_REQ, DiscreteMove.NONE,
                             self.config.direction_type, action)
        self.send(pack_out)
        self.recv()

    # ------------------------------- GRID MOVES ------------------------------
    def send_grid_move(self, move):
        """Send grid move to external controller.

        Used for grid communication and WbtGymGrid."""
        pack_out = PacketOut(self.msg_cnt, 0, PacketType.COM, move, 0)
        self.send(pack_out)

    def _wait_for_grid_done(self, wait_time=0.01):
        # give controller some time to update internal data
        time.sleep(wait_time)
        self.get_data()
        while self.state.discrete_action_done != 1:
            self.get_data()
            time.sleep(wait_time)

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
