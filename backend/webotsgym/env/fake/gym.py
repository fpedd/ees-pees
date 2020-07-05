from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import copy
import gym
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from webotsgym.env.fake import FakeState, FakeAction
from webtosenv.env.util import get_line
import webotsgum.utils as utils

WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class WbtGymFake(env.Env):
    def __init__(self, seed=None, N=10, num_of_sensors=4, obstacles_each=4, step_range=(1, 1), obs=FakeState, obs_len=1):
        super(WbtGymFake, self).__init__()

        self.history = {}

        self.action_mapper = FakeAction(4, step_range)

        self.seed(seed)
        self.reward_range = (-100, 100)
        self.action_mapping = self.action_mapper.action_map
        self.action_space = self.action_mapper.action_space

        self.com_inits = (N, num_of_sensors, obstacles_each, obs_len)
        self.com = FakeCom(self.seeds, self.com_inits[0], self.com_inits[1],
                           self.com_inits[2], self.com_inits[3])
        self.plotpadding = 0
        self.visited_count = np.zeros(self.com.field.shape)

        if type(obs) == type:
            self.obs = (obs)(self)
        else:
            self.obs = obs
        self.observation_space = spaces.Box(0, np.inf, shape=self.obs.shape(),
                                            dtype=np.float32)

        self.total_reward = 0

    def seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        if seed is None:
            seed = np.random.randint(0, 10**6, 1)
        self.seeds = [seed]
        np.random.seed(seed)
        self.seeds.extend(list(set(np.random.randint(0, 10**6, 1000))))

    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])

    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        action = self.action_mapping(action)
        self.com.send(action)
        self.visited_count[self.gps_actual] += 1
        reward = self.calc_reward()
        self.total_reward += reward
        done = self.check_done()
        self.history[self.com.time_steps] = copy.deepcopy(self.state_object)
        self.com.time_steps += 1
        return self.state, reward, done, {}

    def close(self):
        pass

    def get_target_distance(self, normalized=False):
        """Calculate euklidian distance to target."""
        dist = utils.euklidian_distance(self.gps_actual, self.gps_target)
        if normalized is True:
            dist = dist / self.max_distance
        return dist

    def check_done(self):
        if self.com.time_steps == 1000:
            return True
        if self.gps_actual == self.gps_target:
            return True
        return False

    @property
    def max_distance(self):
        return np.sqrt(2) * self.com.N

    @property
    def state(self):
        return self.obs.get(self)

    @property
    def state_object(self):
        return self.com.state

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def gps_visited_count(self):
        return self.visited_count[self.gps_actual]

    @property
    def gps_target(self):
        return self.com.state.gps_target

    def calc_reward(self):
        """Calculate reward function."""
        if self.gps_actual == self.gps_target:
            reward = 1000
        else:
            epsilon = 10**-5
            cost_step = 1
            distance = self.get_target_distance() + epsilon
            cost_distance = (distance**0.4) / (distance)
            reward_factor = -1
            reward = reward_factor * (cost_step * cost_distance)
            if self.state_object:
                reward = reward - 10
        return reward

    def reset(self, seed=None, hard=True, min_complexity=1):
        self.total_reward = 0
        if seed is None:
            seed = utils.np_random_seed(set=False)
        self.seed(seed)
        self.com = FakeCom(self.seeds, self.com_inits[0], self.com_inits[1],
                           self.com_inits[2], self.com_inits[3])
        self.visited_count = np.zeros(self.com.field.shape)
        if hard is True and len(self.finder_path()) < min_complexity:
            seed = utils.np_random_seed(set=False)
            # print("No path available or too simple, reset with seed: ", seed)
            self.reset(seed)
        return self.state

    def render(self):
        plt.figure(figsize=(10, 10))
        f = self.com.field.copy()
        rx, ry = self.gps_actual
        tx, ty = self.gps_target
        s = self.plotpadding
        r_minx = max(0, (rx - s))
        r_maxx = min(rx + s + 1, self.com.N)
        r_miny = max(0, (ry - s))
        r_maxy = min(ry + s + 1, self.com.N)

        t_minx = max(0, (tx - s))
        t_maxx = min(tx + s + 1, self.com.N)
        t_miny = max(0, (ty - s))
        t_maxy = min(ty + s + 1, self.com.N)

        f[t_minx:t_maxx, t_miny:t_maxy] = VAL_TARGET
        f[r_minx:r_maxx, r_miny:r_maxy] = VAL_ROBBIE
        plt.matshow(f)
        return

    @property
    def field(self):
        return self.com.field

    def finder_path(self, finder=AStarFinder):
        grid = self.field.copy()
        grid[grid > 0] = 99
        grid[grid == 0] = 1
        grid[grid == 99] = 0
        grid = grid.astype(int)
        grid = grid.tolist()
        grid = Grid(matrix=grid)

        # find path
        sx, sy = self.gps_actual
        tx, ty = self.gps_target
        start = grid.node(sy, sx)
        end = grid.node(ty, tx)
        finder = finder()
        path, _ = finder.find_path(start, end, grid)

        return path

    def average_solvability(self, test_cases=1000):
        """Check how many environmnents with current settings are solvable."""
        solves = 0
        for _ in range(test_cases):
            self.reset(hard=False)
            if self.is_path():
                solves += 1
        return solves / test_cases



class FakeCom():
    def __init__(self, seeds, N=10, num_of_sensors=4, obstacles_each=2,
                 obs_len=1):
        self.seeds = seeds
        self.next_seed_idx = 1
        self.inits = (N, num_of_sensors, obstacles_each, obs_len)
        self.N = N
        self.offset = int(2 * N)
        self.num_of_sensors = num_of_sensors
        self.obs_len = obs_len
        self._init(N, obstacles_each, obs_len)
        self.time_steps = 0

    def _init(self, N, obstacles_each, obs_len):
        self.state = FakeState()
        self._setup_fields()

        # place obstacles randomly (horizontal and vertical walls)
        self.place_random_obstacle(dx=1, dy=obs_len, N=obstacles_each)
        self.place_random_obstacle(obs_len, 1, N=obstacles_each)

        # random start and finish positions
        self.state.gps_actual = self.random_position()
        self.state.gps_target = self.random_position()

        # init distance sensoring
        self.distance_sensor()

        # reset seed to something random
        utils.np_random_seed()

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
        line = get_line(self.pos_outer, anchor)
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

        pts_on_line = self.pts_to_anchor(self.anchors[::int(self.num_of_sensors/4)][orientation_idx],
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
