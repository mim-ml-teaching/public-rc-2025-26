import numpy as np
import pandas as pd
import cv2
import math
import tyro
import mujoco
from typing import Optional
from mujoco import viewer
from drone_simulator import DroneSimulator
from pid import PID
from plotting import plot_results
# TODO: Additional imports if needed
# END OF TODO

# Simulation parameters
resolution = (480, 640)  # (height, width) in pixels
fovy_deg = 90  # vertical field of view in degrees
np.set_printoptions(suppress=True, precision=3)
pd.set_option('display.float_format', lambda x: f'{x:.3f}')

# TODO: Additional functions if needed

# END OF TODO


def camera_intrinsics_from_fovy(fovy_deg: float, height: int, width: int) -> np.ndarray:
    fy = (height / 2.0) / math.tan(math.radians(fovy_deg) / 2.0)
    K = np.array([[fy, 0,  width / 2.0],
                  [0,  fy, height / 2.0],
                  [0,   0,  1]])
    return K


def update_gate_position(model: mujoco.MjModel, data: mujoco.MjData, gate_name: str, gate_vel: np.ndarray, 
                         gate_motion_prob: float = 0.1,
                         gate_motion_scale: float = 0.1, 
                         gate_noise_scale: float = 0.005, 
                         gate_damping: float = 0.95,
                         sim_dt: Optional[float] = None) -> np.ndarray:
    """Update gate position with smooth motion dynamics."""
    if sim_dt is None:
        sim_dt = model.opt.timestep
    gate_id = model.body(gate_name).id

    # Random impulse
    if np.random.uniform() < gate_motion_prob:
        impulse = np.random.normal(scale=gate_motion_scale, size=3)
        gate_vel += impulse
    
    # Add noise and apply damping
    gate_vel += np.random.normal(scale=gate_noise_scale, size=3)
    gate_vel *= gate_damping
    
    # Integrate to new position
    cur_pos = data.body(gate_name).xpos.copy()
    new_pos = cur_pos + gate_vel * sim_dt * [0.3, 1.0, 1.0]  # slower x motion
    
    # Keep gate within reasonable bounds
    new_pos[0] = np.clip(new_pos[0], -10.0, 2.0)  # x bounds
    new_pos[1] = np.clip(new_pos[1], -1.5, 1.5)   # y bounds
    new_pos[2] = np.clip(new_pos[2], 0.5, 5)      # z bounds
    
    # Apply to model
    model.body_pos[gate_id] = new_pos
    
    return gate_vel


def build_world(rotated_gates: bool) -> str:
    world = open("scene.xml").read()


        # Use random starting positions
    world = world.replace(
        '<body name="red_gate" pos="-2 0 3">',
        f'<body name="red_gate" pos="-2 {np.random.uniform(-0.6, 0.6)} {np.random.uniform(2.7, 3.3)}">'
    )
    
    world = world.replace(
        '<body name="green_gate" pos="-4 -0.6 3.3">',
        f'<body name="green_gate" pos="-4 {np.random.uniform(-0.6, 0.6)} {np.random.uniform(2.7, 3.3)}">'
    )
    world = world.replace(
        '<body name="blue_gate" pos="-6 0.6 2.7">',
        f'<body name="blue_gate" pos="-6 {np.random.uniform(-0.6, 0.6)} {np.random.uniform(2.7, 3.3)}">'
    )

    if rotated_gates:
        world = world.replace(
            '<body name="red_gate"',
            f'<body name="red_gate" euler="0 0 {np.random.uniform(-30, -15) if np.random.rand() < 0.5 else np.random.uniform(15, 30)}"'
        )
        world = world.replace(
            '<body name="green_gate"',
            f'<body name="green_gate" euler="0 0 {np.random.uniform(-30, -15) if np.random.rand() < 0.5 else np.random.uniform(15, 30)}"'
        )
        world = world.replace(
            '<body name="blue_gate"',
            f'<body name="blue_gate" euler="0 0 {np.random.uniform(-30, -15) if np.random.rand() < 0.5 else np.random.uniform(15, 30)}"'
        )
    return world


