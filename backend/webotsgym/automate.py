import subprocess
import socket
import struct
import time
import numpy as np
from enum import IntEnum
import psutil
import os

from webotsgym.config import WebotConfig
import webotsgym.utils as utils


def get_repo_dir():
    """Get directory of ees-pees."""
    p = os.path.abspath('..')
    home_dir = p.split("/ees-pees")[0]
    repo_dir = os.path.join(home_dir, "ees-pees")
    return repo_dir


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


# =========================================================================
# ========================        SUPERVISOR       ========================
# =========================================================================
class WebotCtrl():
    def __init__(self, config: WebotConfig = WebotConfig()):
        self.config = config
        self.sock = None
        self.client_sock = None
        self.address = None
        self.return_code = ReturnCode.SUCCESS
        self.extr_ctrl = ExtCtrl()

    def init(self):
        """Init webots, environment and external controller."""
        self.compile_program()
        self.start_program()
        self.establish_connection()
        self.extr_ctrl.init()

    def close(self):
        """Close webots environment."""
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
                "webots/worlds/training_env.wbt")])

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

    def start_env(self, seed=None, waiting_time=1):
        """Start environment with seed and config info."""
        self.extr_ctrl.reset()
        if seed is None:
            seed = utils.set_random_seed()
        data = struct.pack('iiiiif',
                           FunctionCode.START,
                           seed,
                           int(self.config.fast_simulation),
                           self.config.num_obstacles,
                           self.config.world_size,
                           self.config.world_scaling)
        print("sending: env")
        self.client_sock.send(data)
        time.sleep(waiting_time)
        self.get_metadata()

        time.sleep(self.config.wait_env_creation)

    def get_metadata(self):
        """Get current environment metadata."""
        buffer = self.client_sock.recv(self.config.PACKET_SIZE_S)
        self.return_code = struct.unpack('i', buffer[0:4])[0]
        self.config.sim_time_step = struct.unpack('i', buffer[4:8])[0]
        self.config.gps_target = struct.unpack('2f', buffer[8:16])

    def reset_environment(self, seed=None, waiting_time=1):
        """Reset environment with seed."""
        self.extr_ctrl.reset()
        if seed is None:
            seed = utils.set_random_seed()
        # environment sollte sein wie beim start der simulation
        data = struct.pack('iiiiif', FunctionCode.RESET, seed, 0, 0, 0, 0.0)
        print("sending: reset")
        self.client_sock.send(data)
        time.sleep(waiting_time)
        self.get_metadata()

        time.sleep(self.config.wait_env_reset)

    def close_environment(self):
        """Close environment."""
        # environment sollte sein wie beim start der simulation
        data = struct.pack('iiiiif', FunctionCode.CLOSE, 0, 0, 0, 0, 0.0)
        print("sending: close")
        self.client_sock.send(data)

    def print(self):
        print("===== WebotCtrl =====")
        print("return_code", self.return_code)
        print("target", self.config.gps_target[0], self.config.gps_target[1])
        print("sim_time_step", self.config.sim_time_step)
        print("=====================")


# =========================================================================
# =====================       EXTERNAL CONTROLLER       ===================
# =========================================================================
class ExtCtrl():
    def init(self):
        self.compile()
        self.start()

    def reset(self):
        """Reset external controller."""
        self.close()
        self.init()

    def compile(self):
        """Compile external controller."""
        self.close()
        subprocess.call(["make", "clean"], cwd=os.path.join(get_repo_dir(),
                                                            "controller"))
        subprocess.call(["make", "all"], cwd=os.path.join(get_repo_dir(),
                                                          "controller"))

    def start(self):
        """Start external controller."""
        subprocess.Popen([os.path.join(get_repo_dir(),
                                       "controller/build/controller")])

    def close(self):
        """Kill process of external controller."""
        subprocess.call(["pkill", "controller"])
