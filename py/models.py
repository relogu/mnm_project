import math
from math import pi as PI

from util import ring_distance_1d
from baselines import (ACC, D_CM_MIN, ALPHA_L,
                       ALPHA_O, EPS, DELTA_T, V_MAX)
        
def model_ca(cars, rng):
    ring = 2*PI*cars[0].radius
    dv = V_MAX/100
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        # acceleration
        cars[f_idx].speed = min(cars[f_idx].v_max, cars[f_idx].speed + dv)
        # deceleration
        d = ring_distance_1d(cars[f_idx].x, cars[l_idx].x, ring)
        d = math.trunc(d)
        if d <= cars[f_idx].speed/DELTA_T:
            cars[f_idx].speed = min(cars[f_idx].speed, (d-1)*DELTA_T)
        # random perturbation
        p = rng.uniform()
        if cars[f_idx].speed > 0 and p < 0.5:
            cars[f_idx].speed = max(cars[f_idx].speed-dv, 0)
        else:
            cars[f_idx].speed = max(cars[f_idx].speed, 0)
        # movement
        cars[f_idx].x = cars[f_idx].x + cars[f_idx].speed/DELTA_T
        cars[f_idx].x = math.trunc(cars[f_idx].x)
        cars[f_idx].ring_mod()
    # check distances between cars
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        d = ring_distance_1d(cars[f_idx].x, cars[l_idx].x, 2*PI*cars[f_idx].radius)
        if d < 1:
            cars[f_idx].x = cars[l_idx].x - 1
            cars[f_idx].ring_mod()
    return cars

def evolve_rk2(cars, rng, model):
    acc_fn = get_acc_fn(model)
    tmp_cars = cars.copy()
    for i in range(len(tmp_cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        tmp_cars[f_idx].acc = acc_fn(cars[f_idx], cars[l_idx], rng)
    for i in range(len(tmp_cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        # computations
        tmp_cars[f_idx].x += tmp_cars[f_idx].speed*DELTA_T/2
        tmp_cars[f_idx].ring_mod()
        tmp_cars[f_idx].speed += tmp_cars[f_idx].acc*DELTA_T/2
        tmp_cars[f_idx].check_speed()
    for i in range(len(tmp_cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        tmp_cars[f_idx].acc = acc_fn(tmp_cars[f_idx], tmp_cars[l_idx], rng)
    for i in range(len(tmp_cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        # computations
        cars[f_idx].x += tmp_cars[f_idx].speed*DELTA_T
        cars[f_idx].ring_mod()
        cars[f_idx].speed += tmp_cars[f_idx].acc*DELTA_T
        cars[f_idx].check_speed()
    # check distances between cars
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        d = ring_distance_1d(cars[f_idx].x, cars[l_idx].x, 2*PI*cars[f_idx].radius)
        if d < 1:
            cars[f_idx].x = cars[l_idx].x - 1
            cars[f_idx].ring_mod()
    return cars

def evolve_euler(cars, rng, model):
    acc_fn = get_acc_fn(model)
    # compute evolution
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        cars[f_idx].acc = acc_fn(cars[f_idx], cars[l_idx], rng)
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        # computations
        old_speed = cars[f_idx].speed
        cars[f_idx].speed += cars[f_idx].acc*DELTA_T
        cars[f_idx].check_speed()
        cars[f_idx].x += (old_speed + cars[f_idx].speed)*DELTA_T/2
        cars[f_idx].ring_mod()
    # check distances between cars
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        d = ring_distance_1d(cars[f_idx].x, cars[l_idx].x, 2*PI*cars[f_idx].radius)
        if d < 1:
            cars[f_idx].x = cars[l_idx].x - 1
            cars[f_idx].ring_mod()
    return cars

# TODO: decide whether to use or not
def get_safe_d(car):
    speed_in_kmh = car.speed*3.6*D_CM_MIN/DELTA_T
    mod_speed_in_kmh = car.reactivity-10+speed_in_kmh
    d_in_m = (mod_speed_in_kmh/10)**2
    return 1 + (d_in_m)/D_CM_MIN

def get_acc_fn(model: str = None):
    switcher = {
        'opt_speed': acc_opt_speed,
        'ftl': acc_ftl,
        'm_ftl': acc_m_ftl,
    }
    return switcher[model]

def acc_opt_speed(follower, leader, rng):
    # compute distance between two following cars
    ring = 2*PI*follower.radius
    d_n = ring_distance_1d(follower.x, leader.x, ring)
    # compute safety distance
    d_s = 1 + leader.speed
    # compute safety speed
    v_s = d_n - 1
    # the current car behaves following three regimes
    # 1. actual distance >> safety distance
    if d_n > 20*d_s:
        a = - ALPHA_O * (follower.speed - V_MAX)
    # 2. actual distance > safety distance
    elif d_n > d_s:
        a = - ALPHA_O * (follower.speed - leader.speed)
    # 3. actual distance <= safety distance
    elif d_n <= d_s:
        a = - 5 * ALPHA_O * (follower.speed - v_s)
    else:
        a = 0
    # add a very small constant to overcome the traffic light problem
    a += 0.00001*(rng.uniform()-0.5)*ACC
    return a

def acc_ftl(follower, leader, rng):
    # compute distance between two following cars
    ring = 2*PI*follower.radius
    d_n = ring_distance_1d(follower.x, leader.x, ring)
    # compute safety distance
    d_s = follower.speed + 1 if follower.speed > 0 else 1
    # the current car behaves following two regimes
    # 1. actual distance > safety distance
    if d_n > d_s:
        a = - ALPHA_L * (follower.speed - leader.speed)
    # 2. actual distance <= safety distance
    else:
        a = - ALPHA_L * (d_s - d_n)
    # add a very small constant to overcome the traffic light problem
    #a += 0.00001*(rng.uniform()-0.5)*ACC
    return a

def acc_m_ftl(follower, leader, rng):
    # compute distance between two following cars
    ring = 2*PI*follower.radius
    d_n = ring_distance_1d(follower.x, leader.x, ring)
    # compute safety distance
    d_s = follower.speed*DELTA_T + 1 if follower.speed > 0 else 1
    #d_s = get_safe_d(follower) if follower.speed > 0 else 1
    # the current car behaves following two regimes
    # the current car behaves following three regimes
    # 1. actual distance >> safety distance
    if d_n > 20*d_s:
        a = - ALPHA_O * (follower.speed - V_MAX)
    # 2. actual distance > safety distance
    elif d_n > d_s:
        a = - ALPHA_L * (follower.speed - (1+EPS) * leader.speed)
    # 3. actual distance <= safety distance
    else:
        a = - ALPHA_L * (d_s - d_n)
    # add a very small constant to overcome the traffic light problem
    #a += 0.00001*(rng.uniform()-0.5)*ACC
    return a
