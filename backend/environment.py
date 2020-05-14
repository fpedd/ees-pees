import numpy as np
import matplotlib.pyplot as plt
import abc

import communicate
import utils


class Env(abc.ABC):
    @abc.abstractmethod
    def step(self):
        pass

    def reward(self):
        pass


class WebotsEnv(Env):
    def __init__(self):
        self.com = communicate.Com()

    def step(self, action=None):
        if action is None:
            action = self.random_action()
        self.com.send(action)
        self.com.recv()
        return self.state_arr, self.reward, self.done, {}

    def random_action(self):
        action = communicate.WebotAction()
        action._init_randomly()
        return action

    @property
    def state(self):
        return self.com.state

    @property
    def reward(self):
        r = self.com.conf.MAX_DISTANCE * (1 - self.state.touching) - \
            self.target_distance
        return r

    @property
    def done(self):
        if self.target_distance < 20:
            return True
        return False

    @property
    def state_arr(self):
        return self.state.get()

    @property
    def pos(self):
        return self.com.state.gps_actual

    @property
    def targetpos(self):
        return self.com.state.gps_target

    @property
    def target_distance(self):
        return utils.euklidian_distance(self.pos[0:2], self.targetpos[0:2])


WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6


class FakeEnvironmentAbstract(Env):
    def __init__(self, N, startpos, targetpos, num_of_sensors=4):
        self.N = N
        self.offset = int(2 * N)
        self.num_of_sensors = num_of_sensors
        self.startpos = startpos
        self.pos = startpos
        self.target = targetpos
        self.plotpadding = 1
        self.setup_fields()
        self.distance_sensor()

    def reset(self):
        self.pos = self.startpos
        self.distance_sensor()
        reward = self.reward(crash=False)
        return self.state, reward, False, {}

    def step(self, action=None, target_gap=2, step_len=1):
        if self.distances is None:
            self.distance_sensor()
        if action is None:
            action = self.random_action()
        orientation_idx, len_ = action
        pts_on_line = self.pts_to_anchor(self.anchors[orientation_idx],
                                         filterout=False)[0]
        self.pt = pts_on_line
        crash = False
        safept = self.pos
        for i, pt in enumerate(pts_on_line):
            if self.field[pt[0], pt[1]] > 0:
                crash = True
                break
            if utils.euklidian_distance(self.pos, pt) > len_:
                break
            else:
                safept = pt
        self.pos = safept
        self.distance_sensor()
        reward = self.reward(crash)
        if self.target_distance() < target_gap:
            done = True
        else:
            done = False
        return self.state, reward, done, {}

    def random_action(self, length=None):
        orientation = np.random.randint(len(self.distance_arr))
        if length is None:
            length = int(self.N / 10)
        return orientation, length

    def reward(self, crash):
        reward = np.sqrt(2) * self.N**2 * (1 - crash) - self.target_distance()
        return reward

    def setup_fields(self):
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)

        # set up walls
        self.field[0:WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL

    def add_obstacle(self, x1x2y1y2):
        x1, x2, y1, y2 = x1x2y1y2
        self.field[x1:x2, y1:y2] = VAL_OBSTACLE
        self.distance_sensor()

    def pts_to_anchor(self, anchor, filterout=True):
        pts = []
        line = utils.get_line(self.pos_outer, anchor)
        for i, p in enumerate(line):
            if (self.inner[0] <= p[0] <= self.inner[1]) and \
               (self.inner[0] <= p[1] <= self.inner[1]):
                p = self.pt2inner(p)
                x, y = p
                if filterout is True and i > 0 and self.field[x, y] > 0:
                    return pts, utils.euklidian_distance(self.pos, p)
                pts.append(p)
        return pts, utils.euklidian_distance(self.pos, p)

    def distance_sensor(self):
        N = self.N
        pos = self.pos
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
        self.distances = distances
        return anchors, distances

    def render(self):
        plt.figure(figsize=(10, 10))
        f = self.field.copy()
        rx, ry = self.pos
        tx, ty = self.target
        s = self.plotpadding
        f[(rx - s):(rx + s + 1), (ry - s):(ry + s + 1)] = VAL_ROBBIE
        f[(tx - s):(tx + s + 1), (ty - s):(ty + s + 1)] = VAL_TARGET
        plt.matshow(f)

    def target_distance(self):
        return utils.euklidian_distance(self.pos, self.target)

    def pt2outer(self, pt):
        return (pt[0] + self.offset, pt[1] + self.offset)

    def pt2inner(self, pt):
        return (pt[0] - self.offset, pt[1] - self.offset)

    @property
    def distance_arr(self):
        return np.array(self.distances).ravel()

    @property
    def total_len(self):
        return self.N + 2 * self.offset

    @property
    def pos_outer(self):
        return self.pt2outer(self.pos)

    @property
    def state(self):
        positions = np.array([self.pos, self.target]).ravel()
        self.distance_sensor()
        data = np.hstack((positions, self.distance_arr))
        return data


class FakeEnvironmentMini(FakeEnvironmentAbstract):
    def __init__(self):
        super(FakeEnvironmentMini, self).__init__(N=10, startpos=(2, 2),
                                                  targetpos=(8, 8),
                                                  num_of_sensors=4)
        self.plotpadding = 0

    def step(self, action=None, target_gap=1, no_crash=False):
        if self.distances is None:
            self.distance_sensor()
        if action is None:
            action = self.random_action(no_crash=no_crash)

        orientation_idx = action
        pts_on_line = self.pts_to_anchor(self.anchors[orientation_idx],
                                         filterout=False)[0]
        self.pt = pts_on_line
        if self.field[pts_on_line[1][0], pts_on_line[1][1]] > 0:
            crash = True
        else:
            self.pos = pts_on_line[1]
            crash = False

        self.distance_sensor()
        reward = self.reward(crash)
        if self.target_distance() <= target_gap:
            done = True
        else:
            done = False
        return self.state, reward, done, {}

    def random_action(self, orientation=None, no_crash=False):
        if orientation is None:
            if no_crash is True:
                orientation = np.random.choice(np.where(self.distance_arr > 0)[0])
            else:
                orientation = np.random.randint(len(self.distance_arr))
        return orientation


class FakeEnvironmentMedium(FakeEnvironmentAbstract):
    def __init__(self, num_of_sensors=8):
        super(FakeEnvironmentMedium, self).__init__(
            N=50, startpos=(8, 8), targetpos=(35, 40),
            num_of_sensors=num_of_sensors)
        self.plotpadding = np.floor(self.N / 50)
