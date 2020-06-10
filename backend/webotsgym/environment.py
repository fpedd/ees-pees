import numpy as np
import gym
import time

import webotsgym.utils as utils
import webotsgym.automate as automate
from webotsgym.config import WebotConfig
from webotsgym.action import DiscreteAction
from webotsgym.evaluate import Evaluate
from webotsgym.observation import Observation
from webotsgym.communicate import Com


class WebotsEnv(gym.Env):
    def __init__(self,
                 seed=None,
                 gps_target=None,
                 train=False,
                 start_controller=False,
                 action_class=DiscreteAction,
                 evaluate_class=Evaluate,
                 observation_class=Observation,
                 config: WebotConfig = WebotConfig()):
        super(WebotsEnv, self).__init__()
        self.seed(seed)

        if gps_target is None and train is False:
            raise ValueError("Target GPS data must be supplied in normal mode")
        self.gps_target = gps_target

        # some general inits
        self.i = 0
        self.history = {}
        self.config = config

        self.reset_history = [time.time()]

        # init action, reward, observation
        self.action_class = action_class
        self.evaluate_class = evaluate_class
        self.observation_class = observation_class
        self._init_act_rew_obs(self)

        # communication and supervisor
        self.train = train
        self._setup_train()
        self._init_com()

        if train is False and start_controller is True:
            self.external_controller = automate.ExtCtrl()
            self.external_controller.init()

        self.send_data_request()

    # =========================================================================
    # ==========================       SEEDING       ==========================
    # =========================================================================
    def seed(self, seed):
        """Set main seed of env + 1000 other seeds for placements."""
        if seed is None:
            seed = utils.set_random_seed()
        self.seeds = [seed]
        np.random.seed(seed)
        self.seeds.extend(utils.seed_list(seed, n=1000))

    def get_next_seed(self):
        """Get next random seed, increment next_seed_idx."""
        seed = self.seeds[self.next_seed_idx]
        self.next_seed_idx += 1
        return seed

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])

    # =========================================================================
    # ==========================        SETUPS       ==========================
    # =========================================================================
    def _init_com(self):
        self.com = Com(self.gps_target, self.config)

    def _setup_train(self):
        if self.train is True:
            # start webots program, establish tcp connection
            self.supervisor = automate.WebotCtrl(self.config)
            self.supervisor.init()

            # start environment and update config
            self.supervisor.start_env()

            self.gps_target = self.config.gps_target

    def _init_act_rew_obs(self, env):
        # type to instance
        if type(self.action_class) == type:
            self.action_class = (self.action_class)()
        if type(self.observation_class) == type:
            self.observation_class = (self.observation_class)(env)
        if type(self.evaluate_class) == type:
            self.evaluate_class = (self.evaluate_class)(env, self.config)

        self.action_space = self.action_class.action_space
        self.observation_space = self.observation_class.observation_space
        self.reward_range = self.evaluate_class.reward_range

    @property
    def observation(self):
        return self.observation_class.get()

    # =========================================================================
    # ==========================         CORE        ==========================
    # =========================================================================
    def step(self, action):
        """Perform action on environment.

        Handled inside com class.
        """
        pre_action = self.state.pre_action
        action = self.action_class.map(action, pre_action)
        self.send_command_and_data_request(action)
        reward = self.calc_reward()
        if len(self.history) % 250 == 0:
            print("Reward (", len(self.history), ")\t", reward)
        done = self.check_done()

        return self.observation, reward, done, {}

    def calc_reward(self):
        """Calc reward with evaluate class."""
        return self.evaluate_class.calc_reward()

    def check_done(self):
        """Check done."""
        return self.evaluate_class.check_done()

    def reset(self):
        """Reset environment to random."""
        if self.supervisor_connected is True:
            self.reset_history.append(time.time())
            print("TIME FOR RESET=========", self.reset_history[-1] - self.reset_history[-2])

            seed = utils.set_random_seed(apply=False)
            self.seed(seed)
            print("=========resetting with seed: ", seed)
            self.supervisor.reset_environment(self.main_seed)

            self._init_com()
            self.send_data_request()

            return self.observation

    def close(self):
        """Close connection to supervisor and external controller."""
        if self.supervisor_connected is True:
            self.supervisor.close()

    def render(self):
        """Render dummy, does nothing."""
        pass

    # =========================================================================
    # ==========================        HELPER       ==========================
    # =========================================================================
    def send_data_request(self):
        self.com.send_data_request()
        self._update_history()

    def send_command(self, action):
        self.com.send_command(action)

    def send_command_and_data_request(self, action):
        self.com.send_command_and_data_request(action)
        self._update_history()

    def recv(self):
        """Receive state via Com class."""
        self.com.recv()
        self._update_history()

    def _update_history(self):
        """Add current state of Com to history."""
        self.history[self.i] = self.state
        self.i += 1

    def get_target_distance(self):
        """Calculate euklidian distance to target."""
        return utils.euklidian_distance(self.gps_actual, self.gps_target)

    @property
    def state(self):
        return self.com.state

    @property
    def iterations(self):
        return len(self.history)

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def supervisor_connected(self) -> bool:
        if self.supervisor is not None and self.supervisor.return_code == 0:
            return True
        return False
