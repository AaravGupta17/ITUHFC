import math
from typing import Tuple

from src.hardware.stepper import Stepper
from src.hardware.gripper import Gripper
from src.hardware.color_sensor import ColorSensor
from src.kinematics.inverse_kinematics import calculate_angles

# Define constants for colors
RIPE_COLOR = (255, 0, 0)
UNRIPE_COLOR = (0, 255, 0)
ROTTEN_COLOR = (0, 0, 0)

# Define constants for locations (placeholders)
CRATE_GRIP_POINT = (0.2, 0.1)
BUTTON_1_LOCATION = (0.3, 0.2)
BUTTON_2_LOCATION = (0.3, 0.3)
REFILL_LOCATION = (0.1, 0.1)
LEVER_1_LOCATION = (0.4, 0.2)
LEVER_2_LOCATION = (0.4, 0.3)
FRUIT_LOCATIONS = [(0.5, 0.1), (0.5, 0.2), (0.5, 0.3)]
WASTE_PIT_LOCATION = (0.1, 0.4)
FRUIT_PIT_LOCATION = (0.2, 0.4)
NEUTRAL_POSITION = (0.2, 0.3) # A safe position to move to

class Robot:
    def __init__(
        self,
        base_stepper: Stepper,
        shoulder_stepper: Stepper,
        elbow_stepper: Stepper,
        gripper: Gripper,
        color_sensor: ColorSensor,
        upper_arm_length: float,
        forearm_length: float,
    ):
        self.base_stepper = base_stepper
        self.shoulder_stepper = shoulder_stepper
        self.elbow_stepper = elbow_stepper
        self.gripper = gripper
        self.color_sensor = color_sensor
        self.l1 = upper_arm_length
        self.l2 = forearm_length

    def initialize(self):
        """Initializes the robot by homing all motors."""
        self.base_stepper.home()
        self.shoulder_stepper.home()
        self.elbow_stepper.home()
        self.gripper.open()

    def move_to_xy(self, x: float, y: float):
        """Moves the arm to a specific (x, y) coordinate."""
        try:
            shoulder_angle_rad, elbow_angle_rad = calculate_angles(x, y, self.l1, self.l2)

            # Convert radians to degrees for the stepper motors
            shoulder_angle_deg = math.degrees(shoulder_angle_rad)
            elbow_angle_deg = math.degrees(elbow_angle_rad)

            self.shoulder_stepper.move_to_angle(shoulder_angle_deg)
            self.elbow_stepper.move_to_angle(elbow_angle_deg)
        except ValueError as e:
            print(f"Error moving to ({x}, {y}): {e}")

    def sow(self):
        """Executes the sowing game plan."""
        print("--- Starting Sowing ---")

        # This is a simplified version of the logic described.
        # A full implementation would require more state management (e.g. for button presses)
        # and timing (delays).

        print("Moving crate for the first time...")
        self.move_to_xy(*CRATE_GRIP_POINT)
        self.gripper.close()
        self.move_to_xy(*BUTTON_1_LOCATION) # Simplified: move to a location related to button 1

        print("Recalling crate to refill...")
        self.move_to_xy(*REFILL_LOCATION)

        print("Moving crate for the second time...")
        self.move_to_xy(*BUTTON_2_LOCATION) # Simplified: move to a location related to button 2

        print("Recalling crate and finishing...")
        self.move_to_xy(*REFILL_LOCATION)
        self.gripper.open()

        print("Working water levers...")
        self.move_to_xy(*LEVER_1_LOCATION)
        self.gripper.close()
        # Simulate moving down and up by just waiting
        self.move_to_xy(*LEVER_2_LOCATION)
        self.gripper.open()

        print("--- Sowing Complete ---")


    def harvest(self):
        """Executes the harvesting game plan."""
        print("--- Starting Harvesting ---")
        for fruit_location in FRUIT_LOCATIONS:
            self.move_to_xy(*NEUTRAL_POSITION)
            self.move_to_xy(*fruit_location)

            color = self.color_sensor.read_color()

            if color == UNRIPE_COLOR:
                print("Fruit is unripe, skipping.")
                continue

            self.gripper.close()
            self.move_to_xy(*NEUTRAL_POSITION)

            if color == RIPE_COLOR:
                print("Fruit is ripe, moving to fruit pit.")
                self.move_to_xy(*FRUIT_PIT_LOCATION)
            elif color == ROTTEN_COLOR:
                print("Fruit is rotten, moving to waste pit.")
                self.move_to_xy(*WASTE_PIT_LOCATION)

            self.gripper.open()

        self.move_to_xy(*NEUTRAL_POSITION)
        print("--- Harvesting Complete ---")
