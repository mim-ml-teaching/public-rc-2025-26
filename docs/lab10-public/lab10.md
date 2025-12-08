# SLAM
The goal of this lab is to create a simple, 2D version of SLAM.

SLAM (Simultaneous Localization and Mapping) is a technique used to create a map of the environment and at the same time estimate the position of the robot in that environment. SLAM is often used in exploration and robotics problems, for example self-driving cars.

Formally, SLAM is defined as an optimization problem, where we want to minimize the cost function over the map of the environment and the agent's position with a given set of (usually noisy) observations.

## Dead reckoning
Dead reckoning is a technique of estimating the current position based only on sensors' estimates of speed and velocity. A good example would be a ship that has only a compass and measurement of its speed. Knowing the starting point of the ship, the navigator can try to estimate the current position. However, due to errors in measurements compounding over time, this is likely to result in a low-quality estimate.

## SLAM 1D
In `slam_core` directory there is an implementation of SLAM in the one-dimensional case. We assume that our agent is moving in a straight line and has access to (noisy) measurements of displacement and (again noisy) estimates of distances to some landmarks in the environment (in the ship's case those could be far-away small islands).

Run `slam1d.py` to create a visualization comparing dead reckoning and 1D SLAM estimations to ground truth. On the visualization, there are also landmark positions estimated by our algorithm. Notice their distance to the original landmarks.

![Example output of `slam1d.py`](./assets/slam1d_example_result.png)

The implementation consists of `Frontend`, which simulates the environment, agent's measurements (odometry) and sensor readings, and `Backend` which handles the optimization of the cost function to create a good estimate of the map and the agent's position. Read both of those implementations to understand their interfaces and functions.

## SLAM 2D
The main task for today is implementation of 2D SLAM. In `Frontend.SLAM2DFrontend` and `Backend.SLAM2DBackend` there are TODO sections which you should fill out in `slam_core/frontend.py` and `slam_core/backend.py`.

In this case we want to estimate not only the position of the robot but also its heading (rotation). You will have to take that into account when generating the data and optimizing the cost function. Running `slam2d.py` will produce a visualization of the robot's movement, dead reckoning estimation, and SLAM results.

Try out different trajectories of the robot and different levels of noise to see how this affects the results. Specifically, try increasing the odometry noise and see how SLAM is able to correct dead reckoning errors. Is the same true when increasing sensor noise? What happens if you add more landmarks to the environment?

![Example output of `slam2d.py`](./assets/slam2d_example_result.png)