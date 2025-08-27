from abc import ABC, abstractmethod

class Stepper(ABC):
    def __init__(self, steps_per_rotation: int):
        self.steps_per_rotation = steps_per_rotation
        self.current_angle = 0.0

    @abstractmethod
    def move_to_angle(self, angle: float):
        """Moves the stepper motor to a specific angle."""
        pass

    @abstractmethod
    def home(self):
        """Moves the stepper to the home position (0 degrees)."""
        pass
