class WebotConfig(object):

    def __init__(self):
        # external controller protocol
        self.IP = "127.0.0.1"
        self.CONTROL_PORT = 6969
        self.BACKEND_PORT = 6970
        self.PACKET_SIZE = 1496
        self.TIME_OFFSET_ALLOWED = 1.0

        self.DIST_VECS = 360

        # supervisor communication protocol
        self.IP_S = "127.0.0.1"
        self.PORT_S = 10201
        self.PACKET_SIZE_S = 16

        self.seed = None
        self.length = 10
        self.world_size = 10
        self.lidar_min_range = 0.12
        self.lidar_max_range = 3.5
        self.sim_time_step = 32  # ms
        self.fast_simulation = False
        self.num_obstacles = 10
        self.world_size = 10
        self.target_x = 0.5
        self.target_y = 0.5
