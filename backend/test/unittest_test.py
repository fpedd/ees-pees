import unittest

import sys
sys.path.insert(0, '..')


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


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.config = WebotConfig()
        self.config.reset_env_after = 20000
        self.config.num_obstacles = 0
        self.config.world_size = 8
        self.config.world_scaling = 0.5
        self.env = WebotsGrid(config=self.config)
 
    
    def tearDown(self):
        print ('end execute')
    
    
    def test_example(self):
        
        #self.assertIn()
       # self.assertEqual()

if __name__ == '__main__':
    unittest.main()

