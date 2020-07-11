import numpy as np
import pandas as pd
import gym
import warnings

import webotsgym.utils as utils
from webotsgym.config import WbtConfig

from webotsgym.env.action import WbtActContinuous
from webotsgym.env.observation import WbtObs
from webotsgym.env.reward import WbtReward
from webotsgym.com import WbtCtrl, Communication, ActionOut

gym.logger.set_level(40)  # disable lowered precision warning


class WbtGym(gym.Env):
    def __init__(self,
                 seed=None,
                 gps_target=(1, 1),
                 train=True,
                 action_class=WbtActContinuous,
                 request_start_data=False,
                 evaluate_class=WbtReward,
                 observation_class=WbtObs,
                 config: WbtConfig = WbtConfig()):
        super(WbtGym, self).__init__()
        self.seed(seed)

        self._gps_target = gps_target

        # some general inits
        self.history = []
        self.config = config
        self.distances = []
        self.rewards = []
        self.results = np.empty((0, 3))
        self.pre_action = ActionOut(config, (0, 0))

        # init action, reward, observation classes
        self.action_class = action_class
        self.evaluate_class = evaluate_class
        self.observation_class = observation_class
        self._init_act_rew_obs(self)

        # comunication and supervisor
        self.train = train
        self._setup_train()
        self._init_com()

        if request_start_data is True:
            self.get_data()

    # =========================================================================
    # ====================       IMPORTANT PROPERTIES       ===================
    # =========================================================================
    @property
    def supervisor_connected(self) -> bool:
        if self.supervisor is not None and self.supervisor.return_code == 0:
            return True
        return False

    @property
    def gps_target(self):
        if self.supervisor_connected:
            return self.config.gps_target
        elif self._gps_target is not None:
            return self._gps_target
        raise ValueError("Target GPS not defined.")

    @property
    def state(self):
        return self.com.state

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

    @property
    def main_seed(self):
        """Get the main seed of the env, first in seeds (list)."""
        return int(self.seeds[0])

    # =========================================================================
    # ==========================        SETUPS       ==========================
    # =========================================================================
    def _init_com(self):
        self.com = Communication(self.config)

    def _setup_train(self):
        self.supervisor = None
        if self.train is True:
            # start webots program, establish tcp connection
            self.supervisor = WbtCtrl(self.config)
            self.supervisor.init()

            # start environment and update config
            self.supervisor.start_env()

    def _init_act_rew_obs(self, env):
        # type to instance
        if type(self.action_class) == type:
            self.action_class = (self.action_class)(config=self.config)
        # overwriting relative action behaviour if action class is a type
        if self.config.relative_action is not None:
            warnings.warn("Relative property of action class is overwritten "
                          "by config.relative_action. This might interfere "
                          "with bounds argument for WbtActContinuous.")
            self.action_class.relative = self.config.relative_action

        if type(self.observation_class) == type:
            self.observation_class = (self.observation_class)(env)

        if type(self.evaluate_class) == type:
            self.evaluate_class = (self.evaluate_class)(env, self.config)

        self.action_space = self.action_class.action_space
        self.observation_space = self.observation_class.observation_space

    @property
    def observation(self):
        return self.observation_class.get()

    # =========================================================================
    # ==========================         CORE        ==========================
    # =========================================================================
    def step(self, action):
        """Perform action on environment.

        Parameters
        ----------
        action : tuple
            Action from RL agent to be send via external controller. The action
            from the agent is mapped via the action_class of the environment.


        Returns
        -------
        observation : np.ndarray
            Current webots state information, handled in the observation_class.
        reward : float
            Reward generated by applying the agent's action. This is handled in
            the evaluate_class.
        done : bool
            Flag whether environment run is finished. This is handled in the
            evaluate_class.
        dict
            Empty info dict.

        """
        if self.action_class.type == "grid":
            raise TypeError("Grid action class must be used with WbtGymGrid.")

        pre_action = self.state.get_pre_action()
        action = self.action_class.map(action, pre_action)
        self.send_command_and_data_request(action)
        # self.pre_action = action

        reward = self.calc_reward()
        self.rewards.append(reward)
        done = self.check_done()

        # logging, printing
        self.distances.append(self.get_target_distance())
        self._update_history()

        self.send_stop_action()

        return self.observation, reward, done, {}

    def calc_reward(self):
        """Calc reward with evaluate class."""
        return self.evaluate_class.calc_reward()

    def check_done(self):
        """Check done."""
        return self.evaluate_class.check_done()

    def reset(self, seed=None):
        """Reset environment to random."""
        if self.supervisor_connected is True:
            # logging trajectory results
            if self.iterations > 0:
                trajectory_result = np.array([self.iterations,
                                              self.total_reward,
                                              self.state.sim_time])
                self.results = np.vstack((self.results, trajectory_result))

            # resetting
            if seed is None:
                seed = utils.set_random_seed(apply=False)
            self.seed(seed)

            self.supervisor.reset_environment(self.main_seed)
            self.history = []
            self.rewards = []
            self.distances = []
            self._init_com()
            self.get_data()

            if self.get_target_distance(False) < 0.05:
                self.reset()

            return self.observation
        return False

    def close(self):
        """Close connection to supervisor and external controller."""
        if self.supervisor_connected is True:
            self.supervisor.close()

    def render(self):
        """Render dummy, does nothing."""
        pass

    # =========================================================================
    # ==============================   PLOTTING   =============================
    # =========================================================================
    def plot_lidar(self, relative=False):
        if relative is True:
            data = self.state.lidar_relative
        else:
            data = self.state.lidar_absolute
        utils.plot_lidar(data)

    # =========================================================================
    # ========================   HELPER / PROPERTIES   ========================
    # =========================================================================
    def get_data(self):
        self.com.get_data()

    def send_stop_action(self):
        act = ActionOut(action=(0, 0))
        self.send_command_and_data_request(act)

    def send_command_and_data_request(self, action):
        self.com.send_command_and_data_request(action)

    def _update_history(self):
        """Add current state of Com to history."""
        self.history.append(self.state)

    def get_target_distance(self, normalized=False):
        """Calculate euklidian distance to target.

        Parameters
        ----------
        normalized : bool
            If True, get relative target distance. Normalized by maximal
            distance in environment (sqrt(2) * length).

        Returns
        -------
        float
            Distance of roboter to target.

        """
        distance = utils.euklidian_distance(self.gps_actual, self.gps_target)
        if normalized is True:
            distance = distance / self.max_distance
        return distance

    @property
    def iterations(self):
        return len(self.history)

    @property
    def total_reward(self):
        return sum(self.rewards)

    @property
    def gps_actual(self):
        return self.com.state.gps_actual

    @property
    def max_distance(self):
        return np.sqrt(2) * self.config.world_size

    @property
    def df_results(self):
        res = self.results
        res = res[res[:, 0] > 0]
        df = pd.DataFrame(res)
        df.columns = ["steps", "total_reward", "sim_time"]
        return df
