class WebotConfig(object):

    def __init__(self):
        # ----------------------------------------------------------------------
        # external controller protocol
        self.IP = "127.0.0.1"
        self.CONTROL_PORT = 6969
        self.BACKEND_PORT = 6970
        self.PACKET_SIZE = 1480
        self.TIME_OFFSET_ALLOWED = 1.0

        self.DIST_VECS = 360

        # ----------------------------------------------------------------------
        # supervisor communication protocol
        self.IP_S = "127.0.0.1"
        self.PORT_S = 10201
        self.PACKET_SIZE_S = 16

        # settable for environment start via supervisor
        self.fast_simulation = False
        self.num_obstacles = 10
        self.world_size = 10
        self.seed = None

        # (received) world metadata
		self.gps_target = None
        self.sim_time_step = 32  # ms

    def print(self):
        for (k, v) in self.__dict__.items():
            print(str(k) + "\t" + str(v))
