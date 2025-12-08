from dataclasses import dataclass
from typing import List, Tuple

# Type alias for clarity
Pose1D = float
Point2D = Tuple[float, float]

Pose2D = Tuple[Point2D, float]  # ((x, y), theta)


@dataclass
class OdometryMeasurement:
    step_index: int
    delta_x: float
    delta_y: float
    delta_theta: float


@dataclass
class SensorMeasurement:
    pose_index: int
    distances: List[float]
    angles: List[float]
