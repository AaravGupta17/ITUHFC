from src.navigation.base import MobileBase

class MockBase(MobileBase):
    """
    A mock implementation of the MobileBase for testing purposes.
    It simulates the robot's movement by printing actions and tracking state.
    """
    def __init__(self, start_x: float = 0.0, start_y: float = 0.0, start_angle: float = 0.0):
        self._x = start_x
        self._y = start_y
        self._angle = start_angle
        print(f"MockBase initialized at ({self._x}, {self._y}, {self._angle} deg)")

    def drive_to(self, x: float, y: float):
        """Simulates driving to a new coordinate."""
        print(f"MockBase: Driving from ({self._x:.2f}, {self._y:.2f}) to ({x:.2f}, {y:.2f})")
        self._x = x
        self._y = y

    def rotate_to(self, angle: float):
        """Simulates rotating to a new angle."""
        print(f"MockBase: Rotating from {self._angle:.2f} deg to {angle:.2f} deg")
        self._angle = angle

    def get_position(self) -> tuple[float, float, float]:
        """Returns the simulated current position."""
        return (self._x, self._y, self._angle)
