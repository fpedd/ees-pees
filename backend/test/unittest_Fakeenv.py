import sys
import unittest
import random
import gym
import numpy as np
sys.path.insert(0, '../../backend')
from fakegym.fakeenv import WbtGymFake




class TestFakeEnv(unittest.TestCase):

    def setUp(self):
        self.env = WbtGymFake(N=10, num_of_sensors=4, obstacles_num=4, step_range=(1, 1), obs_len=1)
        self.N = 10

    def tearDown(self):
        del self.env

    def test_Baseenv(self):
        """Test some basic things."""
        env = self.env
        self.assertEqual(self.env.field.shape, (self.N, self.N), 
        "The size of the field must be equal to the size of environment")
        assert type(env.action_space) is gym.spaces.discrete.Discrete, "The type of action space must be correspond to gym.space.discrete.Discrete"
        self.assertEqual(env.obs.get(env).shape, (10,), 
        "The size of observation must be equal to 10")
        self.assertEqual(len(env.gps_actual), 2, 
        "The size of actual gps info must be 2")
        self.assertEqual(len(env.gps_target), 2, 
        "The size of target gps info must be 2")

    def test_reset(self):
        """Test reset function."""
        env = self.env
        obs_1 = env.reset()
        pos_actual1 = env.gps_actual
        pos_target1 = env.gps_target
        obs_2 = env.reset()
        pos_actual2 = env.gps_actual
        pos_target2 = env.gps_target

        self.assertFalse(pos_actual1 == pos_actual2 or pos_target1 == pos_target2 or (obs_1 == obs_2).all(), 
        "The position of start point/the position of target point/infos of observation must be different after reset the environment")

    def test_step(self):
        """Test step function."""
        env = self.env
        obs_start = env.reset()
        action = random.randint(0, 3)
        obs, rewards, done, _ = env.step(action)
        self.assertFalse((obs_start == obs).all()), "The information of observation must be updated after an action"
        self.assertTrue(env.reward_range[0] <= rewards <= env.reward_range[1], "The value of reward must fall in the range of reward")
        self.assertIsInstance(done, bool, "The `done` signal must be a boolean")

    def test_get_target_distance(self):
        """Test get target distance."""
        env = self.env
        actual = env.gps_actual
        target = env.gps_target
        distance = np.sqrt(np.square(actual[0]-target[0]) + np.square(actual[1]-target[1]))
        self.assertEqual(env.get_target_distance(normalized=False), distance, 
        "The function of get_target_distance(normalized=False) must calculate correct distance")
        distance_normalize = distance/ (np.sqrt(2)*env.N)
        self.assertEqual(env.get_target_distance(normalized=True), distance_normalize, 
        "The function of get_target_distance(normalized=True) must calculate correct normalized distance")

    def test_gps_visited_count(self):
        """Test visited count."""
        env = self.env
        rx, ry = env.gps_actual
        vc = env.gps_visited_count
        env.step(0)
        if (rx, ry != env.gps_actual):
            env.step(2)
            self.assertEqual(env.gps_visited_count, vc+1, 
            "The value of gps_visited_count must plus 1 when the agent get to the same position")
            env.step(0)
            env.step(2)
            self.assertEqual(env.gps_visited_count, vc+2, 
            "The value of gps_visited_count must plus 1 when the agent get to the same position")

    def test_reset_with_seed(self):
        """Test reset the env with same seed."""
        env = self.env
        obs_1 = env.reset(seed=1)
        pos_actual1 = env.gps_actual
        pos_target1 = env.gps_target
        obs_2 = env.reset(seed=1)
        pos_actual2 = env.gps_actual
        pos_target2 = env.gps_target
        self.assertTrue(pos_actual1 == pos_actual2 and pos_target1 == pos_target2 and (obs_1 == obs_2).all(), 
        "The position of start point/the position of target point/infos of observation must be same after reset the environment with same seed")


if __name__ == '__main__':
    unittest.main()
