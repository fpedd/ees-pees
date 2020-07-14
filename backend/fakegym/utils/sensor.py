import numpy as np
from .getline import get_line
from .misc import  euklidian_distance


class Sensors():

    def __init__(self, env):
        self.env = env


    def pts_to_anchor(self, anchor, filterout=True):
        """Finds all points on grid (x,y) from current gps to anchor point.

        Used to move the robot into specified direction.
        """
        pts = []
        line = get_line(self.env.pos_outer, anchor)
        for i, p in enumerate(line):
            if (self.env.inner[0] <= p[0] <= self.env.inner[1]) and \
               (self.env.inner[0] <= p[1] <= self.env.inner[1]):
                p = self.env.pt2inner(p)
                x, y = p
                if filterout is True and i > 0 and self.env.field[x, y] > 0:
                    return pts, euklidian_distance(self.env.gps_actual, p)
                pts.append(p)
        return pts, euklidian_distance(self.env.gps_actual, p)

    def distance_sensor(self):
        """Calculate distance to obstacles in all directions.

        Starts at 0 degrees and moves clockwise. The number and angle of
        directions is specified by num_of_sensors.
        """
        N = self.env.N
        pos = self.env.gps_actual
        endpoints = [(0, 0), (N - 1, 0), (0, N - 1), (N - 1, N - 1)]
        radius = round(max([euklidian_distance(pos, ep) for
                            ep in endpoints]))
        phi = np.linspace(0, 2 * np.pi, self.env.num_of_sensors + 1)[:-1]
        pos = self.env.pos_outer
        y = (radius * np.cos(phi)).astype(int) + pos[1]
        x = (radius * np.sin(phi)).astype(int) + pos[0]
        anchors = list(zip(x, y))
        distances = []
        for anch in anchors:
            distances.append(self.pts_to_anchor(anch)[1] - 1)
        return anchors, distances
