import numpy as np


class FakeState():
    def __init__(self, env):
        self.gps_actual = None
        self.gps_target = None
        self.distance = None
        self.touching = 0

    def _update(self, env):
        self.gps_actual = env.state_object.gps_actual
        self.gps_target = env.state_object.gps_target
        self.distance = env.state_object.distance
        self.touching = env.state_object.touching

    def shape(self):
        return (9, )

    def get(self, env):
        """Get observation as numpy array."""
        self._update(env)
        arr = np.empty(0)
        arr = np.hstack((arr, np.array(self.gps_actual)))
        arr = np.hstack((arr, np.array(self.gps_target)))
        arr = np.hstack((arr, np.array(self.distance)))
        arr = np.hstack((arr, np.array(self.touching)))
        return arr
