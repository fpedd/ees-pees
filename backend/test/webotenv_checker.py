import sys
import os
import numpy as np
from stable_baselines.common.env_checker import _check_spaces, _check_obs
import gym
from gym import spaces
sys.path.insert(0, '../../backend')
import webotsgym as wg


def check_reset_step(env: gym.Env, observation_space: spaces.Space,
                     action_space: spaces.Space):
    """ Check reset() and step() function."""
    obs_pre = env.reset()
    _check_obs(obs_pre, observation_space, 'reset')
    obs_current = env.reset()
    assert (obs_pre[1:8] != obs_current[1:8]).any(), \
        "The infos of the observation must differ after reset the webot env."
    assert (obs_pre[10:] != obs_current[10:]).any(), \
        "The infos of the lidar data must differ after reset the webot env."

    for _ in range(3):
        action = action_space.sample()
        obs_next, _, _, _ = env.step(action)
        _check_obs(obs_next, observation_space, 'step')
    assert (obs_next[0:3] != obs_current[0:3]).any(), \
        "The information of observation must be updated after the first action"
    assert (obs_next[6:9] != obs_current[6:9]).any(), \
        "The information of observation must be updated after the first action"
    assert (obs_next[10:] != obs_current[10:]).any(), \
        "The information of lidar data must be updated after the first action"


def check_run(env: gym.Env, action_space: spaces.Space):
    """Check normally running process of webotenv."""
    num_env = 3
    time_steps = 100
    for _ in range(num_env):
        env.reset()
        for j in range(time_steps):
            action = action_space.sample()
            _, _, done, _ = env.step(action)
            if done is True:
                assert j+1 == env.steps_in_run, \
                         "The value of time steps is correct when 'done'"
                break
            if j == time_steps-1:
                assert env.steps_in_run == time_steps, \
                    "The number time steps are correct after steps > 1"


def check_webotenv(env: gym.Env):
    """Check main env function."""
    assert isinstance(env, gym.Env), \
        "The environment must inherit from gym.Env class"
    _check_spaces(env)

    observation_space = env.observation_space
    action_space = env.action_space
    assert isinstance(observation_space, spaces.Box), \
        "The observation space must inherit from gym.spaces"
    if isinstance(action_space, spaces.Box):
        assert np.all(np.abs(action_space.low) == np.abs(action_space.high)), \
            "The Box action space must be symmetric"
        assert np.all(np.abs(action_space.low) <= 1), \
            "The Box action space must be normalized"
        assert np.all(np.abs(action_space.high) <= 1), \
            "The Box action space must be normalized"

    check_reset_step(env, observation_space, action_space)
    env.reset()
    check_run(env, action_space)


if __name__ == "__main__":
    config = wg.WbtConfig()
    config.world_size = 8
    config.num_obstacles = 2
    config.sim_mode = wg.config.SimSpeedMode.RUN
    # Test Webotenv
    env = wg.WbtGym(config=config)

    check_webotenv(env)
    os.system("killall -15 webots")
    os.system("killall -15 controller")
    os.system("killall -9 webots")
    print("========== END OF TEST ==========")
