import subprocess
import os
import pathlib


FILE_PATH = pathlib.Path(__file__).parent.absolute()
HOME_PATH = str(pathlib.Path(FILE_PATH).parents[3])


class ExtCtrl():
    """Create class to communicate with external controller."""

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
        subprocess.call(["make", "clean"], cwd=os.path.join(HOME_PATH,
                                                            "controller"))
        subprocess.call(["make", "all"], cwd=os.path.join(HOME_PATH,
                                                          "controller"))

    def start(self):
        """Start external controller."""
        subprocess.Popen([os.path.join(HOME_PATH,
                                       "controller/build/controller")])

    def close(self):
        """Kill process of external controller."""
        subprocess.call(["pkill", "controller"])
