import numpy as np

import communicate
import utils


WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class FakeState(communicate.WebotState):
    def __init__(self):
        self.gps_actual = None
        self.gps_target = None
        self.distance = None
        self.touching = 0


class FakeCom():
    def __init__(self, seeds, N=100, num_of_sensors=4, obstacles_each=4):
        self.seeds = seeds
        self.next_seed_idx = 1
        self.inits = (N, num_of_sensors, obstacles_each)
        self.N = N
        self.offset = int(2 * N)
        self.num_of_sensors = num_of_sensors
        self._init(N, obstacles_each)

    def _init(self, N, obstacles_each):
        self.state = FakeState()
        self._setup_fields()

        # place obstacles randomly (horizontal and vertical walls)
        self.place_random_obstacle(dx=1, dy=int(N / 3), N=obstacles_each)
        self.place_random_obstacle(int(N / 3), 1, N=obstacles_each)

        # random start and finish positions
        self.state.gps_actual = self.random_position()
        self.state.gps_target = self.random_position()

        # init distance sensoring
        self.distance_sensor()

        # reset seed to something random
        utils.set_random_seed()

    def reset(self):
        N, num_of_sensors, obstacles_each = self.inits
        self.next_seed_idx = 1
        self._init(N, obstacles_each)

    # #########################################################################
    # ###############################   SETUP   ###############################
    # #########################################################################
    def _setup_fields(self):
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)
        # set up walls
        self.field[0:WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL

    # #########################################################################
    # ######################   RANDOM OBJECT PLACEMENT   ######################
    # #########################################################################
    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    def random_grid_int(self):
        seed = self.get_next_seed()
        np.random.seed(seed)
        random_grid_int = np.random.randint(self.N)
        return random_grid_int

    def random_position(self):
        """Get a random x,y pair."""
        x = self.random_grid_int()
        y = self.random_grid_int()
        if self.field[x, y] > 0:
            x, y = self.random_position()
        return (x, y)

    def add_obstacle(self, x1x2y1y2):
        x1, x2, y1, y2 = x1x2y1y2
        self.field[x1:x2, y1:y2] = VAL_OBSTACLE

    def place_random_obstacle(self, dx, dy, N=1):
        if N == 1:
            x, y = self.random_position()
            xmax = min(x + dx, self.N - 1)
            ymax = min(y + dy, self.N - 1)
            self.add_obstacle((x, xmax, y, ymax))
        else:
            for _ in range(N):
                self.place_random_obstacle(dx, dy)

    # #########################################################################
    # #########################   DISTANCE SENSORS   ##########################
    # #########################################################################
    def pts_to_anchor(self, anchor, filterout=True):
        """Finds all points on grid (x,y) from current gps to anchor point.

        Used to move the robot into specified direction.
        """
        pts = []
        line = utils.get_line(self.pos_outer, anchor)
        for i, p in enumerate(line):
            if (self.inner[0] <= p[0] <= self.inner[1]) and \
               (self.inner[0] <= p[1] <= self.inner[1]):
                p = self.pt2inner(p)
                x, y = p
                if filterout is True and i > 0 and self.field[x, y] > 0:
                    return pts, utils.euklidian_distance(self.state.gps_actual, p)
                pts.append(p)
        return pts, utils.euklidian_distance(self.state.gps_actual, p)

    def distance_sensor(self):
        """Calculate distance to obstacles in all directions.

        Starts at 0 degrees and moves clockwise. The number and angle of
        directions is specified by num_of_sensors.
        """
        N = self.N
        pos = self.state.gps_actual
        endpoints = [(0, 0), (N - 1, 0), (0, N - 1), (N - 1, N - 1)]
        radius = round(max([utils.euklidian_distance(pos, ep) for
                            ep in endpoints]))
        phi = np.linspace(0, 2 * np.pi, self.num_of_sensors + 1)[:-1]
        pos = self.pos_outer
        y = (radius * np.cos(phi)).astype(int) + pos[1]
        x = (radius * np.sin(phi)).astype(int) + pos[0]
        anchors = list(zip(x, y))
        distances = []
        self.anchors = anchors
        for anch in anchors:
            distances.append(self.pts_to_anchor(anch)[1] - 1)
        self.state.distance = distances
        return anchors, distances

    # #########################################################################
    # #############################   SEND/RECV   #############################
    # #########################################################################
    def send(self, action):
        """Pretend to send action to external controller."""
        self.distance_sensor()

        # if isinstance(action, tuple) is False or\
        #    isinstance(action[0], int) is False or\
        #    isinstance(action[1], int) is False:
        #     raise TypeError("Action must be of a tuple of 2 integers.")
        orientation_idx, action_length = action

        pts_on_line = self.pts_to_anchor(self.anchors[orientation_idx],
                                         filterout=False)[0]
        self.pt = pts_on_line
        self.state.touching = False
        safept = self.state.gps_actual
        for i, pt in enumerate(pts_on_line):
            # too far away
            if utils.euklidian_distance(self.state.gps_actual, pt) > action_length:
                break
            # crash
            elif self.field[pt[0], pt[1]] > 0:
                self.state.touching = True
                break
            else:
                safept = pt
        self.state.gps_actual = safept
        self.distance_sensor()

    def recv(self):
        """Fake for consistency."""
        pass

    # #########################################################################
    # ###############################   HELPER  ###############################
    # #########################################################################
    def pt2outer(self, pt):
        """Convert position from inner to outer grid."""
        return (pt[0] + self.offset, pt[1] + self.offset)

    def pt2inner(self, pt):
        """Convert position from inner to outer grid."""
        return (pt[0] - self.offset, pt[1] - self.offset)

    @property
    def total_len(self):
        return self.N + 2 * self.offset

    @property
    def pos_outer(self):
        """Convert current gps in outer grid."""
        return self.pt2outer(self.state.gps_actual)
