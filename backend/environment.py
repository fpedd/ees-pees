import numpy as np
import matplotlib.pyplot as plt
import communicate
import utils
import abc

import gym
from gym import spaces


class MyGym(gym.Env):
    def __init__(self, seed):
        super(MyGym, self).__init__()
        self.seeds = self.seed(seed)
        self.reward_range = (-100, 100)

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def step(self):
        pass

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    def seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        if seed is None:
            seed = np.random.randint(0, 10**6, 1)
        seeds = [seed]
        np.random.seed(seed)
        seeds.extend(list(set(np.random.randint(0, 10**6, 1000))))
        return seeds

    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])


def no_mapping(self, action):
    return action


class WebotsBlue(MyGym):
    def __init__(self, seed, action_mapping=no_mapping):
        super(WebotsBlue, self).__init__(seed=seed)
        self.action_mapping = action_mapping

    def reset(self):
        self.com.reset()
        return self.state

    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        action = self.action_mapping(action)
        self.com.send(action)
        self.com.recv()
        reward = self.calc_reward()
        done = self.check_done()
        return self.state, reward, done, {}

    def close(self):
        pass

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    def calc_reward(self):
        return np.random.random()

    def check_done(self):
        if self.gps_actual == self.gps_target:
            return True
        return False

    @property
    def state(self):
        return self.com.state.get()

    @property
    def state_object(self):
        return self.com.state

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def gps_target(self):
        return self.com.state.gps_target


class ActionMapper(object):
    def __init__(self):
        self.action_space = None

    def action_map(self, action):
        return action


class DiscreteAction(ActionMapper):
    def __init__(self, num_of_directions, step_range, mode):
        super(DiscreteAction, self).__init__()
        self.num_of_directions = num_of_directions
        self.step_range = step_range
        self.steps = step_range[1] - step_range[0] + 1
        self.mode = mode

        if mode == "flatten":
            self.action_space = spaces.Discrete(num_of_directions * self.steps)
        elif mode == "tuple":
            self.action_space = spaces.Tuple((spaces.Discrete(num_of_directions),
                                              spaces.Discrete(self.steps)))
        # elif mode == "multi_discrete":
        #     self.action_space = spaces.MultiDiscrete([num_of_directions, self.steps])

    def action_map(self, action):
        if self.mode == "flatten":
            orientation = action % self.num_of_directions
            step_length = int((action - orientation) / self.num_of_directions)
        else:
            orientation, step_length = action
        return (orientation, step_length + self.step_range[0])


# class ContinuousAction(ActionMapper):
#     def __init__(self, num_of_directions):
#         super(ContinuousAction, self).__init__()
#         self.mode = "continous"
#
#     def action_map(self, action):
#         action = (np.randint(action), 1)
#         return action


class WebotsEnv(WebotsBlue):
    def __init__(self, seed):
        super(WebotsEnv, self).__init__(seed=seed)
        self.com = communicate.Com(self.seeds)


class WebotsFake(WebotsBlue):
    def __init__(self, seed, N, num_of_sensors, obstacles_each,
                 step_range=(1, 7), action_mode="flatten"):
        self.action_mapper = DiscreteAction(num_of_sensors, step_range,
                                            action_mode)
        super(WebotsFake, self).__init__(seed=seed, action_mapping=self.action_mapper.action_map)
        self.com = FakeCom(self.seeds, N, num_of_sensors, obstacles_each)
        self.plotpadding = 1

        # set observation and action space
        obs_shape = self.state_object.observation_shape
        self.observation_space = spaces.Box(0, np.inf, shape=obs_shape,
                                            dtype=np.float32)

        self.action_space = self.action_mapper.action_space

    def calc_reward(self):
        base_v = np.sqrt(2) * self.com.N
        distance_penalty = self.get_target_distance()
        val = base_v * (1 - self.state_object.touching) - distance_penalty
        return val * 100 / base_v

    def reset(self):
        self.com.reset()
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

    @property
    def field(self):
        return self.com.field


