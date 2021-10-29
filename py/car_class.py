import math
from math import pi as PI

class Car(object):

    def __init__(self,
                 x: float = None,
                 theta: float = None,
                 radius: float = None,
                 speed: float = None,
                 v_max: float = None,
                 reactivity: int = None):
        # cartesian coord.
        self.x = x
        # polar coord.
        self.theta = theta
        self.radius = radius
        # velocity
        self.speed = speed
        # acceleration
        self.acc = 0.0
        # car's characteristics
        self.v_max = v_max
        self.reactivity = reactivity # integer in [0, 10]
    
    def check_speed(self):
        if self.speed < 0:
            self.speed = 0
        if self.speed > self.v_max:
            self.speed = self.v_max
    
    def ring_mod(self):
        self.x = math.fmod(self.x, 2*PI*self.radius)
