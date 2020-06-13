import numpy as np
import matplotlib.pyplot as plt
import copy
import gym
from gym import spaces

import fakegym.utils as utils


def no_mapping(self, action):
    return action


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


class ContinuousAction(ActionMapper):
    def __init__(self, num_of_directions, step_range):
        super(ContinuousAction, self).__init__()
        self.num_of_directions = num_of_directions
        self.step_range = step_range
        self.steps = step_range[1] - step_range[0] + 1
        self.action_space = spaces.Box(-1, 1, shape=(2,), dtype=np.float32)

    def action_map(self, action):
        orientation, length = action
        orientation = utils.id_in_range(-1, 1, self.num_of_directions, orientation)
        length = utils.id_in_range(-1, 1, self.steps, length) + self.step_range[0]
        return orientation, length


class Observation():
    def __init__(self, env):
        self.gps_actual = None
        self.gps_target = None
        self.distance = None
        self.touching = None

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
        for k, v in self.__dict__.items():
            if k != "env":
                arr = np.hstack((arr, np.array(v)))
        return arr


class FakeGym(gym.Env):
    def __init__(self, seed=None, N=10, num_of_sensors=4, obstacles_each=4,
                 step_range=(1, 1), action_type="discrete",
                 discrete_action_shaping="flatten", obs=Observation):
        super(FakeGym, self).__init__()

        self.history = {}

        if action_type == "continous":
            self.action_mapper = ContinuousAction(num_of_sensors, step_range)
        else:
            self.action_mapper = DiscreteAction(num_of_sensors, step_range,
                                                discrete_action_shaping)
        self.seed(seed)
        self.reward_range = (-100, 100)
        self.action_mapping = self.action_mapper.action_map
        self.action_space = self.action_mapper.action_space

        self.com_inits = (N, num_of_sensors, obstacles_each)
        self.com = FakeCom(self.seeds, self.com_inits[0], self.com_inits[1],
                           self.com_inits[2])
        self.plotpadding = 0

        self.obs = (obs)(self)
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
        reward = self.calc_reward()
        self.total_reward += reward
        done = self.check_done()
        self.history[self.com.time_steps] = copy.deepcopy(self.state_object)
        self.com.time_steps += 1
        return self.state, reward, done, {}

    def close(self):
        pass

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    def check_done(self):
        if self.com.time_steps == 1000:
            return True
        if self.gps_actual == self.gps_target:
            return True
        return False

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
    def gps_target(self):
        return self.com.state.gps_target

    def calc_reward(self):
        """Calculate reward function.

        Idea(Mats):
        - negative reward for normal move so that james moves faster to goal
        - still lower negative reward if james gets closer to goal
        - high positive award for reaching it
        - high negative award to hitting a wall
        - epsilon only to divide never by 0

        """
        if self.gps_actual == self.gps_target:
            reward = 1000
        else:
            epsilon = 10**-5
            cost_step = 1
            distance = self.get_target_distance()+epsilon
            cost_distance = (distance**0.4)/(distance)
            reward_factor = -1
            reward = reward_factor * (cost_step * cost_distance)
            if self.state_object:
                reward = reward - 10
        return reward

    def reset(self):
        self.total_reward = 0
        seed = utils.np_random_seed(set=False)
        self.seed(seed)
        self.com = FakeCom(self.seeds, self.com_inits[0], self.com_inits[1],
                           self.com_inits[2])
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


WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class FakeState():
    def __init__(self):
        self.gps_actual = None
        self.gps_target = None
        self.distance = None
        self.touching = 0

    @property
    def observation_shape(self):
        if self.state_filled:
            arr = self.get()
            return arr.shape
        return None


class FakeCom():
    def __init__(self, seeds, N=100, num_of_sensors=4, obstacles_each=2):
        self.seeds = seeds
        self.next_seed_idx = 1
        self.inits = (N, num_of_sensors, obstacles_each)
        self.N = N
        self.offset = int(2 * N)
        self.num_of_sensors = num_of_sensors
        self._init(N, obstacles_each)
        self.time_steps = 0

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
