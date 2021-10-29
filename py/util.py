from argparse import RawTextHelpFormatter, ArgumentParser
from os import spawnlpe
from typing import Dict
import pathlib
import math
from math import pi as PI
import numpy as np

from car_class import Car
from baselines import M_TO_U

def parse_args():
    """Parse the arguments passed."""
    description = 'This python program provides a UI to make some experiments' \
        ' on different traffic models on a closed route, i.e. a circle.\n' \
        'The user is able to choose one out of 4 different microscopic traffic models:\n' \
        '1. Follow-the-Leader\n2. Modifed Follow-the-Leader\n3. Optimal Speed\n4. Cellular Automata (discrete)\n' \
        'The user can also choose the number of cars to simulate, the radius of the circle and many other parameters.\n\n' \
        'A wider explanation of this program is available here: ' # TODO: put link to repo readme
    parser = ArgumentParser(description=description,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-n', '--number_of_cars',
                        dest='number_of_cars',
                        required=False,
                        type=int,
                        default=50,
                        action='store',
                        help='Set the number of cars to simulate')
    parser.add_argument('-r', '--radius',
                        dest='radius',
                        required=False,
                        type=float,
                        default=2.0,
                        action='store',
                        help='Set the radius of the track (in km)')
    parser.add_argument('-m', '--model',
                        dest='model',
                        required=False,
                        type=type(''),
                        default='ftl',
                        choices=['ftl', 'ca', 'opt_speed', 'm_ftl'],
                        action='store',
                        help='Set the model of the simulation')
    parser.add_argument('-s', '--scheme',
                        dest='scheme',
                        required=False,
                        type=type(''),
                        default='rk2',
                        choices=['rk2', 'euler'],
                        action='store',
                        help='Set the scheme for the evolution')
    parser.add_argument('-t', '--ui_update_ms',
                        dest='ui_update_ms',
                        required=False,
                        type=float,
                        default=1,
                        action='store',
                        help='Set the frame update timestep for the UI (in milliseconds)')
    parser.add_argument('-f', '--filling',
                        dest='filling',
                        required=False,
                        type=float,
                        default=1.0,
                        action='store',
                        help='Set the percentage of the circle that is initially filled')
    parser.add_argument('-o', '--out_folder',
                        dest='out_folder',
                        required=False,
                        type=type(''),
                        action='store',
                        help='Set the folder where the outputs will be dumped')
    args = parser.parse_args()
    return args

def ring_distance_1d(f_x: float, l_x: float, ring: float):
    d = l_x - f_x if l_x >= f_x else l_x + ring - f_x
    return d

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'same') / w

def average_speed(cars: list[Car]):
    avg = 0
    for car in cars:
        avg += car.speed
    return avg/len(cars)

def distance_field(cars: list[Car]):
    d = []
    radius = cars[0].radius
    for i in range(len(cars)):
        f_idx, l_idx = i, int(math.fmod(i-1,len(cars)))
        d.append(ring_distance_1d(cars[f_idx].x, cars[l_idx].x, 2*PI*radius))
    return np.array(d)

def speed_field(cars: list[Car]):
    return np.array([float(car.speed) for car in cars])

def compute_position(car: Car):
    x = M_TO_U * car.radius * \
        math.cos(car.x / car.radius)
    y = M_TO_U * car.radius * \
        math.sin(car.x / car.radius)
    return np.vstack([x, y, .0]).transpose()

def dump_result_dict(filename: str, result: Dict, verbose: int = 0):
    """Dump the result dictionary.
    The function dumps to the file given by complete path
    (relative or absolute) the row composed by results.values(),
    separated by a comma
    If result[\'round\'] == 1, the function dumps also the headers of 
    the dictionary, contained in results.keys(), separated by a comma.

    Args:
        filename ([str]): path to file to dump
        result ([Dict]): dictionary containing the values to dump
    """
    # get file path
    path_to_file = pathlib.Path(__file__).parent.parent.absolute()
    path_to_file = path_to_file/"output"/(filename+".dat")
    # touching file
    path_to_file.touch()
    if verbose > 0:
        print("Dumping results at "+str(path_to_file))
    with open(path_to_file, "a") as outfile:
        # write line(s)
        if result['timestamp'] == 0:
            print(','.join(list(result.keys())), file=outfile)
        print(','.join(map(str, list(result.values()))), file=outfile)
