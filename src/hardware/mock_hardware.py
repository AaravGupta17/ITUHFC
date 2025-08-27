from typing import Tuple
from src.hardware.stepper import Stepper
from src.hardware.gripper import Gripper
from src.hardware.color_sensor import ColorSensor

class MockStepper(Stepper):
    def move_to_angle(self, angle: float):
        print(f"Stepper moving to {angle} degrees.")
        self.current_angle = angle

    def home(self):
        print("Stepper homing.")
        self.current_angle = 0.0

class MockGripper(Gripper):
    def open(self):
        print("Gripper opening.")

    def close(self):
        print("Gripper closing.")

class MockColorSensor(ColorSensor):
    def __init__(self, color_to_return: Tuple[int, int, int] = (0, 0, 0)):
        self._color = color_to_return

    def read_color(self) -> Tuple[int, int, int]:
        print(f"Color sensor reading: {self._color}")
        return self._color
