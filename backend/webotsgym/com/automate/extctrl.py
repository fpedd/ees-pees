import subprocess
import os

from webotsgym.comm.automate import get_repo_dir


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
