import subprocess
import socket
import struct
import time
from enum import IntEnum
import psutil
import os

from webotsgym.config import WebotConfig
import webotsgym.utils as utils
from webotsgym.comm.automate import get_repo_dir
from webotsgym.comm.automate import ExtCtrl


class FunctionCode(IntEnum):
    UNDEFINED = -1
    NO_FUNCTION = 0
    START = 1
    RESET = 2
    CLOSE = 3


class ReturnCode(IntEnum):
    UNDEFINED = -1
    SUCCESS = 0
    ERROR = 1


class WbtCtrl():
    def __init__(self, config: WebotConfig = WebotConfig()):
        self.config = config
        self.sock = None
        self.client_sock = None
        self.address = None
        self.return_code = ReturnCode.SUCCESS
        self.extr_ctrl = ExtCtrl()

    def init(self):
        """Init webots, gymironment and external controller."""
        self.compile_program()
        self.start_program()
        self.establish_connection()
        self.extr_ctrl.init()

    def close(self):
        """Close webots gymironment."""
        self.close_connection()
        self.close_program()
        self.extr_ctrl.close()

    def is_program_started(self):
        """Check if there is a process with the name "webots-bin" running."""
        return "webots-bin" in (p.name() for p in psutil.process_iter())

    def compile_program(self):
        """Complile controllers."""
        self.close_program()
        # clean both controllers in webots
        subprocess.call(["make", "clean"], cwd=os.path.join(get_repo_dir(),
            "webots/controllers/supervisor"))
        subprocess.call(["make", "clean"], cwd=os.path.join(get_repo_dir(),
            "webots/controllers/internal"))
        # compile both controllers in webots
        subprocess.call(["make", "all"], cwd=os.path.join(get_repo_dir(),
            "webots/controllers/supervisor"))
        subprocess.call(["make", "all"], cwd=os.path.join(get_repo_dir(),
            "webots/controllers/internal"))

    def start_program(self):
        """Open webots."""
        if self.is_program_started() is False:
            # start webots with the path of the world as argument
            subprocess.Popen(["webots", os.path.join(get_repo_dir(),
                "webots/worlds/training_gym.wbt")])

    def close_program(self):
        """Kill webots process."""
        if self.is_program_started() is True:
            # kill webots process
            subprocess.call(["pkill", "webots-bin"])

    def establish_connection(self):
        """Start tcp connection to Webot Supervisor."""
        if self.sock is not None:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.config.IP_S, self.config.PORT_S))
        self.sock.listen(5)
        print("Accepting on Port: ", self.config.PORT_S)
        (self.client_sock, self.address) = self.sock.accept()

    def close_connection(self):
        """Close tcp connection to webot supervisor."""
        self.sock.close()

    def start_gym(self, seed=None, waiting_time=1):
        """Start gymironment with seed and config info."""
        self.extr_ctrl.reset()
        if seed is None:
            seed = utils.set_random_seed()
        data = struct.pack('iiiiif',
                           FunctionCode.START,
                           seed,
                           int(self.config.sim_mode),
                           self.config.num_obstacles,
                           self.config.world_size,
                           self.config.world_scaling)
        print("sending: start gym", int(self.config.sim_mode))
        self.client_sock.send(data)
        time.sleep(waiting_time)
        self.get_metadata()

        time.sleep(self.config.wait_gym_creation)

    def get_metadata(self):
        """Get current gymironment metadata."""
        buffer = self.client_sock.recv(self.config.PACKET_SIZE_S)
        self.return_code = struct.unpack('i', buffer[0:4])[0]
        self.config.sim_time_step = struct.unpack('i', buffer[4:8])[0]
        self.config.gps_target = struct.unpack('2f', buffer[8:16])

    def reset_gymironment(self, seed=None, waiting_time=1):
        """Reset gymironment with seed."""
        self.extr_ctrl.reset()
        if seed is None:
            seed = utils.set_random_seed()
        # gymironment sollte sein wie beim start der simulation
        data = struct.pack('iiiiif', FunctionCode.RESET, seed, 0, 0, 0, 0.0)
        print("sending: reset")
        self.client_sock.send(data)
        time.sleep(waiting_time)
        self.get_metadata()

        time.sleep(self.config.wait_gym_reset)

    def close_gymironment(self):
        """Close gymironment."""
        # gymironment sollte sein wie beim start der simulation
        data = struct.pack('iiiiif', FunctionCode.CLOSE, 0, 0, 0, 0, 0.0)
        print("sending: close")
        self.client_sock.send(data)

    def print(self):
        print("===== WebotCtrl =====")
        print("return_code", self.return_code)
        print("target", self.config.gps_target[0], self.config.gps_target[1])
        print("sim_time_step", self.config.sim_time_step)
        print("=====================")