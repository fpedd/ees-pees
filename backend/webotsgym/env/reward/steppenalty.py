import numpy as np
from webotsgym.utils import exponential_decay


def step_pen_04(env, step_base=-1, eps=10**-5):
    distance = env.get_target_distance() + eps
    dist_fac = (distance**0.4) / (distance)
    return step_base * dist_fac


def step_pen_tanh(env, step_base=-1):
    distance = env.get_target_distance()
    dist_fac = np.tanh(distance / (0.5 * env.max_distance))
    return step_base * dist_fac


def step_pen_exp(x, step_penalty=-1, lambda_=5):
    return step_penalty * (1 - exponential_decay(x, lambda_=lambda_))
