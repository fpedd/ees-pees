import unittest
import os
import sys
import time
sys.path.insert(0, '..')

import gym
import webotsgym as wg
import numpy as np



from webotsgym.config import WebotConfig
from webotsgym.environment import WebotsEnv, WebotsGrid
from webotsgym.evaluate import Evaluate, EvaluateMats, EvaluatePJ0
from webotsgym.action import DiscreteAction, ContinuousAction
from webotsgym.observation import Observation


class TestEnvironment(unittest.TestCase):
    """Run integration tests for discrete environment."""

    def setUp(self):
        """Open webotsEnv ."""
        self.setup_done = True
        self.config = WebotConfig()
        self.config.num_obstacles = 0
        self.config.fast_simulation = False
        self.config.world_size = 8
        self.config.world_scaling = 0.5
        self.env = WebotsGrid(seed=1,
                              train=True,
                              gps_target=(1, 1),
                              config=self.config)

    def tearDown(self):
        """Create final message and close webots."""
        print("done")
        os.system("killall -15 webots")
        os.system("killall -15 controller")
        os.system("killall -9 webots")

    def test_steps(self):
        """Test num_steps and reset on discrete action env."""
        num_steps = 4
        num_loops = 3
        for num in range(0, num_loops):
            if num != 0:
                self.env.reset()
            gps_checker, gps_state, step_checker = self.apply_steps(num_steps)
            self.assertEqual(gps_checker, gps_state)
            self.assertEqual(step_checker, num_steps)

    def apply_steps(self, num_steps):
        """Apply num_steps on the discrete environment."""
        gps_checker = np.round(0.5 + np.array(self.env.gps_actual) * 2)
        step_checker = 0
        for num in range(0, num_steps):
            gps_state = np.round(0.5 + np.array(self.env.gps_actual) * 2)
            if num % 2 == 0:
                if gps_state[0] < 2:
                    action = 1  # increase x
                    self.env.step(action)
                    gps_checker[0] = gps_checker[0] + 1
                    step_checker += 1
                else:
                    action = 3  # decrease x
                    self.env.step(action)
                    gps_checker[0] = gps_checker[0] - 1
                    step_checker += 1
            else:
                if gps_state[1] < 2:
                    action = 0  # increase y
                    self.env.step(action)
                    gps_checker[1] = gps_checker[1] + 1
                    step_checker += 1
                else:
                    action = 2  # decrease y
                    self.env.step(action)
                    gps_checker[1] = gps_checker[1] - 1
                    step_checker += 1
        gps_state = np.round(0.5 + np.array(self.env.gps_actual) * 2)
        return tuple(gps_checker), tuple(gps_state), step_checker


if __name__ == '__main__':
    unittest.main()
