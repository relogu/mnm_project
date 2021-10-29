from baselines import V_MAX, D_CM_MIN, TAU
from functools import partial

def quake(rng, intensity, cars):
    for i in range(len(cars)):
        cars[i].speed = cars[i].speed + intensity*rng.integers(-5, 5)/D_CM_MIN*TAU
        cars[i].check_speed()
    return cars
    
def big_quake(rng, cars):
    for i in range(len(cars)):
        cars[i].speed = rng.uniform(0, V_MAX)
    return cars

def leader_brake(cars):
    cars[0].speed = cars[0].speed - 10/D_CM_MIN*TAU
    cars[0].check_speed()
    return cars

def middle_brake(cars):
    cars[int(len(cars)/2)].speed = cars[0].speed - 10/D_CM_MIN*TAU
    cars[int(len(cars)/2)].check_speed()
    return cars

def get_pert_fn(rng, id: int = None):
    switcher = {
        1: partial(quake, rng, 1),
        2: partial(quake, rng, 2),
        3: partial(quake, rng, 3),
        4: partial(big_quake, rng),
        5: leader_brake,
        6: middle_brake,
    }
    return switcher[id]