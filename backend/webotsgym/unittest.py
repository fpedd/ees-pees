"""
import unittest
import numpy as np
import gym

import webotsgym.utils as utils
import webotsgym.automate as automate
from webotsgym.config import WebotConfig
from webotsgym.environment import WebotsEnv, WebotsGrid
from webotsgym.action import DiscreteAction, GridAction
from webotsgym.evaluate import Evaluate
from webotsgym.observation import Observation, GridObservation
from webotsgym.communicate import Com


class TestWebotsGrid(unittest.TestCase):
    Runs tests for the environment.py.
    def __init__(self):
        config = WebotConfig()
        config.fast_simulation = False
        config.reset_env_after = 20000
        config.num_obstacles = 0
        config.world_size = 8
        config.world_scaling = 0.5
        env = WebotsGrid(train=False, config=config)
        
    def test_example(self):
        self.assertEqual(something, returnsomething)
        self.assertTrue(something(true))
        self.assertFalse(something(false))

if __name__ == '__main__':
    unittest.main()

"""
