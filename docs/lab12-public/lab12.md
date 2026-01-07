# LQR control

<script type="text/javascript"
src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.3/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
In this class we will implement LQR control for a cartpole system. We will use the [control](https://python-control.readthedocs.io/) library to design the controller and simulate the system.

The lab consists of three parts:

1. We will use the `control` library for a simple linear system. Just to get a feel for the library.
2. We will use the `control` library for a cartpole system. We will use the linearized dynamics of the cartpole system. The system will be simulated using  <https://github.com/microsoft/cartpole-py/blob/main/cartpole.py> which is a Python implementation of the cartpole system from the Microsoft.
3. We will use the `control` library for a cartpole system simulated using MuJoCo.

In the second step, you need to linearize the cartpole system at a fixed point using the basic simulation source code you have. Then, employ this linearization in the third step.

## Part 1: Simple linear system

In the `tiny_lqr.py` file in this repo we simulate a simple linear system.
If you run the code, you should see the system state changes randomly.
We want to design a controller that stabilizes the system to the origin `[0,0]`.
You can use the `control` library to design the controller.

You should start by preparing the matrices for LQR controller and computing the gains.
This is an operation one has to do only once, so it can be done outside the loop.
Start with something simple.
Then you should use the gain `K` to stabilize the system.

Try to run the code.
Quite quickly you should get the system that stabilizes at the origin.

Check what happens if you change the cost matrices `Q` and `R`.
What happens if you increase the cost of the control signal `R`?
What happens if you increase the cost of the state `Q`?
You might want to make a plot of the state trajectory for different values of `Q` and `R`.

## Part 2: Cartpole system - using specific simulation code

In this part, we will use the cartpole system from Microsoft.
The code is available at <https://github.com/microsoft/cartpole-py/blob/main/cartpole.py>,
but we have included it here for convenience (with some minor modifications).

Your goal is to fill in the TODOs in the `simple-cartpole.py` file we provide you with.

The crucial part of the code is the `step` method of `CartPoleModel` that simulates the cartpole system.
The function takes a command as an input and returns the state of the system.

If you run the code with:

```python
uv run python simple-cartpole.py --no-force
```

you should see the cartpole system in action.
The flag `--no-force` indicates no controller, hence the system falls down.
The simulation stops when the pole angle is be greater than 45 degrees, as seen on a video below.

<video width="512" height="208" controls>
  <source src="simple-free.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

Check what happens if you change the initial cart position and pole angle.
What happens if you remove the noise from the force?
What happens if you change the mass of the cart or the pole?
What happens if you change the length of the pole?
What happens if you change the gravity constant?

Your task is to design an LQR controller that stabilizes the cartpole system to the origin.
The linearization should be done at a fixed point.
You should write a function that returns the matrices `A` and `B` of the linearized system.
You should know how to linearize the system from the previous classes.

(hint) You may find following equations usefull:

$$\ddot{\theta} = \frac{(M+m)g\sin\theta - \cos\theta \left[ F + ml\dot{\theta}^2 \sin\theta \right]}{\left( \frac{4}{3} \right)(M+m) - ml\cos^2\theta}$$

$$\ddot{x} = \frac{ \left\{ F + ml \left[ \dot{\theta}^2 \sin\theta - \ddot{\theta}\cos\theta \right] \right\} }{M+m}$$


After filling in the missing parts and running the script without the `--no-force` flag,
you should see the cartpole system stabilized to the origin as seen on a video below.

<video width="512" height="208" controls>
  <source src="simple-controlled.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

Please note, that system starts in -3 position, so it is not stabilized in the center.
Also note, that we limit the force to be between -1 and 1.

## Part 3: Cartpole system - using MuJoCo

In this part, we will use the cartpole system from MuJoCo. Cartpole XML is a modified version of the cartpole.xml from MuJoCo and is available in this repo with `mujoco_cartpole.xml` name. If you want to find mass of the cart and pole, you can do it by using `print(model.body_mass)` after loading the model.

Using the stub code from `mujoco_lqr.py`. You should be able to stabilize the cartpole system using MuJoCo. You don't need to change linearization code from the previous part. You should only change the simulation code.

You should see the cartpole system stabilized to the origin as seen on a video below. Note, that
at the beginning the system is not stabilized in the center because it takes 50 steps with force 0.03 as
in provided code.

<video width="500" height="400" controls>
  <source src="mujoco-controlled.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
