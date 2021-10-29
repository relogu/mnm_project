import pathlib
import sys

import numpy as np
from math import pi as PI
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QHBoxLayout

from util import parse_args, compute_position, distance_field, speed_field
from my_widgets import Slider, MyWidget, Window
from car_class import Car
from models import evolve_euler, evolve_rk2, model_ca
from perturbations import get_pert_fn
from baselines import D_CM_MIN, V_MAX, ACC, TAU, DELTA_T

log_file = "simulation_log.txt"

class Visualizer(object):
    def __init__(self,
                 model: str = None,
                 ui_update_ms: int = 1,
                 n_cars: int = None,
                 radius: float = None,
                 filling: float = None,
                 start_speed: float = None,
                 scheme: str = None,
                 path_to_out: pathlib.Path = None):
        self.app = QtGui.QApplication([])
        main_window = Window(model)
        main_window.show()
        self.win = pg.GraphicsLayoutWidget(show=True)
        main_window.setCentralWidget(self.win)
        self.path_to_out = path_to_out
        self.w = MyWidget(app=self.app,
                          visualizer=self,
                          log_file=self.path_to_out/log_file)
        self.w.show()

        self.model = model
        self.ui_update_ms = ui_update_ms
        self.scheme = scheme
        self.rng = np.random.default_rng(51550)

        self.real_time = 0.0
        self.time_elapsed = 0
        self.time_avg_count = 0
        self.time_avg_limit = 10
        if self.model == 'FTL':
            self.time_avg_limit = 10
        elif self.model == 'CA':
            self.time_avg_limit = 5
        self.track = None
        self.speed_field = np.array([0.0]*N)
        self.dist_field = None

        self.n = n_cars  # number of cars
        self.traffic_light = False
        self.v_max = V_MAX # already in adimensional units
        self.start_speed = start_speed
        speed_in_kmh = V_MAX*3.6*D_CM_MIN/TAU # conversion to km/h
        self.filling = filling
        self.thetas = np.linspace(0.0, 2*PI*self.filling, self.n, endpoint=False)
        self.radius = radius*1000/D_CM_MIN # radius is given in km
        self.ring = 2*PI*self.radius
        self.delta_t = DELTA_T
        with open(self.path_to_out/log_file, 'a') as file:
            print('Initial conditions\n', file=file)
            print('\tInitial number of cars {}\n'.format(self.n), file=file)
            print('\tMax Speed {} km/h\n'.format(speed_in_kmh), file=file)
            print('\tMax safe distance (not for CA model) {} m\n'.format((1+V_MAX)*D_CM_MIN), file=file)
            print('\tMin safe distance (not for CA model) {} m\n'.format(D_CM_MIN), file=file)
            print('\tInitial angles (rad) {}\n'.format(self.thetas), file=file)
            print('\tInitial radius {} m\n'.format(radius*1000), file=file)
            print('\tInitial positions (u) {}\n'.format(self.radius*self.thetas), file=file)
            print('\tInitial positions (m) {}\n'.format(self.radius*self.thetas*D_CM_MIN), file=file)
            print('\tInitial ring length {} m\n'.format(self.ring*D_CM_MIN), file=file)
            print('\tSpace per car {} m\n'.format(self.ring*D_CM_MIN/self.n), file=file)
            print('\tInitial speed {} u\n'.format(V_MAX), file=file)
            print('\tInitial speed {} km/h\n'.format(V_MAX*3.6*D_CM_MIN/TAU), file=file)

        self.init_grid()
        self.cars = []
        self.init_cars()
        self.traces = dict()
        self.draw_cars(is_first=True)

        self.compute_speed_and_density()

        # get a layout
        self.layoutgb = QtGui.QGridLayout()
        self.win.setLayout(self.layoutgb)
        self.layoutgb.addWidget(self.w, 0, 0)
        self.w.sizeHint = lambda: pg.QtCore.QSize(50, 50)
        
        self.init_controls()

        self.init_plots()

        self.animation()

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            sys.exit(QtGui.QApplication.instance().exec_())
            
    def draw_cars(self, is_first: bool = False):
        for i in range(self.n):
            pts = compute_position(self.cars[i])
            if is_first:
                self.traces[i] = gl.GLScatterPlotItem(
                    pos=pts,
                    color=pg.mkColor((255, 255*self.cars[i].speed/self.v_max, 0)),
                    size=7.0)# could be an array
                self.w.addItem(self.traces[i])
            else:
                self.set_points_data(
                    name=i,
                    points=pts,
                    color=pg.mkColor((255, 255*self.cars[i].speed/self.v_max, 0)),
                )

    def set_points_data(self, name, points, color):
        self.traces[name].setData(pos=points, color=color)

    def set_plots_data(self):
        if self.time_avg_count == self.time_avg_limit:
            self.speed_field = np.nan_to_num(self.speed_field, posinf=self.v_max, neginf=0.0)
            self.speed_plot.setData(
                np.linspace(0, self.n, self.n, endpoint=False), # x
                self.speed_field) # y
            self.density_plot.setData(
                np.linspace(0, self.n, self.n, endpoint=False), # x
                self.dist_field) # y

    def compute_speed_and_density(self):
        self.time_avg_count+=1
        if self.time_avg_count > self.time_avg_limit:
            self.time_avg_count = 0
        if self.time_avg_count == 1:
            self.speed_field = np.zeros(len(self.cars))
            self.dist_field = np.zeros(len(self.cars))
        self.speed_field = self.speed_field + speed_field(self.cars)*3.6*D_CM_MIN/self.time_avg_limit/TAU
        self.dist_field = self.dist_field + distance_field(self.cars)*D_CM_MIN/self.time_avg_limit

    def update(self):
        if self.delta_t > 0:
            self.real_time += DELTA_T
            if self.traffic_light:
                self.cars[0].v_max = max(self.cars[0].v_max - ACC, 0)
            else:
                self.cars[0].v_max = V_MAX
            if self.model == 'ca':
                self.cars = model_ca(self.cars, self.rng)
            else:
                if self.scheme == 'rk2':
                    self.cars = evolve_rk2(self.cars, self.rng, self.model)
                elif self.scheme == 'euler':
                    self.cars = evolve_euler(self.cars, self.rng, self.model)
            
            self.draw_cars()
            self.compute_speed_and_density()
            self.set_plots_data()

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.ui_update_ms)
        self.start()

    def pause_resume(self):
        if self.delta_t == DELTA_T:
            self.delta_t = 0.0
            command = 'Pause'
        else:
            self.delta_t = DELTA_T
            command = 'Resume'
        with open(self.path_to_out/log_file, 'a') as file:
            print(command, file=file)

    def set_traffic_light(self):
        self.traffic_light = not self.traffic_light

    def external_perturbation(self, id):
        self.pause_resume()
        ext_pert_fn = get_pert_fn(self.rng, id)
        self.cars = ext_pert_fn(self.cars)
        self.dump()
        self.pause_resume()
    
    def set_n_cars(self, n_cars):
        self.pause_resume()
        self.n = int(n_cars)
        self.thetas = np.linspace(0.0, 2*PI*self.filling, self.n, endpoint=False)
        with open(self.path_to_out/log_file, 'a') as file:
            print('Setting number of cars to {}'.format(self.n), file=file)
            print('\tCurrent density is {} m^-1'.format(self.n/self.ring/D_CM_MIN), file=file)
            print('\tSpace per car {} m\n'.format(self.ring*D_CM_MIN/self.n), file=file)
        self.pause_resume()
        self.init_cars()
        self.init_grid()
        self.traces = dict()
        self.draw_cars(True)
        self.init_plots()
        
    def set_radius(self, new_radius):
        self.pause_resume()
        self.radius = new_radius*1000/D_CM_MIN # radius is given in km
        self.ring = 2*PI*self.radius
        with open(self.path_to_out/log_file, 'a') as file:
            print('Setting radius of the ring to {} m'.format(self.radius*D_CM_MIN), file=file)
            print('\tCurrent density is {} m^-1'.format(self.n/self.ring/D_CM_MIN), file=file)
            print('\tRing length {} m'.format(self.ring*D_CM_MIN), file=file)
            print('\tSpace per car {} m\n'.format(self.ring*D_CM_MIN/self.n), file=file)
        self.pause_resume()
        self.init_cars()
        self.draw_cars()
        self.init_plots()
    
    def set_filling(self, filling):
        self.pause_resume()
        self.filling = filling/100
        self.thetas = np.linspace(0.0, 2*PI*self.filling, self.n, endpoint=False)
        with open(self.path_to_out/log_file, 'a') as file:
            print('Setting initial filling to {}'.format(self.filling), file=file)
        self.pause_resume()
        self.init_cars()
        self.init_grid()
        self.draw_cars(True)
        self.init_plots()
    
    def dump(self):
        np.save(self.path_to_out/str('distance_field_'+str(self.real_time)), distance_field(self.cars))
        np.save(self.path_to_out/str('speed_field_'+str(self.real_time)), speed_field(self.cars))
        np.save(self.path_to_out/str('positions_'+str(self.real_time)), np.array([float(car.x) for car in self.cars]))
    
    def init_cars(self):
        new_cars = []
        for i in range(self.n):
            reactivity = np.random.choice(range(20),
                                p = [0.05]*20,
                                size = 1)
            c = Car(x=self.radius*self.thetas[self.n-1-i],
                    radius=self.radius,
                    theta=self.thetas[self.n-1-i],
                    speed=self.start_speed,
                    v_max=self.v_max,
                    reactivity=reactivity)
            new_cars.append(c)
        self.cars = new_cars
            
    def init_plots(self):
        self.speed_plot = pg.PlotWidget()
        self.density_plot = pg.PlotWidget()
        
        self.speed_plot.setLabels(title='Cars\' speeds', left='v [km/h]', bottom='car')
        #self.density_plot.setLabels(title='Line density', left='rho [1/m]', bottom='position [m]')
        self.density_plot.setLabels(title='Density as distances between cars', left='d [m]', bottom='car')
        
        self.density_plot.setYRange(0, 2*self.ring*D_CM_MIN/self.n)
        self.speed_plot.setYRange(0, self.v_max*3.6*D_CM_MIN/TAU+10)
        
        self.layoutgb.addWidget(self.speed_plot, 1, 1)
        self.layoutgb.addWidget(self.density_plot, 1, 0)
        
        self.speed_plot.sizeHint = lambda: pg.QtCore.QSize(50, 50)
        self.density_plot.sizeHint = lambda: pg.QtCore.QSize(50, 50)
        
        self.w.setSizePolicy(self.speed_plot.sizePolicy())
        
        self.speed_plot = self.speed_plot.plot(pen='y')
        self.density_plot = self.density_plot.plot(pen='r')
        self.time_avg_count = 0
        self.set_plots_data()
    
    def init_controls(self):
        h_layout = QHBoxLayout()
        self.w1 = Slider(1, 200, name='Cars', initial_value=self.n, visualizer_fn=self.set_n_cars)
        self.w2 = Slider(0, 2.5, name='Radius (km)', initial_value=self.radius/1000*D_CM_MIN, visualizer_fn=self.set_radius, dtype=float)
        self.w3 = Slider(0, 100, name='Ring\ninitial\nfilling', initial_value=self.filling*100, visualizer_fn=self.set_filling)
        h_layout.addWidget(self.w1)
        h_layout.addWidget(self.w2)
        h_layout.addWidget(self.w3)
        self.layoutgb.addLayout(h_layout, 0, 1)
        
    def init_grid(self):
        self.w.clear()
        # create the background grids
        gx = gl.GLGridItem()
        gx.setSize(50.0, 50.0, 50.0)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-25, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.setSize(50.0, 50.0, 50.0)
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -25, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.setSize(50.0, 50.0, 50.0)
        gz.translate(0, 0, -25)
        self.w.addItem(gz)


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    
    # Get the arguments' parser
    args = parse_args()
    
    # defining output folder
    if args.out_folder is None:
        path_to_out = pathlib.Path(__file__).parent.parent.absolute()/'output'
    else:
        path_to_out = pathlib.Path(args.out_folder)
    path_to_out.mkdir(parents=True, exist_ok=True)
    [file.unlink() for file in path_to_out.glob('*')]
    np.set_printoptions(threshold=np.inf)
    with open(path_to_out/log_file, 'w') as file:
        print('Starting the simulation\n\n', file=file)
    # Parse the arguments
    model = args.model
    N = args.number_of_cars
    R = args.radius
    # Launch the app
    v = Visualizer(model=model,
                   ui_update_ms=args.ui_update_ms,
                   n_cars=N,
                   radius=R,
                   filling=args.filling,
                   start_speed=V_MAX,
                   scheme=args.scheme,
                   path_to_out=path_to_out)