def run_single_task(*, wind: bool, rotated_gates: bool, flight_mode, rendering_freq: float) -> None:
    world = build_world(rotated_gates)
    model = mujoco.MjModel.from_xml_string(world)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    view = viewer.launch_passive(model, data)
    view.cam.type = mujoco.mjtCamera.mjCAMERA_FIXED
    view.cam.fixedcamid = model.camera("front_camera").id

    K = camera_intrinsics_from_fovy(fovy_deg, resolution[0], resolution[1])
    dist_coeffs = np.zeros(5)
    desired_thrust = 3.2496
    roll_thrust, pitch_thrust, yaw_thrust = 0.0, 0.0, 0.0

    SIM_TIME = 500 if flight_mode == "hover" else 5000

    pnp_position_list = []  # Store PnP position estimates
    true_position_list = []  # Store true gate positions
    kalman_position_list = []  # Store KF filtered positions
    # TODO: Additional variables if needed
    pnp_position = np.zeros(3)
    kalman_position = np.zeros(3)
    current_marker = 0
    
    # END OF TODO

    task_label = f"rotated={'yes' if rotated_gates else 'no'}, wind={'yes' if wind else 'no'}, flight_mode={flight_mode}"
    print(f"Starting task ({task_label})")

    wind_change_prob = 0.1 if wind else 0

    # If you want the simulation to be displayed more slowly, decrease rendering_freq
    # Note that this DOES NOT change the timestep used to approximate the physics of the simulation!
    drone_simulator = DroneSimulator(
        model, data, view, wind_change_prob = wind_change_prob, rendering_freq = rendering_freq
    )

    # --- initiate motion for all 3 gates ---
    red_gate_vel = np.zeros(3, dtype=float)
    green_gate_vel = np.zeros(3, dtype=float)
    blue_gate_vel = np.zeros(3, dtype=float)
    # ---------------------------------------

    renderer = None
    try:
        renderer = mujoco.Renderer(model, resolution[0], resolution[1])
        for i in range(SIM_TIME):
            # ----- update smooth motion of all 3 gates -----
            # Move the gates only in "hover" mode
            if flight_mode == "hover":
                red_gate_vel = update_gate_position(model, data, "red_gate", red_gate_vel)
                green_gate_vel = update_gate_position(model, data, "green_gate", green_gate_vel)
                blue_gate_vel = update_gate_position(model, data, "blue_gate", blue_gate_vel)
            mujoco.mj_forward(model, data)
            # -----------------------------------------------
            
            # Render camera frame
            renderer.update_scene(data, camera="front_camera")
            camera_frame = renderer.render()
            camera_frame = np.asarray(camera_frame, dtype=np.uint8)

            # Get current orientation
            current_orien, _ = drone_simulator.orientation_sensor()

            drone_position = drone_simulator.position_sensor()[0]
            if current_marker == 0:
                gate_position = data.body("red_gate").xpos.copy()
            elif current_marker == 4:
                gate_position = data.body("green_gate").xpos.copy()
            elif current_marker == 8:
                gate_position = data.body("blue_gate").xpos.copy()

            # You can use true_position as ground truth for debugging purposes
            true_position = gate_position - drone_position
            #print(f"true_position: {true_position.round(3)}")

            # TODO: Detect, estimate pose, apply Kalman filter

            # END OF TODO

            if pnp_position is not None:
                pnp_position_list.append(pnp_position.copy())
                kalman_position_list.append(kalman_position.copy())
                true_position_list.append(true_position.copy())


            # Make a simulation step
            drone_simulator.sim_step(
                desired_thrust, roll_thrust,
                pitch_thrust, yaw_thrust
            )

        # Plot the results
        rotated_str = "rotated" if rotated_gates else "straight"
        mode_str = "flight" if flight_mode == "flight" else "hover"
        filename = f"plot_{rotated_str}_{mode_str}.png"
        plot_results(pnp_position_list, true_position_list, kalman_position_list, filename=filename)

        print(f"Task ({task_label}) completed successfully!")

    finally:
        # Ensure renderer and viewer are closed before the next run to avoid multiple open windows.
        if renderer is not None:
            try:
                renderer.close()
            except Exception:
                pass
        try:
            view.close()
        except Exception:
            pass
    


def main(
    wind: bool = False,
    rotated_gates: bool = False,
    all_tasks: bool = True,
    runs: int = 1,
    rendering_freq: float = 1
) -> None:
    """
    Run the drone control simulation.

    Args:
        wind: Enable wind disturbances.
        rotated_gates: Rotate gates to create the harder variant.
        all_tasks: Run all four combinations of wind/rotated gates.
        runs: How many times to repeat each selected task.
        rendering_freq: Viewer rendering frequency multiplier (lower slows playback).
    """
    task_list = []
    if all_tasks:
        task_list = [
            (False, False, "hover"),
            (False, True, "hover"),
        ]
    else:
        task_list = [(False, False, "hover")] # the easiest setup

    for wind_flag, rotated, flight_mode in task_list:
        for run_idx in range(runs):
            print(f"\nRun {run_idx + 1}/{runs} for wind={wind_flag}, rotated_gates={rotated}, flight_mode={flight_mode}")
            run_single_task(
                wind=wind_flag,
                rotated_gates=rotated,
                flight_mode=flight_mode,
                rendering_freq=rendering_freq
            )


if __name__ == '__main__':
    tyro.cli(main)
