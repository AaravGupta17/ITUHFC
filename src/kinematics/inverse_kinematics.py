import math
from typing import Tuple

def _calculate_2d_angles(
    x: float, y: float, l1: float, l2: float
) -> Tuple[float, float]:
    """
    Internal helper to calculate shoulder and elbow angles for a 2-link arm in a 2D plane.
    """
    # Distance from origin (shoulder joint) to target
    d_squared = x**2 + y**2
    d = math.sqrt(d_squared)

    # Check if the target is reachable
    if d > l1 + l2:
        raise ValueError("Target is out of reach")
    # Check if target is too close
    if d < abs(l1 - l2):
        raise ValueError("Target is too close to reach")

    # Elbow angle (theta2) using Law of Cosines
    # (d^2 = l1^2 + l2^2 - 2*l1*l2*cos(pi - theta2))
    # cos(pi - theta2) = -cos(theta2)
    cos_theta2 = (d_squared - l1**2 - l2**2) / (2 * l1 * l2)

    # Clamp the value to handle potential floating point inaccuracies
    cos_theta2 = max(-1.0, min(1.0, cos_theta2))

    theta2 = math.acos(cos_theta2)

    # Shoulder angle (theta1) using Law of Cosines
    alpha = math.atan2(y, x)
    # Clamp the value for beta calculation
    cos_beta = (d_squared + l1**2 - l2**2) / (2 * d * l1)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)

    # We choose the "elbow up" configuration
    theta1 = alpha - beta

    return theta1, theta2

def calculate_angles_3d(
    x: float, y: float, z: float, l1: float, l2: float
) -> Tuple[float, float, float]:
    """
    Calculates the angles for a 3-axis robotic arm (base, shoulder, elbow).

    Args:
        x: The x-coordinate of the target.
        y: The y-coordinate of the target.
        z: The z-coordinate of the target (height).
        l1: The length of the upper arm (shoulder to elbow).
        l2: The length of the forearm (elbow to gripper).

    Returns:
        A tuple containing the base, shoulder, and elbow angles in radians.
    """
    # Base angle (rotation around Z-axis)
    base_angle = math.atan2(y, x)

    # Reduce to a 2D problem in the vertical plane
    # r is the horizontal distance from the base to the target
    r = math.sqrt(x**2 + y**2)

    # The 2D problem is to reach point (r, z)
    # Note: We assume the shoulder joint is at the origin (0,0) of this plane.
    # If the shoulder joint has a height offset from the base, z would need adjustment.
    # For now, we assume z is relative to the shoulder joint.
    shoulder_angle, elbow_angle = _calculate_2d_angles(r, z, l1, l2)

    return base_angle, shoulder_angle, elbow_angle
