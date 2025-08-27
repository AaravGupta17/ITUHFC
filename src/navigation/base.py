from abc import ABC, abstractmethod

class MobileBase(ABC):
    """
    Abstract base class for the robot's mobile base.
    Defines the interface for navigation and movement.
    """

    @abstractmethod
    def drive_to(self, x: float, y: float):
        """
        Drives the robot's base to the specified (x, y) coordinate on the field.
        This method should handle path planning and motor control.
        """
        pass

    @abstractmethod
    def rotate_to(self, angle: float):
        """
        Rotates the robot's base to face a specific angle in degrees.
        0 degrees could be facing the opponent's side, for example.
        """
        pass

    @abstractmethod
    def get_position(self) -> tuple[float, float, float]:
        """
        Returns the current estimated position and orientation of the robot.

        Returns:
            A tuple (x, y, angle_degrees).
        """
        pass
