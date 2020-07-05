import subprocess
import socket
import struct
import time
from enum import IntEnum
import psutil
import os

from webotsgym.config import WebotConfig, SimSpeedMode
import webotsgym.utils as utils


def get_repo_dir():
    """Get directory of ees-pees."""
    p = os.path.abspath('..')
    home_dir = p.split("/ees-pees")[0]
    repo_dir = os.path.join(home_dir, "ees-pees")
    return repo_dir


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
