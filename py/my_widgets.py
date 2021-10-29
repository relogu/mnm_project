import pathlib
import sys
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QSizePolicy,
                             QSlider, QSpacerItem, QVBoxLayout,
                             QWidget, QDialog, QMainWindow,
                             QMenu, QAction)

buttons_explanation = 'This helper provides an explanations on the functionalities' \
    ' available by pressing buttons from your keyboard.<br>Before launching one of such' \
    ' actions is necessary to put the focus on the top-left pane, where the cars are moving.' \
    '<br>The focus could simply be put on any pane by clicking on it using the first mouse button.' \
    '<br>Here follows the list of actions and buttons.<br><br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Pause/Resume</b> the simulation by pressing the <em>Space</em>&nbsp;&nbsp;button<br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Restart</b> the simulation by pressing the <em>R</em>&nbsp;&nbsp;button<br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Kill</b> the simulation by pressing the <em>Esc</em>&nbsp;&nbsp;button<br><br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Dump</b> important measures (positions, velocities, distances) by pressing the <em>D</em>&nbsp;&nbsp;button<br><br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Traffic Light</b> simulated in front of the first car by pressing the <em>T</em>&nbsp;&nbsp;button<br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Perturbation 1</b> by pressing the <em>1</em>&nbsp;&nbsp;button<br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Perturbation 2</b> by pressing the <em>2</em>&nbsp;&nbsp;button<br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Perturbation 3</b> by pressing the <em>3</em>&nbsp;&nbsp;button<br>' \
    '&nbsp;&nbsp;&nbsp;&nbsp;<b>Perturbation 4</b> by pressing the <em>4</em>&nbsp;&nbsp;button<br>'

class Window(QMainWindow):
    """Main Window."""
    def __init__(self,
                 model: str = None,
                 parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle(
            "Traffic model simulation, model: {}".format(model))
        self.resize(800, 400)
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)
        help_action = QAction("&Help Content", self)
        help_menu.addAction(help_action)
        help_action.triggered.connect(self.about)
    
    def about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Help")
        layout = QVBoxLayout()
        message = QLabel(buttons_explanation)
        message.setTextFormat(Qt.RichText)
        layout.addWidget(message)
        dlg.setLayout(layout)
        dlg.exec()

class MyWidget(gl.GLViewWidget):

    def __init__(self,
                 app = None,
                 visualizer: object = None,
                 log_file: pathlib.Path = None,
                 *args,
                 **kwargs):
        super(MyWidget, self).__init__(*args, **kwargs)
        self.app = app
        self.visualizer = visualizer
        self.log_file = log_file

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            with open(self.log_file, 'a') as file:
                print('Killing simulation', file=file)
            sys.exit(self.app.exec_())
        elif ev.key() == QtCore.Qt.Key_Space:
            self.visualizer.pause_resume()
        elif ev.key() == QtCore.Qt.Key_R:
            self.visualizer.cars = []
            self.visualizer.init_cars()
            self.visualizer.init_grid()
            self.visualizer.traces = dict()
            self.visualizer.draw_cars(True)
            self.visualizer.real_time = 0.0
            with open(self.log_file, 'a') as file:
                print('Restart', file=file)
        elif ev.key() == QtCore.Qt.Key_T:
            self.visualizer.set_traffic_light()
            with open(self.log_file, 'a') as file:
                print('Traffic Light', file=file)
        elif ev.key() == QtCore.Qt.Key_D:
            self.visualizer.dump()
            with open(self.log_file, 'a') as file:
                print('Dumping Cars', file=file)
        elif ev.key() == QtCore.Qt.Key_Enter:
            with open(self.log_file, 'a') as file:
                print('Enter Key has been pressed', file=file)
        elif ev.key() == QtCore.Qt.Key_1:
            with open(self.log_file, 'a') as file:
                print('External Perturbation 1', file=file)
            self.visualizer.external_perturbation(1)
        elif ev.key() == QtCore.Qt.Key_2:
            with open(self.log_file, 'a') as file:
                print('External Perturbation 2', file=file)
            self.visualizer.external_perturbation(2)
        elif ev.key() == QtCore.Qt.Key_3:
            with open(self.log_file, 'a') as file:
                print('External Perturbation 3', file=file)
            self.visualizer.external_perturbation(3)
        elif ev.key() == QtCore.Qt.Key_4:
            with open(self.log_file, 'a') as file:
                print('External Perturbation 4', file=file)
            self.visualizer.external_perturbation(4)
        elif ev.key() == QtCore.Qt.Key_5:
            with open(self.log_file, 'a') as file:
                print('External Perturbation 5', file=file)
            self.visualizer.external_perturbation(5)
        elif ev.key() == QtCore.Qt.Key_6:
            with open(self.log_file, 'a') as file:
                print('External Perturbation 6', file=file)
            self.visualizer.external_perturbation(6)
        ev.accept()
        return super().keyPressEvent(ev)
    

class Slider(QWidget):
    def __init__(self,
                 minimum: int = 0,
                 maximum: int = 100,
                 name: str = None,
                 initial_value: float = None,
                 visualizer_fn = None,
                 parent = None,
                 dtype = int):
        super(Slider, self).__init__(parent=parent)
        self.visualizer_fn = visualizer_fn
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setStyleSheet('QLabel#nom_plan_label {color: white}')
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        spacer_item = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer_item)
        self.slider = QSlider(self)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(1)
        self.slider.setMaximum(200)
        self.slider.setMinimum(0)
        self.slider.setOrientation(QtCore.Qt.Vertical)
        self.horizontalLayout.addWidget(self.slider)
        spacer_item1 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer_item1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resize(self.sizeHint())

        self.dtype = dtype
        self.minimum = minimum
        self.maximum = maximum
        self.name = name
        self.slider.setValue(int(self.getSliderValue(initial_value)))
        self.label.setText('<font color="white">{0:s}: {1:.4g}</font>'.format(self.name, initial_value))
        self.slider.valueChanged.connect(self.setLabelValue)
        self.x = None
    
    def getLabelValue(self, slider_value):
        x = self.minimum + (slider_value / (self.slider.maximum() - self.slider.minimum())) * (
        self.maximum - self.minimum)
        return x
    
    def getSliderValue(self, label_value):
        x = ((label_value - self.minimum) * (self.slider.maximum() - self.slider.minimum())) / (
        self.maximum - self.minimum)
        return x

    def setLabelValue(self, value):
        x = self.getLabelValue(value)
        if self.dtype(x) >= self.maximum:
            x = self.maximum
        self.label.setText('<font color="white">{0:s}: {1:.4g}</font>'.format(self.name, self.dtype(x)))
        self.visualizer_fn(self.dtype(x))
