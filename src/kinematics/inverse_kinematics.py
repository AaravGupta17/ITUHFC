import math

def calculate_angles(x: float, y: float, l1: float, l2: float) -> tuple[float, float]:
    """
    Calculates the angles of the shoulder and elbow joints for a 2-link arm.

    Args:
        x: The x-coordinate of the target.
        y: The y-coordinate of the target.
        l1: The length of the upper arm.
        l2: The length of the forearm.

    Returns:
        A tuple containing the shoulder angle (theta1) and elbow angle (theta2) in radians.
    """
    # Distance from origin to target
    d_squared = x**2 + y**2
    d = math.sqrt(d_squared)

    # Check if the target is reachable
    if d > l1 + l2:
        raise ValueError("Target is out of reach")

    # Elbow angle (theta2)
    cos_theta2 = (d_squared - l1**2 - l2**2) / (2 * l1 * l2)
    # Ensure the value is within the domain of acos
    if cos_theta2 > 1.0:
        cos_theta2 = 1.0
    elif cos_theta2 < -1.0:
        cos_theta2 = -1.0

    theta2 = math.acos(cos_theta2)

    # Shoulder angle (theta1)
    alpha = math.atan2(y, x)
    beta = math.acos((d_squared + l1**2 - l2**2) / (2 * d * l1))
    theta1 = alpha - beta

    return theta1, theta2
