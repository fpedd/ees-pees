import sys
sys.path.insert(0,'..')
import numpy as np

import stable_baselines
from stable_baselines.common.vec_env import DummyVecEnv, VecCheckNan
from stable_baselines.common.env_checker import _check_spaces, _check_obs
import warnings
from typing import Union

import gym
from gym import spaces

import webotsgym as wg

def check_reset_step(env: gym.Env, observation_space: spaces.Space, action_space: spaces.Space):
    """ check reset() and step() function"""
    obs_pre = env.observation
    _check_obs(obs, observation_space, 'init')
    obs = env.reset()
    _check_obs(obs, observation_space, 'reset')
    assert (obs_pre != obs).all()

    action = action_space.sample()
    obs_next, reward, done, info = env.step(action)
    _check_obs(obs, observation_space, 'step')
    assert (obs_next != obs).all()

    


def check_webotenv(env: gym.Env):
    assert isinstance(env, gym.Env)
    _check_spaces(env)

    observation_space = env.observation_space
    action_space = env.action_space
    assert isinstance(observation_space, spaces.Box)
    if isinstance(action_space, spaces.Box):
        assert np.any(np.abs(action_space.low) != np.abs(action_space.high))
        assert np.any(np.abs(action_space.low) > 1) 
        assert np.any(np.abs(action_space.high) > 1)
    
    check_reset_step(env, observation_space, action_space)
