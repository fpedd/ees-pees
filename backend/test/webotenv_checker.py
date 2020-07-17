"""Test the functionality of webot environment."""
import sys
import os
import numpy as np
from stable_baselines.common.env_checker import _check_spaces, _check_obs
import gym
from gym import spaces
sys.path.insert(0, '../../backend')
import webotsgym as wg

def check_reset_step(env: gym.Env, observation_space: spaces.Space, action_space: spaces.Space):
    """ Check reset() and step() function"""
    obs_pre = env.reset()
    _check_obs(obs_pre, observation_space, 'reset')
    obs_current = env.reset()
    assert (obs_pre[1:8] != obs_current[1:8]).any()
    assert (obs_pre[10:] != obs_current[10:]).any()

    for _ in range(3):
        action = action_space.sample()
        obs_next, _, _, _ = env.step(action)
        _check_obs(obs_next, observation_space, 'step')
    assert (obs_next[0:3] != obs_current[0:3]).any()
    assert (obs_next[6:9] != obs_current[6:9]).any()
    assert (obs_next[10:] != obs_current[10:]).any()

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
                assert j+1 == env.steps_in_run
                break
            if j == time_steps-1:
                assert env.steps_in_run == time_steps

def check_webotenv(env: gym.Env):
    """Main check env function."""
    assert isinstance(env, gym.Env)
    _check_spaces(env)

    observation_space = env.observation_space
    action_space = env.action_space
    assert isinstance(observation_space, spaces.Box)
    if isinstance(action_space, spaces.Box):
        assert np.all(np.abs(action_space.low) == np.abs(action_space.high))
        assert np.all(np.abs(action_space.low) <= 1)
        assert np.all(np.abs(action_space.high) <= 1)

    check_reset_step(env, observation_space, action_space)
    env.reset()
    check_run(env, action_space)


if __name__ == "__main__":
    config = wg.WbtConfig()
    config.world_size = 8
    config.num_obstacles = 2
    config.sim_mode = wg.config.SimSpeedMode.RUN
    #Test Webotenv
    env = wg.WbtGym(config=config)

    check_webotenv(env)
    os.system("killall -15 webots")
    os.system("killall -15 controller")
    os.system("killall -9 webots")
    print("========== END OF TEST ==========")
