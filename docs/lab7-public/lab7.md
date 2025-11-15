---
title: Lab 7
usemathjax: true
---

<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>

# Why this lab?
We begin with linearizing nonlinear systems around their fixed points to build intuition about local behaviour and solve small analytical questions. We then switch gears to a short introduction to numerical integration, because even when no fixed point is nearby we still need reliable tools to simulate the nonlinear dynamics.

# Linearization of non-linear dynamics around fixed points

Find fixed points of the following systems and linearize their dynamics around these fixed points, i.e.:

- given a system $\dot{x} = f(x)$, find $\overline{x}$ such that $f(\overline{x})=0$ and 
- formulate approximate dynamics $\dot{\Delta x} = A ⋅ \Delta x$, where $A$ is the matrix you need to find and $\Delta x=x-\overline{x}$.

[Notes with solutions and hints](linearization-solutions.pdf).

## System 1

Consider the following 1-dimensional system that can be used to model population growth. Here, $x$ is the population size, and $P_{max}$ is the population limit above which resources become scarce.

$$\dot{x} = f(x) = x(P_{max}-x)$$

## System 2

Damped pendulum can be modeled with the following equation: 

$$\ddot{\theta} = -\sin(\theta) - \delta\dot{\theta}$$

where $\theta$ denotes the angle and $\delta$ is the damping coefficient.

_Hint_: rewrite the second-order equation as a first-order system before linearizing.

## System 3

In the following system you can assume $-\pi \le \theta \le \pi$.


$$\dot{r} = r^2 - r$$

$$\dot{\theta} = \sin^2(\theta / 2)$$


## System 4

$$\begin{pmatrix}\dot{x} \\ \dot{y}\end{pmatrix} = 
\begin{pmatrix}x(3-x-2y)\\ y(2-x-y)\end{pmatrix}$$

## System 5

A mass-spring system is subject to damping and a nonlinear restoring force, modeled by the equation:

$$\ddot{z} + 2\beta\dot{z} + \alpha z + \gamma z^2 = 0$$

where:
* $z(t)$ - displacement,
* $\beta = 0.5$ - damping coefficient,
* $\alpha = 1$ - linear stiffness coefficient,
* $\gamma = 1$ - nonlinear coefficient.

# Beyond Fixed Points: Numerical Integration
Linearization only answers local questions.
To study the full trajectory of a nonlinear system we rely on numerical integration.
In the following section we explore: 

 - how a simple Forward Euler scheme works;
 - the impact of the timestep size in simulations.

## Manual simulation step

Let $x(t)$ be the state of some system.
If the system evolves according to $\dot{x} = f(x)$ and the timestep is $\Delta t$,
the Forward Euler integration scheme is given by:

$$x_{i+1} = x_i + \Delta t f(x_i)$$

For System 5 form the part on linearization,
perform a few simulation steps using the Forward Euler method with a timestep $\Delta t = 0.1$,
starting at the fixed points and some other points.

Will the system stay at the fixed points during the simulation?
Why or why not?
Does the result depend on the choice of the timestep?
How does the behaviour at the fixed points compare to that from any other initial state?

## Does this matter in real simulations?
When we increase the timestep, we speed up the simulation, but we also decrease its accuracy.
With a sufficiently large timestep, unexpected things might happen.
Objects may pass through each other,
or collisions can launch objects in random directions at high velocities.
Depending on the purpose of the simulation, it is important to adjust the timestep parameter.

In the `timestep.py` file, you are given a very simple system with a ball bouncing on a plane.
The simulated bouncing is near-perfect, and thus the ball will bounce forever.

Run the program and observe the behaviour of the ball.
Then increase the `TIMESTEP` variable and see how this affects the system.
What is the threshold at which the physics seem to change?
