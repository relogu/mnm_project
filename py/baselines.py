## DEFINITION
# The grid on to which the ring of cars will be painted is 50x50x50.
# that's why I need to convert the virtual units.
U_TO_M = 20 # conversion factor to meters
M_TO_U = 1/U_TO_M # conversion factor to units
# The cars' size chosen is 4 meters
CAR_SIZE = 4
# The minimum distance between cars is set to 1 meter
D_MIN = 1
# Following this reasoning, the minimum distance between two following
# cars' centers of mass is:
D_CM_MIN = CAR_SIZE+D_MIN
# The maximum speed a car can reach is set
V_MAX = 36.1 # 36.1 m/s --> ~130 km/h, usual in highways
#V_MAX = 13.9 # 13.9 m/s --> ~50 km/h, usual on normal roads
# Gravity acceleration value
G = 9.8
# The acceleration of car on a road is in average 10% of gravity acceleration
ACC = G/10
# I set the value for accelaration fluctuations as the 10% of the average acc
ACC_FLUCT = ACC/10
# Time step for updating the model
DELTA_T = 0.05
# Time scale
TAU = 1.0

## RESCALING
# For modelling, I refer every dimensional quantity to the some constant
# in order to have adimensional values.
# Then the space is scaled using @{D_CM_MIN} and time using @{FRAME_TIMESTEP}
V_MAX = V_MAX/D_CM_MIN*TAU
G = G/D_CM_MIN*TAU*TAU
ACC = ACC/D_CM_MIN*TAU*TAU
ACC_FLUCT = ACC_FLUCT/D_CM_MIN*TAU*TAU

## These constants are already scaled
# Constant value for the Optimal Speed and FTL models, this describes 
# the acceleration properties of the driver-vehicle system
ALPHA_O = 0.5 # optimal speed, 2.0/1.0/0.5/0.4 stable
ALPHA_L = 0.5 # leader model, 2.0/1.0/0.5 stable
# Constant value that describes the influence of the leader speed for the
# computation of the acceleration in the mFTL model (dimensionless)
EPS = 0.01
