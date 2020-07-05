import numpy as np


class FakeState():
    def __init__(self, env):
        self.gps_actual = None
        self.gps_target = None
        self.distance = None
        self.touching = None

    def shape(self):
        return (9, )

    def get(self, env):
        """Get observation as numpy array."""
        self._update(env)
        arr = np.empty(0)
        for k, v in self.__dict__.items():
            if k != "env":
                arr = np.hstack((arr, np.array(v)))
        return arr
