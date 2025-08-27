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

# --- Define constants for field locations (all in meters, in world coordinates from the robot's base) ---
# Heights
GROUND_HEIGHT = 0.0
TRAVEL_HEIGHT = 0.4
ELEVATED_PLATFORM_HEIGHT = 0.2

# Key Positions
ARM_NEUTRAL_POSITION = (0.2, 0.0, TRAVEL_HEIGHT) # Safe position for movement
CONTAINER_PICKUP_LOC = (0.3, -0.3, GROUND_HEIGHT + 0.05)

# Sowing locations
PLOT_LOCATIONS = {
    "orange": (0.5, -0.5, GROUND_HEIGHT),
    "green": (0.5, 0.5, GROUND_HEIGHT),
    # Add other plot locations here
}

# Harvesting locations
HARVEST_LOCATIONS = [
    (0.6, 0.2, ELEVATED_PLATFORM_HEIGHT),
    (0.6, 0.4, GROUND_HEIGHT),
    # Add other fruit locations here
]

# Drop-off locations
FRUIT_PIT_LOC = (0.3, 0.4, GROUND_HEIGHT + 0.1)
WASTE_PIT_LOC = (0.3, -0.4, GROUND_HEIGHT + 0.1)

# Irrigation locations
WATER_LEVER_START_LOC = (0.0, 0.5, 0.3)
WATER_LEVER_END_LOC = (0.0, 0.5, 0.1)


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
        """Initializes all components of the robot."""
        print("Initializing robot...")
        self.base_stepper.home()
        self.shoulder_stepper.home()
        self.elbow_stepper.home()
        self.gripper.open()
        self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

    def move_arm_to_xyz(self, x: float, y: float, z: float):
        """Moves the arm to a specific (x, y, z) coordinate in the world frame."""
        print(f"Arm moving to world ({x:.2f}, {y:.2f}, {z:.2f})")
        try:
            base, shoulder, elbow = calculate_angles_3d(x, y, z, self.l1, self.l2)
            self.base_stepper.move_to_angle(math.degrees(base))
            self.shoulder_stepper.move_to_angle(math.degrees(shoulder))
            self.elbow_stepper.move_to_angle(math.degrees(elbow))
        except ValueError as e:
            print(f"Error moving arm: {e}")

    def full_mission(self):
        """Executes the full autonomous mission."""
        print("\n--- STARTING FULL AUTONOMOUS MISSION ---")
        self.initialize()
        self.sow()
        self.irrigate()
        self.harvest()
        print("\n--- FULL MISSION COMPLETE ---")

    def sow(self):
        """Performs the sowing action for all active plots."""
        print("\n--- Starting Sowing Mission ---")
        for plot_name in self.active_plots:
            print(f"Sowing plot: {plot_name.upper()}")
            plot_location = PLOT_LOCATIONS.get(plot_name)
            if not plot_location:
                print(f"Warning: No location defined for plot '{plot_name}'. Skipping.")
                continue

            # 1. Grab container
            self.move_arm_to_xyz(*CONTAINER_PICKUP_LOC)
            self.gripper.close()
            self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

            # 2. Move to plot and release
            self.move_arm_to_xyz(*plot_location)
            self.gripper.open()
            self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

        print("\n--- Sowing Mission Complete ---")

    def harvest(self):
        """Performs harvesting and sorting for all predefined fruit locations."""
        print("\n--- Starting Harvesting Mission ---")
        for fruit_loc in HARVEST_LOCATIONS:
            print(f"Checking for fruit at {fruit_loc}")
            self.move_arm_to_xyz(*fruit_loc)

            color = self.color_sensor.read_color()
            if color == UNRIPE_COLOR:
                print("Fruit is unripe. Leaving it.")
                continue

            print("Fruit is ripe or rotten. Harvesting.")
            self.gripper.close()
            self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

            if color == RIPE_COLOR:
                print("Moving arm to fruit pit")
                self.move_arm_to_xyz(*FRUIT_PIT_LOC)
            else: # ROTTEN_COLOR or other
                print("Moving arm to waste pit")
                self.move_arm_to_xyz(*WASTE_PIT_LOC)

            self.gripper.open()
            self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

        print("\n--- Harvesting Mission Complete ---")

    def irrigate(self):
        """Moves the arm to operate the water lever."""
        print("\n--- Starting Irrigation Mission ---")
        print("Moving to water lever...")
        self.move_arm_to_xyz(*WATER_LEVER_START_LOC)
        self.gripper.close()
        print("Pulling water lever...")
        self.move_arm_to_xyz(*WATER_LEVER_END_LOC)
        self.gripper.open()
        self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)
        print("\n--- Irrigation Mission Complete ---")
