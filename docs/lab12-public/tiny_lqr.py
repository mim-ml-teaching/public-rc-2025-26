"""
This script demonstrates the use of Linear Quadratic Regulator (LQR) for controlling a simple linear system.

Functions:
- measure_state: Returns the current state of the system.
- apply_control: Applies the control input to the system and updates its state.
- print_state: Prints the current state of the system.

Classes:
- System: Represents a simple linear system with methods to measure state, apply control, and print state.

Global Variables:
- A: System matrix.
- B: Input matrix.
- Q: State cost matrix.
- R: Control cost matrix.
- K: LQR controller gain.
"""
import random
import time

import control as ctrl
import numpy as np

# Define system matrices
A = np.array([[1, 2], [3, 4]])
B = np.array([[5], [6]])

# TODO: Define cost matrices

# TODO: Uncomment to compute LQR controller gain
# K, S, E = ctrl.lqr(A, B, Q, R)

# K is your controller gain
# print("Controller gain K:", K)


class System:
    def __init__(self):
        self.x = np.array([[1], [2]])  # Initial state

    def measure_state(self):
        return self.x

    def apply_control(self, u):
        dt = 0.01
        self.x = self.x + np.dot(A, self.x) * dt + np.dot(B, u) * dt

    def print_state(self):
        print(f"{self.x[0].item():.2f}, {self.x[1].item():.2f}")


system = System()

for _ in range(1000):
    # Measure or estimate the current state
    x = system.measure_state()

    # TODO: Calculate the control input and use it instead of random noise
    u = random.uniform(-1, 1)

    # Apply the control input to the system
    system.apply_control(u)

    # Wait for the system to react before next iteration
    # (This could be a time delay in a real-time system)
    time.sleep(0.01)

    # Print the current state
    system.print_state()
