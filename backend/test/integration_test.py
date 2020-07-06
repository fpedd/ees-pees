import webotsgym as wg

from webotsgym.config import WebotConfig
from webotsgym.environment import WebotsEnv, WebotsGrid
from webotsgym.evaluate import Evaluate, EvaluateMats, EvaluatePJ0
from webotsgym.action import DiscreteAction, ContinuousAction
from webotsgym.observation import Observation

import numpy as np

import gym
import unittest
import sys
sys.path.insert(0, '..')


class TestEnvironment(unittest.TestCase):
    """Run integration tests for discrete environment."""
    def setUp(self):
        self.config = WebotConfig()
        self.config.num_obstacles = 0
        self.config.fast_simulation = False
        self.config.world_size = 8
        self.config.world_scaling = 0.5
        self.env = WebotsGrid(train=True,
                              gps_target=(1, 1),
                              config=self.config)

    def tearDown(self):
        print("done")

   def test_target(self):
       gps_target = (1,1)
       self.assertEqual(self.env.gps_target, gps_target)
       print(self.env.gps_target)


if __name__ == '__main__':
    unittest.main()
