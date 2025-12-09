import math
import random
from typing import List, Tuple

from .models import OdometryMeasurement, Point2D, Pose1D, SensorMeasurement


class SLAMFrontend:
    """
    Simulates the environment and the robot's sensors.
    Generates ground truth data and noisy measurements.
    """

    def __init__(
        self,
        initial_pose: Pose1D = 0.0,
        num_steps: int = 3,
        odometry_noise_std: float = 0.0,
        sensor_noise_std: float = 0.0,
        initial_guess_std: float = 0.1,
    ):
        self.initial_pose = initial_pose
        self.num_steps = num_steps
        self.odometry_noise_std = odometry_noise_std
        self.sensor_noise_std = sensor_noise_std
        self.initial_guess_std = initial_guess_std

        self.true_poses: List[Pose1D] = []
        self.true_landmarks: List[Point2D] = []

        # Measurements (potentially noisy)
        self.odometry_measurements: List[OdometryMeasurement] = []
        self.sensor_measurements: List[SensorMeasurement] = []

    def add_landmark(self, x: float, y: float):
        self.true_landmarks.append((x, y))

    def generate_ground_truth(self) -> None:
        """Generates the true trajectory of the robot."""
        self.true_poses = [self.initial_pose]
        for _ in range(self.num_steps):
            # Simple logic: move +1 at each step
            self.true_poses.append(self.true_poses[-1] + 1.0)

    def generate_measurements(self) -> None:
        """
        Generates odometry and sensor measurements based on ground truth,
        applying specified noise.
        """
        if not self.true_poses:
            raise ValueError(
                "Ground truth not generated. Call generate_ground_truth() first."
            )

        # 1. Generate Odometry (Movements)
        true_odometry = []
        for i in range(len(self.true_poses) - 1):
            true_odometry.append(self.true_poses[i + 1] - self.true_poses[i])

        self.odometry_measurements = [
            # In 1D case we only consider x shift, y and theta are set to zero
            OdometryMeasurement(
                step_index=i, 
                delta_x=delta_x + random.gauss(0, self.odometry_noise_std),
                delta_y=0.0, 
                delta_theta=0.0
            )
            for i, delta_x in enumerate(true_odometry)
        ]

        # 2. Generate Sensor Readings (Distances to landmarks)
        true_sensor_readings = []
        for pose in self.true_poses:
            distances = self._calculate_observations_for_pose(pose, self.true_landmarks)
            true_sensor_readings.append(distances)

        self.sensor_measurements = []
        for pose_idx, readings_at_pose in enumerate(true_sensor_readings):
            noisy_readings = SensorMeasurement(
                pose_index=pose_idx,
                distances=[
                    dist + random.gauss(0, self.sensor_noise_std)
                    for dist in readings_at_pose
                ],
                angles=[],  # No angles in 1D case
            )
            self.sensor_measurements.append(noisy_readings)

    @staticmethod
    def _calculate_observations_for_pose(
        current_pose_val: Pose1D, landmarks: List[Point2D]
    ) -> List[float]:
        """Calculates Euclidean distance from 1D pose to 2D landmarks."""
        distance_observations = []
        for lm in landmarks:
            # Robot is at (x, 0)
            dist = math.sqrt((lm[0] - current_pose_val) ** 2 + (lm[1] - 0.0) ** 2)
            distance_observations.append(dist)
        return distance_observations

    def get_initial_guess(self) -> Tuple[List[Pose1D], List[Point2D]]:
        """
        Returns an initial guess for the optimizer.
        Here we typically start with a perturbed version of true values or dead-reckoning.
        For this example, we'll start from a guess slightly perturbed from the true poses and
        true landmark locations.
        """
        # Perturb true poses for a better "guess" scenario than just true values
        perturbed_poses = [
            p + random.gauss(0, self.initial_guess_std) for p in self.true_poses
        ]

        # Perturb true landmark locations
        perturbed_landmarks_flat = []
        for lm in self.true_landmarks:
            perturbed_landmarks_flat.append(
                lm[0] + random.gauss(0, self.initial_guess_std)
            )
            perturbed_landmarks_flat.append(
                lm[1] + random.gauss(0, self.initial_guess_std)
            )

        return perturbed_poses, perturbed_landmarks_flat
