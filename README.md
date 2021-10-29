# Project of the exam of Models and Numerical Methods in Physics

This repository contains the scripts used for developing a composed simulation of some traffic models on a system of virtual cars moving on ring.
The idea behind the project is to implement some of the simplest models of the dynamics of cars in a traffic flow, and simulating their evolution graphically to have a visual feedback of their single behaviours.
In the end, a comparison between those simple models is performed looking at some common phenomena in traffic flow dynamics such traffic jam, traffic lights and so on.

## Models

First microscopic models were proposed in the 1950's. They all have a common organization structure. Every car is numerated by the subscript <img src="https://render.githubusercontent.com/render/math?math=n"> according to its order on the road that is assumed to be a (closed) line of constant length. It is assumed that the acceleration, and then speed and position, of the <img src="https://render.githubusercontent.com/render/math?math=n">-th car is defined by the states of the neighbour cars, the most important effect being produced by the immediately preceding car <img src="https://render.githubusercontent.com/render/math?math=n-1">. This car is often called the *leader* and then the entire class of micromodels is often called *"follow-the-leader"* models. The coordinates and speed of the cars will be denoted, respectively, by <img src="https://render.githubusercontent.com/render/math?math=x_n"> and <img src="https://render.githubusercontent.com/render/math?math=v_n">. The factors that mostly define acceleration of the <img src="https://render.githubusercontent.com/render/math?math=n">-th car are:

* speed of the given car w.r.t. the leader <img src="https://render.githubusercontent.com/render/math?math=\Delta v_n(t)=v_n(t)-v_{n-1}(t)">;
* intrinsic car speed <img src="https://render.githubusercontent.com/render/math?math=v_n(t)"> defining the safe interval of movement;
* distance to the leader <img src="https://render.githubusercontent.com/render/math?math=d_n(t)=x_{n-1}(t)-x_n(t)"> or, as a variant in some models, the "pure" distance <img src="https://render.githubusercontent.com/render/math?math=s_n(t)=d_n(t)-l_{n-1}"> taking into account the car length <img src="https://render.githubusercontent.com/render/math?math=l_n">.

Correspondingly, in the general form the movement of cars obeys a system of ordinary differential equations:

<img src="https://render.githubusercontent.com/render/math?math=\dot{v}_n(t) = f(v_n,\Delta v_n,d_n)">.

Different models provide different <img src="https://render.githubusercontent.com/render/math?math=f"> functions. In the following the models used will be discussed in detail.

### Follow the Leader (FTL) Model

In the very first implementations of the follow-the-leader mechanism, it was assumed that each driver is able to adapt its speed to that of the leader. The specific model used defines two different regimes of adaptation depending on the distance <img src="https://render.githubusercontent.com/render/math?math=d_s=d_{\tau}%2Bd_{min}">. Here <img src="https://render.githubusercontent.com/render/math?math=d_n"> and the computed safety distance <img src="https://render.githubusercontent.com/render/math?math=d_s=d_{\tau}%2Bd_{min}">. Here <img src="https://render.githubusercontent.com/render/math?math=d_{\tau}=v_n(t)\cdot \tau"> is the distance the car would cover keeping constant its velocity, <img src="https://render.githubusercontent.com/render/math?math=\tau"> is the time step, <img src="https://render.githubusercontent.com/render/math?math=d_{min}"> is a constant minimal distance whose value is chosen consider the cars' mean size and a realistic value for the distance between cars in a traffic jam. The differential equations, for the two regimes, are then given by:

* for <img src="https://render.githubusercontent.com/render/math?math=d_n\leq d_s">, <img src="https://render.githubusercontent.com/render/math?math=\dot{v}_n(t)=\alpha_l\cdot (d_n-d_s)">
* for <img src="https://render.githubusercontent.com/render/math?math=d_n>d_s">, <img src="https://render.githubusercontent.com/render/math?math=\dot{v}_n(t)=\alpha_l\cdot [(1%2B\epsilon_l)\cdot v_{n-1}(t)-v_n(t)]">,

where <img src="https://render.githubusercontent.com/render/math?math=1/\alpha_l"> is a positive constant modelling the characteristic time of adaptation, and <img src="https://render.githubusercontent.com/render/math?math=\epsilon_l\geq0"> weights the influence of the leader speed for computing the acceleration of the current car. The first regime represent the "free motion" of cars while the latter the car following regime.

### Optimal Speed Model

