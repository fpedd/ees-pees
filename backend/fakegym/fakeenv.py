import numpy as np
import matplotlib.pyplot as plt
import copy
import gym
from gym import spaces

from fakegym.action import FakeAction
from fakegym.state import FakeState
from fakegym.utils.path_finding import finder_path
from fakegym.utils.getline import get_line
from fakegym.utils.sensor import Sensors
from fakegym.utils.seeding import np_random_seed
from fakegym.utils.misc import euklidian_distance

#Values for different things in the field
WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class WbtGymFake(gym.Env):
    def __init__(self, seed=None, N=10, num_of_sensors=4, obstacles_each=4,
                 step_range=(1, 1), obs=FakeState, obs_len=1):
        super(WbtGymFake, self).__init__()
        self.seed(seed)
        self.next_seed_idx = 1 

        # some general inits
        self.history = {}
        self.N = N
        self.offset = int(2 * self.N)
        self.num_of_sensors = num_of_sensors
        self.obs_len = obs_len
        self.obstacles_each = obstacles_each
        if type(obs) == type:
            self.obs = (obs)(self)
        else:
            self.obs = obs
        self._init(self.N, self.obstacles_each, self.obs_len)
        self.time_steps = 0
        self.plotpadding = 0
        self.visited_count = np.zeros(self.field.shape)

        # inits reward, action, observation
        self.total_reward = 0
        self.reward_range = (-1000, 1000)
        self.action_mapper = FakeAction(4, step_range)
        self.action_mapping = self.action_mapper.action_map
        self.action_space = self.action_mapper.action_space
        self.observation_space = spaces.Box(0, np.inf, shape=self.obs.shape(),
                                            dtype=np.float32)


    # =========================================================================
    # ====================       IMPORTANT PROPERTIES       ===================
    # =========================================================================
    @property
    def state(self):
        """Get current state of RL agent in."""
        return self.obs.get(self)
    
    @property
    def gps_actual(self):
        """Get current position of RL agent in the fake environment."""
        return self.obs.gps_actual

    @property
    def gps_target(self):
        """Get current position of RL agent in the fake environment."""
        return self.obs.gps_target


    # =========================================================================
    # ==========================       SEEDING       ==========================
    # =========================================================================
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


    # =========================================================================
    # ==========================        SETUPS       ==========================
    # =========================================================================
    def _init(self, N, obstacles_each, obs_len):
        self._setup_fields()

        # place obstacles randomly (horizontal and vertical walls)
        self.place_random_obstacle(dx=1, dy=obs_len, N=obstacles_each)
        self.place_random_obstacle(obs_len, 1, N=obstacles_each)

        # random start and finish positions
        self.obs.gps_actual = self.random_position()
        self.obs.gps_target = self.random_position()

        # init distance sensoring
        self.Sensors = Sensors(self)
        self.anchors, self.obs.distance = self.Sensors.distance_sensor()

        # reset seed to something random
        np_random_seed()

    def _setup_fields(self):
        """Initialize the field of fake environment."""
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)
        # set up walls
        self.field[0:WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL


    # =========================================================================
    # ==========================  RANDOM OBJECT PLACEMENT  ====================
    # =========================================================================
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
        """Set the corresponding position to obstacle value."""
        x1, x2, y1, y2 = x1x2y1y2
        self.field[x1:x2, y1:y2] = VAL_OBSTACLE

    def place_random_obstacle(self, dx, dy, N=1):
        """Randomly place obstacles"""
        if N == 1:
            x, y = self.random_position()
            xmax = min(x + dx, self.N - 1)
            ymax = min(y + dy, self.N - 1)
            self.add_obstacle((x, xmax, y, ymax))
        else:
            for _ in range(N):
                self.place_random_obstacle(dx, dy)


    # =========================================================================
    # ==========================         CORE        ==========================
    # =========================================================================
    def step(self, action):
        """Perform action on fake environment.

        Args:
            action (int): 
              Action is from RL agent.The action from the agent is mapped 
              via the action_class of the fake environment.

        Returns:
            observation (np.ndarray):
                Current RL agent state information, handled in the observation_class.
            reward (float):
                Reward generated by applying the agent's action. 
            done (bool):
                Flag whether fake environment run is finished. 
            dict:
                Empty info dict.
        """
        action = self.action_mapping(action)
        self.send(action)
        self.visited_count[self.gps_actual] += 1
        reward = self.calc_reward()
        self.total_reward += reward
        done = self.check_done()
        self.history[self.time_steps] = copy.deepcopy(self.state_object)
        self.time_steps += 1
        return self.state, reward, done, {}

    def close(self):
        """Close dummy, does nothing"""
        pass

    def get_target_distance(self, normalized=False):
        """Calculate euklidian distance to target.

        Args:
            normalized (bool, optional): 
                If True, get relative target distance. Normalized by maximal
                distance in environment (sqrt(2) * length).

        Returns:
            dist (float): 
                Distance to target.
        """
        dist = euklidian_distance(self.gps_actual, self.gps_target)
        if normalized is True:
            dist = dist / self.max_distance
        return dist

    def check_done(self):
        """Check done"""
        if self.time_steps == 1000:
            return True
        if self.total_reward < -1000:
            return True
        if self.gps_actual == self.gps_target:
            return True
        return False

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
        """Reset fake environment to random."""
        self.total_reward = 0
        if seed is None:
            seed = np_random_seed(set=False)
        self.seed(seed)
        self.next_seed_idx = 1
        self._init(self.N, self.obstacles_each, self.obs_len)
        self.time_steps = 0
        self.visited_count = np.zeros(self.field.shape)
        if hard is True and len(finder_path(self.field, self.gps_actual, self.gps_target)) < min_complexity:
            seed = np_random_seed(set=False)
            # print("No path available or too simple, reset with seed: ", seed)
            self.reset(seed)
        return self.state

    def render(self):
        """Plot the situaition of current fake environment."""
        plt.figure(figsize=(10, 10))
        f = self.field.copy()
        rx, ry = self.gps_actual
        tx, ty = self.gps_target
        s = self.plotpadding
        r_minx = max(0, (rx - s))
        r_maxx = min(rx + s + 1, self.N)
        r_miny = max(0, (ry - s))
        r_maxy = min(ry + s + 1, self.N)

        t_minx = max(0, (tx - s))
        t_maxx = min(tx + s + 1, self.N)
        t_miny = max(0, (ty - s))
        t_maxy = min(ty + s + 1, self.N)

        f[t_minx:t_maxx, t_miny:t_maxy] = VAL_TARGET
        f[r_minx:r_maxx, r_miny:r_maxy] = VAL_ROBBIE
        plt.matshow(f)
        return


    # =========================================================================
    # ==========================        SEND/RECV       ==========================
    # =========================================================================
    def send(self, action):
        """Pretend to send action to external controller."""
        self.anchors, self.obs.distance = self.Sensors.distance_sensor()
        orientation_idx, action_length = action

        pts_on_line = self.Sensors.pts_to_anchor(self.anchors[::int(self.num_of_sensors/4)][orientation_idx],
                                         filterout=False)[0]
        self.pt = pts_on_line
        self.obs.touching = False
        safept = self.obs.gps_actual
        for i, pt in enumerate(pts_on_line):
            # too far away
            if euklidian_distance(self.obs.gps_actual, pt) > action_length:
                break
            # crash
            elif self.field[pt[0], pt[1]] > 0:
                self.obs.touching = True
                break
            else:
                safept = pt
        self.obs.gps_actual = safept
        self.anchors, self.obs.distance = self.Sensors.distance_sensor()


    # =========================================================================
    # ========================   HELPER / PROPERTIES   ========================
    # =========================================================================
    def pt2outer(self, pt):
        """Convert position from inner to outer grid."""
        return (pt[0] + self.offset, pt[1] + self.offset)

    def pt2inner(self, pt):
        """Convert position from inner to outer grid."""
        return (pt[0] - self.offset, pt[1] - self.offset)

    @property
    def max_distance(self):
        """Get maximal distance in the fake environment."""
        return np.sqrt(2) * self.N

    @property
    def state_object(self):
        """Get FakeState class"""
        return self.obs

    @property
    def gps_visited_count(self):
        """Get frequency of RL agent get to the same position."""
        return self.visited_count[self.gps_actual]

    @property
    def total_len(self):
        return self.N + 2 * self.offset

    @property
    def pos_outer(self):
        """Convert current gps in outer grid."""
        return self.pt2outer(self.obs.gps_actual)

    # def average_solvability(self, test_cases=1000):
    #     """Check how many environmnents with current settings are solvable."""
    #     solves = 0
    #     for _ in range(test_cases):
    #         self.reset(hard=False)
    #         if self.is_path():
    #             solves += 1
    #     return solves / test_cases
