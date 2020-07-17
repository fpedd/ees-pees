import sys
import unittest
import random
import gym
import numpy as np
# sys.path.insert(0, '../../backend')
sys.path.insert(0, '/home/shanshan/github/ees-pees/backend')
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
        self.assertEqual(self.env.field.shape, (self.N, self.N))
        assert type(env.action_space) is gym.spaces.discrete.Discrete
        self.assertEqual(env.obs.get(env).shape, (10,))
        self.assertEqual(len(env.gps_actual), 2)
        self.assertEqual(len(env.gps_target), 2)

    def test_reset(self):
        """Test reset function."""
        env = self.env
        obs_1 = env.reset()
        pos_actual1 = env.gps_actual
        pos_target1 = env.gps_target
        obs_2 = env.reset()
        pos_actual2 = env.gps_actual
        pos_target2 = env.gps_target

        self.assertFalse(pos_actual1 == pos_actual2 and pos_target1 == pos_target2 and (obs_1 == obs_2).all())

    def test_step(self):
        """Test step function."""
        env = self.env
        obs_start = env.reset()
        action = random.randint(0, 3)
        obs, rewards, done, info = env.step(action)
        self.assertFalse((obs_start == obs).all())
        self.assertTrue(env.reward_range[0] <= rewards <= env.reward_range[1])
        self.assertIsInstance(done, bool)

    def test_get_target_distance(self):
        """Test get target distance."""
        env = self.env
        actual = env.gps_actual
        target = env.gps_target
        distance = np.sqrt(np.square(actual[0]-target[0]) + np.square(actual[1]-target[1]))
        self.assertEqual(env.get_target_distance(normalized=False), distance)
        distance_normalize = distance/ (np.sqrt(2)*env.N)
        self.assertEqual(env.get_target_distance(normalized=True), distance_normalize)

    def test_gps_visited_count(self):
        """Test visited count."""
        env = self.env
        rx, ry = env.gps_actual
        vc = env.gps_visited_count
        env.step(0)
        if (rx, ry != env.gps_actual):
            env.step(2)
            self.assertEqual(env.gps_visited_count, vc+1)
            env.step(0)
            env.step(2)
            self.assertEqual(env.gps_visited_count, vc+2)

    def test_reset_with_seed(self):
        """Test reset the env with same seed."""
        env = self.env
        obs_1 = env.reset(seed=1)
        pos_actual1 = env.gps_actual
        pos_target1 = env.gps_target
        obs_2 = env.reset(seed=1)
        pos_actual2 = env.gps_actual
        pos_target2 = env.gps_target
        self.assertTrue(pos_actual1 == pos_actual2 and pos_target1 == pos_target2 and (obs_1 == obs_2).all())


if __name__ == '__main__':
    unittest.main()
