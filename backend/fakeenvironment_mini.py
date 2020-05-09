import numpy as np
import matplotlib.pyplot as plt

def euklidian_distance(source, target):
    xs, ys = source
    xt, yt = target
    dx = xt - xs
    dy = yt - ys
    return np.sqrt(dx**2 + dy**2)

def get_line(start, end):

    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def xy2id(x, y, N=10):
    return x*N + y

def add_tuples(t1, t2):
    arr1 = np.array(t1)
    arr2 = np.array(t2)
    arr = arr1 + arr2
    return tuple(arr)

NUM_OF_SENSORS = 4
WALLSIZE = 1
VAL_WALL = 1
VAL_OBSTACLE = 2
VAL_ROBBIE = 4
VAL_TARGET = 6

class Environment():
    def __init__(self, startpos=(2, 2), targetpos=(8, 8), N=10):
        self.N = N
        self.startpos = startpos
        self.pos = startpos
        self.target = targetpos
        self.offset = int(2*N)
        self.setup_fields()
        self.distance_sensor()

        self.action_space = 4
        self.observation_space = N**2 # ???

    def setup_fields(self):
        self.grid = np.zeros((self.total_len, self.total_len))
        self.field = np.zeros((self.N, self.N))
        self.inner = (self.offset, self.offset + self.N)

        # set up walls
        self.field[0: WALLSIZE] = VAL_WALL
        self.field[-WALLSIZE:] = VAL_WALL
        self.field[:, 0:WALLSIZE] = VAL_WALL
        self.field[:, -WALLSIZE:] = VAL_WALL

    def add_obstacle(self, x1x2y1y2):
        x1, x2, y1, y2 = x1x2y1y2
        self.field[x1:x2, y1:y2] = VAL_OBSTACLE
        self.distance_sensor()


    def update_outer(self):
        self.grid[self.offset:(self.N+self.offset), self.offset:(self.N+self.offset)] = self.field

    def distance_sensor(self):
        N = self.N
        pos = self.pos
        endpoints = [(0, 0), (N-1, 0), (0, N-1), (N-1, N-1)]
        radius = round(max([euklidian_distance(pos, ep) for ep in endpoints]))
        phi = np.linspace(0, 2*np.pi, NUM_OF_SENSORS + 1)[:-1]
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

    def reset(self):
        self.pos = self.startpos
        return self.state

    def pts_to_anchor(self, anchor, filterout=True):
        pts = []
        line = get_line(self.pos_outer, anchor)
        for i, p in enumerate(line):
            if (self.inner[0] <= p[0] <= self.inner[1]) and (self.inner[0] <= p[1] <= self.inner[1]):
                p = self.pt2inner(p)
                x, y = p
                if filterout is True and i>0 and self.field[x, y] > 0:
                    return pts, euklidian_distance(self.pos, p)
                pts.append(p)
        return pts, euklidian_distance(self.pos, p)

    def step(self, action=None, len_=1, target_gap=2):
        if self.distances is None:
            self.distance_sensor()
        if action is None:
            action = self.random_action()

        orientation_idx = action
        pts_on_line = self.pts_to_anchor(self.anchors[orientation_idx], filterout=False)[0]
        self.pt = pts_on_line
        if self.field[pts_on_line[1][0], pts_on_line[1][1]] > 0:
            crash = True
        else:
            self.pos = pts_on_line[1]
            crash = False

        # state = (xy2id(self.pos[0], self.pos[1]), self.distance_sensor()[1])
        self.distance_sensor()
        reward = self.calc_reward(crash)
        if self.target_distance() <= target_gap:
            done = True
        else:
            done = False
        return self.state, reward, done, {}

    def random_action(self, orientation=None, length=None, maxlen=5, no_crash=False):
        if orientation is None:
            if no_crash is True:
                orientation = np.random.choice(np.where(self.distance_arr > 0)[0])
            else:
                orientation = np.random.randint(len(self.distance_arr))
        if length is None:
            len_ = np.random.random()*maxlen
        # return (orientation, len_)
        return orientation

    def calc_reward(self, crash):
        reward = 1.5*10- self.target_distance() - crash * 1.5*10
        return reward

    def target_distance(self):
        return euklidian_distance(self.pos, self.target)

    def pt2outer(self, pt):
        return (pt[0] + self.offset, pt[1] + self.offset)

    def pt2inner(self, pt):
        return (pt[0] - self.offset, pt[1] - self.offset)

    def plot(self):
        fig = plt.figure(figsize=(7, 7))
        f = self.field.copy()
        rx, ry = self.pos
        tx, ty = self.target
        s = 0
        f[rx-s:rx+s+1, ry-s:ry+s+1] = VAL_ROBBIE
        f[tx:tx+1, ty:ty+1] = VAL_TARGET
        plt.imshow(f)

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
    def pos_arr(self):
        return np.array(self.pos)

    @property
    def state(self):
        return np.hstack((self.pos_arr, self.distance_arr))
