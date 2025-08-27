import math
from typing import Tuple, List, Dict

from src.hardware.stepper import Stepper
from src.hardware.gripper import Gripper
from src.hardware.color_sensor import ColorSensor
from src.kinematics.inverse_kinematics import calculate_angles_3d
from src.navigation.base import MobileBase

# --- Define constants for colors ---
RIPE_COLOR = (255, 0, 0)
UNRIPE_COLOR = (0, 255, 0)
ROTTEN_COLOR = (0, 0, 0)

# --- Define constants for field locations (all in meters, in world coordinates) ---
# Heights
GROUND_HEIGHT = 0.0
TRAVEL_HEIGHT = 0.4
ELEVATED_PLATFORM_HEIGHT = 0.2

# Key Positions for Navigation
START_ZONE = (0.5, 0.2, 0) # x, y, angle
SOWING_STATION = (1.5, 0.5, 0) # Position to drive to for sowing
HARVESTING_STATION = (1.5, 2.5, 0) # Position to drive to for harvesting

# Locations relative to the robot's base when it is at a station
# The arm's reach is assumed to be relative to its own base.
ARM_NEUTRAL_POSITION = (0.2, 0.0, TRAVEL_HEIGHT)
CONTAINER_PICKUP_LOC_RELATIVE = (0.3, -0.3, GROUND_HEIGHT + 0.05)

PLOT_ORANGE_LOC_RELATIVE = (0.5, -0.5, GROUND_HEIGHT)
PLOT_GREEN_LOC_RELATIVE = (0.5, 0.5, GROUND_HEIGHT)

FRUIT_LOC_ELEVATED_RELATIVE = (0.6, 0.2, ELEVATED_PLATFORM_HEIGHT)
FRUIT_LOC_GROUND_RELATIVE = (0.6, 0.4, GROUND_HEIGHT)

FRUIT_PIT_LOC_RELATIVE = (0.3, 0.4, GROUND_HEIGHT + 0.1)
WASTE_PIT_LOC_RELATIVE = (0.3, -0.4, GROUND_HEIGHT + 0.1)


class Robot:
    def __init__(
        self,
        mobile_base: MobileBase,
        base_stepper: Stepper,
        shoulder_stepper: Stepper,
        elbow_stepper: Stepper,
        gripper: Gripper,
        color_sensor: ColorSensor,
        upper_arm_length: float,
        forearm_length: float,
        active_plots: List[str],
    ):
        self.mobile_base = mobile_base
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
        self.mobile_base.drive_to(START_ZONE[0], START_ZONE[1]) # Start in the start zone
        self.base_stepper.home()
        self.shoulder_stepper.home()
        self.elbow_stepper.home()
        self.gripper.open()
        self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

    def move_arm_to_xyz(self, x: float, y: float, z: float):
        """Moves the arm to a specific (x, y, z) coordinate RELATIVE TO THE ARM'S BASE."""
        print(f"Arm moving to relative ({x:.2f}, {y:.2f}, {z:.2f})")
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
        self.harvest()
        print("\n--- FULL MISSION COMPLETE ---")

    def sow(self):
        """Drives to the sowing station and performs the sowing action."""
        print("\n--- Starting Sowing Mission ---")
        self.mobile_base.drive_to(SOWING_STATION[0], SOWING_STATION[1])

        # This logic is now simplified as an example of one plot
        # A full implementation would loop through self.active_plots
        print(f"Sowing plot: {self.active_plots[0].upper()}")

        # 1. Grab container
        self.move_arm_to_xyz(*CONTAINER_PICKUP_LOC_RELATIVE)
        self.gripper.close()
        self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

        # 2. Move to plot and release
        self.move_arm_to_xyz(*PLOT_ORANGE_LOC_RELATIVE) # Example for orange
        self.gripper.open()
        self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

        print("\n--- Sowing Mission Complete ---")

    def harvest(self):
        """Drives to the harvesting station and performs harvesting."""
        print("\n--- Starting Harvesting Mission ---")
        self.mobile_base.drive_to(HARVESTING_STATION[0], HARVESTING_STATION[1])

        # This logic is now simplified to one example fruit
        self.move_arm_to_xyz(*FRUIT_LOC_ELEVATED_RELATIVE)

        color = self.color_sensor.read_color()
        if color != UNRIPE_COLOR:
            self.gripper.close()
            self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)
            if color == RIPE_COLOR:
                print("Moving arm to fruit pit")
                self.move_arm_to_xyz(*FRUIT_PIT_LOC_RELATIVE)
            else: # ROTTEN_COLOR
                print("Moving arm to waste pit")
                self.move_arm_to_xyz(*WASTE_PIT_LOC_RELATIVE)
            self.gripper.open()
            self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)

        print("\n--- Harvesting Mission Complete ---")
