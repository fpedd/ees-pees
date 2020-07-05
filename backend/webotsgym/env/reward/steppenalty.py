import numpy as np


def step_penalty_04(env, step_base=-1, eps=10**-5):
    distance = env.get_target_distance() + eps
    dist_fac = (distance**0.4) / (distance)
    return step_base * dist_fac


def step_penalty_tanh(env, step_base=-1):
    distance = env.get_target_distance()
    dist_fac = np.tanh(distance / (0.5 * env.max_distance))
    return step_base * dist_fac
