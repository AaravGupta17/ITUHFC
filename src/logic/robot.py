import math
from typing import Tuple, List, Dict

from src.hardware.stepper import Stepper
from src.hardware.gripper import Gripper
from src.hardware.color_sensor import ColorSensor
from src.kinematics.inverse_kinematics import calculate_angles_3d

# --- Define constants for colors ---
RIPE_COLOR = (255, 0, 0)
UNRIPE_COLOR = (0, 255, 0)
ROTTEN_COLOR = (0, 0, 0)

# --- Define constants for field locations (all in meters) ---
# Heights
GROUND_HEIGHT = 0.0
TRAVEL_HEIGHT = 0.4  # A safe height for moving across the field
ELEVATED_PLATFORM_HEIGHT = 0.2

# General Locations
NEUTRAL_POSITION = (0.2, 0.0, TRAVEL_HEIGHT) # A safe home/neutral position
CONTAINER_PICKUP_LOCATIONS = {
    "orange": (0.1, -0.3, GROUND_HEIGHT + 0.05),
    "gray": (0.1, 0.0, GROUND_HEIGHT + 0.05),
    "green": (0.1, 0.3, GROUND_HEIGHT + 0.05),
}

# Sowing Plot Locations
PLOT_LOCATIONS = {
    "orange": (0.5, -0.5, GROUND_HEIGHT),
    "gray": (0.5, 0.0, GROUND_HEIGHT),
    "green": (0.5, 0.5, GROUND_HEIGHT),
}

# Harvesting Locations
FRUITS_ROW_1 = [(0.6, 0.4, GROUND_HEIGHT), (0.7, 0.4, GROUND_HEIGHT)]
FRUITS_ROW_2_ELEVATED = [(0.6, 0.2, ELEVATED_PLATFORM_HEIGHT), (0.7, 0.2, ELEVATED_PLATFORM_HEIGHT)]
FRUITS_ROW_3 = [(0.6, 0.0, GROUND_HEIGHT), (0.7, 0.0, GROUND_HEIGHT)]
ALL_FRUIT_LOCATIONS = FRUITS_ROW_1 + FRUITS_ROW_2_ELEVATED + FRUITS_ROW_3

# Sorting Pit Locations
WASTE_PIT_LOCATION = (0.2, -0.4, GROUND_HEIGHT + 0.1)
FRUIT_PIT_LOCATION = (0.2, 0.4, GROUND_HEIGHT + 0.1)


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
        active_plots: List[str],
    ):
        self.base_stepper = base_stepper
        self.shoulder_stepper = shoulder_stepper
        self.elbow_stepper = elbow_stepper
        self.gripper = gripper
        self.color_sensor = color_sensor
        self.l1 = upper_arm_length
        self.l2 = forearm_length
        self.active_plots = active_plots

    def initialize(self):
        """Initializes the robot by homing all motors and moving to neutral."""
        print("Initializing and homing all motors...")
        self.base_stepper.home()
        self.shoulder_stepper.home()
        self.elbow_stepper.home()
        self.gripper.open()
        print("Moving to neutral position.")
        self.move_to_xyz(*NEUTRAL_POSITION)

    def move_to_xyz(self, x: float, y: float, z: float):
        """Moves the arm to a specific (x, y, z) coordinate."""
        print(f"Moving to ({x:.2f}, {y:.2f}, {z:.2f})")
        try:
            base, shoulder, elbow = calculate_angles_3d(x, y, z, self.l1, self.l2)
            self.base_stepper.move_to_angle(math.degrees(base))
            self.shoulder_stepper.move_to_angle(math.degrees(shoulder))
            self.elbow_stepper.move_to_angle(math.degrees(elbow))
        except ValueError as e:
            print(f"Error moving to ({x}, {y}, {z}): {e}")

    def sow(self):
        """Executes the sowing game plan using the container drop strategy."""
        print("\n--- Starting Sowing Mission ---")
        for plot_color in self.active_plots:
            print(f"\nSowing plot: {plot_color.upper()}")

            container_loc = CONTAINER_PICKUP_LOCATIONS[plot_color]
            plot_loc = PLOT_LOCATIONS[plot_color]

            # 1. Go to container pickup location
            self.move_to_xyz(container_loc[0], container_loc[1], TRAVEL_HEIGHT)
            self.move_to_xyz(*container_loc)

            # 2. Grab container
            print("Grabbing container...")
            self.gripper.close()

            # 3. Lift container and move to plot
            self.move_to_xyz(container_loc[0], container_loc[1], TRAVEL_HEIGHT)
            self.move_to_xyz(plot_loc[0], plot_loc[1], TRAVEL_HEIGHT)
            self.move_to_xyz(*plot_loc)

            # 4. Release seeds (open flap/gripper)
            print("Releasing seeds...")
            self.gripper.open()

            # 5. Return to neutral
            self.move_to_xyz(plot_loc[0], plot_loc[1], TRAVEL_HEIGHT)
            self.move_to_xyz(*NEUTRAL_POSITION)

        print("\n--- Sowing Mission Complete ---")

    def harvest(self):
        """Executes the harvesting game plan."""
        print("\n--- Starting Harvesting Mission ---")
        for fruit_location in ALL_FRUIT_LOCATIONS:
            print(f"\nApproaching fruit at ({fruit_location[0]:.2f}, {fruit_location[1]:.2f}, {fruit_location[2]:.2f})")
            self.move_to_xyz(*NEUTRAL_POSITION) # Go to neutral first
            self.move_to_xyz(fruit_location[0], fruit_location[1], fruit_location[2] + 0.1) # Approach from above
            self.move_to_xyz(*fruit_location)

            print("Sensing fruit color...")
            color = self.color_sensor.read_color()

            if color == UNRIPE_COLOR:
                print("Fruit is unripe (green), skipping.")
                continue

            print("Harvesting fruit...")
            self.gripper.close()
            self.move_to_xyz(fruit_location[0], fruit_location[1], TRAVEL_HEIGHT) # Lift it up

            if color == RIPE_COLOR:
                print("Fruit is ripe (red), moving to fruit pit.")
                self.move_to_xyz(*FRUIT_PIT_LOCATION)
            elif color == ROTTEN_COLOR:
                print("Fruit is diseased (black), moving to waste pit.")
                self.move_to_xyz(*WASTE_PIT_LOCATION)

            self.gripper.open()

        self.move_to_xyz(*NEUTRAL_POSITION)
        print("\n--- Harvesting Mission Complete ---")
