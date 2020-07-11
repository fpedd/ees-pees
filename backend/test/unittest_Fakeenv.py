import unittest

import sys
sys.path.insert(0, '..')


import numpy as np

import gym
from fakegym.fakeenv import WbtGymFake
import random




class TestFakeEnv(unittest.TestCase):
    
    def setUp(self):
        self.env =WbtGymFake(N=10, num_of_sensors=4, obstacles_each=4,
                 step_range=(1, 1), obs_len=1)
        self.N = 10

    def tearDown(self):
        del self.env

    def test_Baseenv(self):
            env = self.env
            self.assertEqual(self.env.field.shape, (self.N,self.N))
            assert type(env.action_space) is gym.spaces.discrete.Discrete
            self.assertEqual(env.obs.get(env).shape, (9,))
            self.assertEqual(len(env.gps_actual ), 2)
            self.assertEqual(len(env.gps_target ), 2)
            
    def test_reset(self):
        env = self.env
        obs_1 =  env.reset()
        pos_actual1 = env.gps_actual
        pos_target1 =  env.gps_target
        obs_2 = env.reset()
        pos_actual2 = env.gps_actual
        pos_target2 =  env.gps_target
        self.assertFalse(pos_actual1 == pos_actual2)
        self.assertFalse(pos_target1 == pos_target2)
        self.assertFalse((obs_1 == obs_2).all())
    
    def test_step(self):
        env = self.env
        obs_start = env.reset()
        action = random.randint(0,3)
        obs, rewards, done, info = env.step(action)
        self.assertFalse((obs_start == obs).all())
        self.assertTrue(env.reward_range[0] < rewards < env.reward_range[1])
        self.assertIsInstance(done, bool)


if __name__ == '__main__':
    unittest.main()