Another class of models, similar from a mathematical point of view to the previous, are those based on the assumption that the drivers want to approach their speed a desired value, here called <img src="https://render.githubusercontent.com/render/math?math=v_{max}">. Using this point of view, every driver has a "safe" speed <img src="https://render.githubusercontent.com/render/math?math=v_s"> which depends on the distance to the leader through <img src="https://render.githubusercontent.com/render/math?math=v_s=\frac{1}{\tau}(d_n - d_{min})">. Here, again, <img src="https://render.githubusercontent.com/render/math?math=\tau"> is the time step, <img src="https://render.githubusercontent.com/render/math?math=d_{min}"> is a constant minimal distance computed similarly to FTL model one. These are called Optimal Speed models. In this implementation, the regimes of acceleration becomes three. Again the fundamental quantities are <img src="https://render.githubusercontent.com/render/math?math=d_n"> and <img src="https://render.githubusercontent.com/render/math?math=d_s">, and their difference defines the regime to adopt and then the following differential equations:

* for <img src="https://render.githubusercontent.com/render/math?math=d_n\gg d_s">, <img src="https://render.githubusercontent.com/render/math?math=\dot{v}_n(t)=\alpha_ol\cdot (v_{max}-v_n(t))">,
* for <img src="https://render.githubusercontent.com/render/math?math=d_n>d_s">, <img src="https://render.githubusercontent.com/render/math?math=\dot{v}_n(t)=\alpha_o\cdot (v_{n-1}(t)-v_n(t))">,
* for <img src="https://render.githubusercontent.com/render/math?math=d_n\leq d_s">, <img src="https://render.githubusercontent.com/render/math?math=\dot{v}_n(t)=5\alpha_o\cdot (v_{s}(t)-v_n(t))">.

As mentioned before, <img src="https://render.githubusercontent.com/render/math?math=1/\alpha_o"> is a positive constant modelling the characteristic time of adaptation. In this formulation, the first regime represent the "free motion" of a car, the second the car following modality, while the last the optimal distance motion. The difference between the first two regimes has to be numerically defined in the implementation.

### Cellular Automata (CA) Model

The Cellular Automata (CA) concept was firstly introduced by von Neumann in the 1950's in connection with the abstract theory of self-reproducing computers. By CA is meant an idealized representation of a physical system with discrete time and space and the system elements having a discrete set of feasible states.

In these kind of models the car coordinate and speed, as well as time, are discrete variables. The road line is decomposed into conventional "cells" of identical length <img src="https://render.githubusercontent.com/render/math?math=\Delta x">, each cell being at any time instant either occupied by a single car or empty. The states of all cells are simultaneously updated according to a certain set of rules at each time step. The specific set of rules defines the specif CA model. The used formulation is a slightly modified version of the original proposed by Nagel-Schreckberg. The speed of the car is also discretized and can assume values from 0 to <img src="https://render.githubusercontent.com/render/math?math=v_{max}">, the unitary quantization step <img src="https://render.githubusercontent.com/render/math?math=\Delta v"> could be defined.

The state of all cars in the system is updated at each step <img src="https://render.githubusercontent.com/render/math?math=t\longrightarrow\,t%2B1"> according to the following rules:

* **Step 1:** *Acceleration.* If <img src="https://render.githubusercontent.com/render/math?math=v_n<v_{max}">, then the speed of the <img src="https://render.githubusercontent.com/render/math?math=n">-th car is increased by <img src="https://render.githubusercontent.com/render/math?math=\Delta v">, if <img src="https://render.githubusercontent.com/render/math?math=v_n=v_{max}">, it remains unchanged:

    <img src="https://render.githubusercontent.com/render/math?math=v_n\longrightarrow \min(v_n%2B\Delta v, v_{max})">.

* **Step 2:** *Deceleration.* If <img src="https://render.githubusercontent.com/render/math?math=d_n\leq v_n">, then the speed of the <img src="https://render.githubusercontent.com/render/math?math=n">-th car is reduced to <img src="https://render.githubusercontent.com/render/math?math=d_n-1">:

    <img src="https://render.githubusercontent.com/render/math?math=v_n\longrightarrow\min(v_n, d_n-1)">.

* **Step 3:** *Random perturbations.* If <img src="https://render.githubusercontent.com/render/math?math=v_n>0">, then the speed of the $n$th car can be reduced by <img src="https://render.githubusercontent.com/render/math?math=\Delta v"> with probability <img src="https://render.githubusercontent.com/render/math?math=p">; speed remains unchanged if <img src="https://render.githubusercontent.com/render/math?math=v_n=0">:
  
    <img src="https://render.githubusercontent.com/render/math?math=v_n\overset{p}{\longrightarrow}\max(v_n-\Delta v, 0)">.

* **Step 4:** *Movement.* Each car moves ahead by the number of cells corresponding to its new speed

    <img src="https://render.githubusercontent.com/render/math?math=x_n\longrightarrow\,x_n\,%2B\,v_n">.

Step 1 reflects the general tendency of the drivers to move as fast as possible without exceeding the maximum admissible speed. Step 2 ensures that crashes will not occur. Step 3 introduces an element of stochasticity, and could be modelled for taking into consideration the differences in drivers' behaviour, that are more or less aggressive/reactive.

TODO:

## Implementation

## Results

## How to use
