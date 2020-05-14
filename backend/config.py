class WebotConfig(object):

    def __init__(self):
        self.IP = "127.0.0.1"
        self.CONTROL_PORT = 6969
        self.BACKEND_PORT = 6970
        self.PACKET_SIZE = 1496
        self.DIST_VECS = 360
        self.TIME_OFFSET_ALLOWED = 1.0
        self.MAX_DISTANCE = 100