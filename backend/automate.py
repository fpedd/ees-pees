import subprocess
import socket
import struct
import time
import numpy as np
from enum import Enum
import psutil

import config

# class WebotConfig():
#     """NO need fuer aktion, fuell ich selber."""
#     def __init__(self):
#         pass

class FunctionCode(Enum):
    UNDEFINED = -1
    NONE = 0
    START = 1
    RESET = 2
    CLOSE = 3


class ReturnCode(Enum):
    UNDEFINED = -1
    NONE = 0

class WebotCtrl():
    def __init__(self):
        self.sock = None
        self.return_code = ReturnCode.NONE
        self.lidar_min_range = -1.0
        self.lidar_max_range = -1.0
        self.sim_time_step = 0

        # config of webots internal controller (normal robot operations)
        self.w_config = config.WebotConfig()
        # config of webots supervisor controller (automated operations)
        self.s_config = config.SupervisorConfig()

    def init(self):
        # nothing to do here
        self.compile_program()
        self.start_program()
        time.sleep(5.0)
        self.establish_connection()

    def close(self):
        # nothing to do here
        self.close_connection()
        self.close_program()

    def is_program_started(self):
        # check if there is a process with the name "webots-bin" running
        return "webots-bin" in (p.name() for p in psutil.process_iter())

    def compile_program(self):
        self.close_program()
        # clean both controllers in webots
        subprocess.call(["make", "clean"], cwd="../webots/controllers/supervisor")
        subprocess.call(["make", "clean"], cwd="../webots/controllers/internal")
        # compile both controllers in webots
        subprocess.call(["make", "all"], cwd="../webots/controllers/supervisor")
        subprocess.call(["make", "all"], cwd="../webots/controllers/internal")

    def start_program(self):
        if self.is_program_started() is False:
            # start webots with the path of the world as argument
            subprocess.Popen(["webots", "../webots/worlds/testworld_prototype.wbt"])

    def close_program(self):
        if self.is_program_started() is True:
            # kill webots process
            subprocess.call(["pkill", "webots-bin"])

    def establish_connection(self):
        # start tcp connection to Webot Supervisor
        if self.sock is not None:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # reuse socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set buffer size to packet size to store only latest package
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,
                             self.s_config.PACKET_SIZE)
        return self.sock.connect((self.s_config.IP, self.s_config.PORT))

    def close_connection(self):
        # close tcp connection to webot supervisor
        self.sock.close()

    def start_env(self, seed=1, fast_simulation=False, num_obstacles=10, world_size=10):
        data = struct.pack('iiiii',
                           FunctionCode.START,
                           seed,
                           int(fast_simulation),
                           num_obstacles,
                           world_size)
        self.sock.send(data)

    def get_metadata(self):
        buffer = self.sock.recv(self.s_conf.PACKET_SIZE)
        self.return_code = struct.unpack('i', buffer[0:3])[0]
        self.lidar_min_range = struct.unpack('f', buffer[4:7])[0]
        self.lidar_max_range = struct.unpack('f', buffer[8:11])[0]
        self.sim_time_step = struct.unpack('i', buffer[12:15])[0]

    def reset_environment(self):
        # environment sollte sein wie beim start der simulation
        data = struct.pack('iiiii', FunctionCode.RESET, 0, 0, 0, 0)
        self.sock.send(data)

    def close_environment(self):
        # evlt notwendig, eher nicht
        data = struct.pack('iiiii', FunctionCode.CLOSE, 0, 0, 0, 0)
        self.sock.send(data)

    def print(self):
        print("===== WebotCtrl =====")
        print("return_code", self.return_code)
        print("lidar_min_range", self.lidar_min_range)
        print("lidar_max_range", self.lidar_max_range)
        print("sim_time_step", self.sim_time_step)
        print("=====================")


class ExtCtrl():
    def compile(self):
        self.close()
        subprocess.call(["make", "clean"], cwd="../controller")
        subprocess.call(["make", "all"], cwd="../controller")

    def start(self):
        subprocess.Popen(["../controller/build/controller"])

    def close(self):
        subprocess.call(["pkill", "controller"])
