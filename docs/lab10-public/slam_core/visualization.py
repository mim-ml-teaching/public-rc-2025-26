import math
from typing import List, Optional

import matplotlib.pyplot as plt

from .models import OdometryMeasurement, Point2D, Pose1D, Pose2D


def plot_results_1d(
    true_poses: List[Pose1D],
    true_landmarks: List[Point2D],
    odometry_measurements: List[OdometryMeasurement],
    optimized_poses: List[Pose1D],
    optimized_landmarks: List[Point2D],
    initial_pose: Pose1D = 0.0,
    save_path: Optional[str] = "slam1d_result.png",
):
    """
    Plots the ground truth, dead reckoning (from noisy odometry), and optimized results.
    """
    plt.figure(figsize=(10, 6))

    # 1. Plot True Data
    # Poses (y=0 for 1D)
    # We offset y slightly to visualize overlapping lines better if needed,
    # but standard plot order handles visibility.
    plt.plot(
        true_poses,
        [0] * len(true_poses),
        "g-o",
        label="Ground Truth Poses",
        markersize=10,
        linewidth=2,
        zorder=1,
    )

    # Landmarks
    if true_landmarks:
        lx, ly = zip(*true_landmarks)
        plt.scatter(
            lx, ly, c="g", marker="*", s=200, label="Ground Truth Landmarks", zorder=10
        )

    # 2. Plot Dead Reckoning (Odometry Integration)
    dr_poses = [initial_pose]
    current_pose = initial_pose
    for odom in odometry_measurements:
        current_pose += odom.delta_x
        dr_poses.append(current_pose)

    # Shift Y slightly for visibility
    plt.plot(
        dr_poses,
        [-0.05] * len(dr_poses),
        "r--x",
        label="Dead Reckoning (Noisy Odom)",
        alpha=0.6,
        zorder=2,
    )

    # 3. Plot Optimized Data
    plt.plot(
        optimized_poses,
        [0.05] * len(optimized_poses),
        "b-s",
        label="Optimized Poses",
        markersize=6,
        zorder=3,
    )

    if optimized_landmarks:
        ox, oy = zip(*optimized_landmarks)
        plt.scatter(
            ox,
            oy,
            c="b",
            marker="X",
            s=150,
            label="Optimized Landmarks",
            alpha=0.8,
            zorder=11,
        )

    plt.title("1D SLAM Results")
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.axhline(0, color="black", linewidth=0.5)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.axis("equal")  # Keep aspect ratio to judge distances correctly

    if save_path:
        print(f"Saving plot to {save_path}...")
        plt.savefig(save_path)
        print("Plot saved.")
    else:
        plt.show()


def plot_results_2d(
    true_poses: List[Pose2D],
    true_landmarks: List[Point2D],
    odometry_measurements: List[OdometryMeasurement],
    optimized_poses: List[Pose2D],
    optimized_landmarks: List[Point2D],
    initial_pose: Pose2D = ((0, 0), 0.0),
    save_path: Optional[str] = "slam2d_result.png",
    plot_headings: bool = True,
) -> None:
    """
    Plots the ground truth, dead reckoning (from noisy odometry), and optimized results.
    """
    plt.figure(figsize=(10, 6))

    # 1. Plot True Data
    xs = [p[0][0] for p in true_poses]
    ys = [p[0][1] for p in true_poses]
    thetas = [p[1] for p in true_poses]
    plt.plot(
        xs, ys, "g-o", label="Ground Truth Poses", markersize=10, linewidth=2, zorder=1
    )

    # Landmarks
    if true_landmarks:
        lx, ly = zip(*true_landmarks)
        plt.scatter(
            lx, ly, c="g", marker="*", s=200, label="Ground Truth Landmarks", zorder=10
        )

    if plot_headings:
        plt.quiver(
            xs,
            ys,
            [0.2 * math.cos(t) for t in thetas],
            [0.2 * math.sin(t) for t in thetas],
            angles="xy",
            scale_units="xy",
            scale=1,
            color="g",
            alpha=0.8,
            zorder=1,
            width=0.004,
        )

    # 2. Plot Dead Reckoning (Odometry Integration)

    current_x, current_y = initial_pose[0]
    current_theta = initial_pose[1]
    dr_xs = [current_x]
    dr_ys = [current_y]
    dr_thetas = [current_theta]

    for odom in odometry_measurements:
        delta_x = odom.delta_x
        delta_y = odom.delta_y
        delta_theta = odom.delta_theta

        rotated_dx = (
            math.cos(current_theta) * delta_x - math.sin(current_theta) * delta_y
        )
        rotated_dy = (
            math.sin(current_theta) * delta_x + math.cos(current_theta) * delta_y
        )

        current_x += rotated_dx
        current_y += rotated_dy
        current_theta += delta_theta
        dr_xs.append(current_x)
        dr_ys.append(current_y)
        dr_thetas.append(current_theta)

    plt.plot(
        dr_xs, dr_ys, "r--x", label="Dead Reckoning (Noisy Odom)", alpha=0.6, zorder=2
    )

    if plot_headings:
        plt.quiver(
            dr_xs,
            dr_ys,
            [0.2 * math.cos(t) for t in dr_thetas],
            [0.2 * math.sin(t) for t in dr_thetas],
            angles="xy",
            scale_units="xy",
            scale=1,
            color="r",
            alpha=0.6,
            zorder=2,
            width=0.004,
        )

    # 3. Plot Optimized Data
    optimized_poses = optimized_poses.reshape(-1, 3)
    plt.plot(
        optimized_poses[:, 0],
        optimized_poses[:, 1],
        "b-s",
        label="Optimized Poses",
        markersize=6,
        zorder=3,
    )

    if optimized_landmarks:
        ox, oy = zip(*optimized_landmarks)
        plt.scatter(
            ox,
            oy,
            c="b",
            marker="X",
            s=150,
            label="Optimized Landmarks",
            alpha=0.8,
            zorder=11,
        )

    if plot_headings:
        plt.quiver(
            optimized_poses[:, 0],
            optimized_poses[:, 1],
            [0.2 * math.cos(t) for t in optimized_poses[:, 2]],
            [0.2 * math.sin(t) for t in optimized_poses[:, 2]],
            angles="xy",
            scale_units="xy",
            scale=1,
            color="b",
            alpha=0.8,
            zorder=3,
            width=0.004,
        )

    plt.title("2D SLAM Results")
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.axis("equal")  # Keep aspect ratio to judge distances correctly

    if save_path:
        print(f"Saving plot to {save_path}...")
        plt.savefig(save_path)
        print("Plot saved.")
    else:
        plt.show()