class WebotsFakeMini(WebotsFake):
    def __init__(self, N=10, num_of_sensors=4, obstacles_each=2, seed=None,
                 step_range=(1, 1), action_mode="flatten"):
        super(WebotsFakeMini, self).__init__(seed, N, num_of_sensors,
                                             obstacles_each, step_range,
                                             action_mode)
        self.plotpadding = 0


class WebotsFakeMedium(WebotsFake):
    def __init__(self, N=40, num_of_sensors=8, obstacles_each=3, seed=None,
                 step_range=(1, 8), action_mode="flatten"):
        super(WebotsFakeMedium, self).__init__(seed, N, num_of_sensors,
                                               obstacles_each, step_range,
                                               action_mode)
        self.plotpadding = 0


class WebotsFakeLarge(WebotsFake):
    def __init__(self, N=500, num_of_sensors=16, obstacles_each=20, seed=None,
                 step_range=(1, 50), action_mode="flatten"):
        super(WebotsFakeLarge, self).__init__(seed, N, num_of_sensors,
                                              obstacles_each, step_range,
                                              action_mode)
        self.plotpadding = 4


class DQNEnv(WebotsFakeMini):
    def __init__(self, seed=None):
        super(DQNEnv, self).__init__(seed=seed)

    def fields_around(self, radius):
        n_f = radius * 2 + 1
        fields = np.zeros(shape=(n_f, n_f))
        pos = self.gps_actual
        x = 0
        y = 0
        d = (0, 0)
        for i in range(-radius, radius + 1):
            y = 0
            for j in range(-radius, radius + 1):
                d = (i, j)
                pt = tuple(map(lambda i, j: i + j, pos, d))
                if pt == pos:
                    fields[x][y] = -1
                elif self.field[pt[0]][pt[1]] > 0:
                    fields[x][y] = 1
                y += 1
            x += 1

        return fields

    def step_f(self, action, radius):
        done = False
        crash = False
        o_pos = self.gps_actual
        direction, len_ = action
        adj = (0, 0)
        if direction == 1:
            adj = (-1, 0)
        elif direction == 2:
            adj = (0, 1)
        elif direction == 3:
            adj = (1, 0)
        elif direction == 4:
            adj = (0, -1)
        n_p = tuple(map(lambda i, j: i + j, o_pos, adj))
        if self.field[n_p[0], n_p[1]] > 0:
            crash = True
        else:
            self.com.state.gps_actual = n_p
        if self.gps_actual == self.gps_target:
            done = True
        n_pos = self.gps_actual
        state = (self.gps_actual, self.fields_around(radius))
        reward = self.calc_reward(crash, done, o_pos, n_pos)
        return state, reward, done, {}

    def dist_reward(self, o_pos, n_pos):
        d_reward = 0
        t_pos = self.gps_target
        dx_old = abs(o_pos[0] - t_pos[0])
        dx_new = abs(n_pos[0] - t_pos[0])
        dy_old = abs(o_pos[1] - t_pos[1])
        dy_new = abs(n_pos[1] - t_pos[1])

        if dx_old > dx_new:
            d_reward = 20
        if dx_old < dx_new:
            d_reward = -20
        if dy_old > dy_new:
            d_reward = 20
        if dy_old < dy_new:
            d_reward = -20

        return d_reward

    def calc_reward(self, crash, done, o_pos, n_pos):
        reward = 0
        if done is True:
            reward = reward + 1000
        if crash is True:
            reward = reward - 100
        reward = reward + self.dist_reward(o_pos, n_pos)
        reward = reward - 10
        return reward

    def plot(self):
        self.render()


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

        if isinstance(action, tuple) is False or\
           isinstance(action[0], int) is False or\
           isinstance(action[1], int) is False:
            raise TypeError("Action must be of a tuple of 2 integers.")
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
