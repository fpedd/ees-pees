class WebotConfig(object):

    def __init__(self):
        # network
        self.IP = "127.0.0.1"
        self.CONTROL_PORT = 6969
        self.BACKEND_PORT = 6970
        self.PACKET_SIZE = 1496
        self.TIME_OFFSET_ALLOWED = 1.0

        # environment, sensor and robot
        self.DIST_VECS = 360
        self.length = 10
        self.lidar_min = 0.12
        self.lidar_max = 3.5
