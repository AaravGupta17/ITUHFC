from typing import Tuple
from src.hardware.stepper import Stepper
from src.hardware.gripper import Gripper
from src.hardware.color_sensor import ColorSensor

class MockStepper(Stepper):
    def move_to_angle(self, angle: float) -> bool:
        print(f"Stepper moving to {angle} degrees.")
        self.current_angle = angle
        return True

    def home(self) -> bool:
        print("Stepper homing.")
        self.current_angle = 0.0
        return True

class MockGripper(Gripper):
    def __init__(self):
        self.fail_next_action = False

    def open(self) -> bool:
        if self.fail_next_action:
            print("Gripper failed to open.")
            self.fail_next_action = False
            return False
        print("Gripper opening.")
        return True

    def close(self) -> bool:
        if self.fail_next_action:
            print("Gripper failed to close.")
            self.fail_next_action = False
            return False
        print("Gripper closing.")
        return True

class MockColorSensor(ColorSensor):
    def __init__(self, color_to_return: Tuple[int, int, int] = (0, 0, 0)):
        self._color = color_to_return

    def read_color(self) -> Tuple[int, int, int]:
        print(f"Color sensor reading: {self._color}")
        return self._color
