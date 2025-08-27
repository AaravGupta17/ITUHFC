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
    ):
        self.base_stepper = base_stepper
        self.shoulder_stepper = shoulder_stepper
        self.elbow_stepper = elbow_stepper
        self.gripper = gripper
        self.color_sensor = color_sensor
        self.l1 = upper_arm_length
        self.l2 = forearm_length

    def initialize(self):
        """Initializes all components of the robot."""
        print("Initializing robot...")
        self.base_stepper.home()
        self.shoulder_stepper.home()
        self.elbow_stepper.home()
        self.gripper.open()
        self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION)
        return True # Assume initialization is always successful for now

    def move_arm_to_xyz(self, x: float, y: float, z: float) -> bool:
        """
        Moves the arm to a specific (x, y, z) coordinate in the world frame.
        Returns True on success, False on failure.
        """
        print(f"Arm moving to world ({x:.2f}, {y:.2f}, {z:.2f})")
        try:
            base, shoulder, elbow = calculate_angles_3d(x, y, z, self.l1, self.l2)
            # In a real robot, these would return success/fail statuses
            self.base_stepper.move_to_angle(math.degrees(base))
            self.shoulder_stepper.move_to_angle(math.degrees(shoulder))
            self.elbow_stepper.move_to_angle(math.degrees(elbow))
            return True
        except ValueError as e:
            print(f"Error moving arm: {e}")
            return False

    def execute_task(self, task: Dict) -> bool:
        """
        Executes a single task dictionary.
        Returns True on success, False on failure.
        """
        task_type = task.get("type")
        print(f"\n--- Executing Task: {task.get('name')} ---")

        if task_type == "sow":
            return self._execute_sow_task(task)
        elif task_type == "harvest":
            return self._execute_harvest_task(task)
        elif task_type == "irrigate":
            return self._execute_irrigate_task(task)
        else:
            print(f"Unknown task type: {task_type}")
            return False

    def _execute_sow_task(self, task: Dict) -> bool:
        """Executes the sequence for a single sowing task."""
        plot_location = task.get("location")
        if not plot_location:
            print("Error: Sow task requires a 'location'.")
            return False

        # 1. Grab container
        if not self.move_arm_to_xyz(*CONTAINER_PICKUP_LOC): return False
        if not self.gripper.close(): return False
        if not self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION): return False

        # 2. Move to plot and release
        if not self.move_arm_to_xyz(*plot_location): return False
        if not self.gripper.open(): return False
        if not self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION): return False

        return True

    def _execute_harvest_task(self, task: Dict) -> bool:
        """Executes the sequence for a single harvesting task."""
        fruit_loc = task.get("location")
        if not fruit_loc:
            print("Error: Harvest task requires a 'location'.")
            return False

        if not self.move_arm_to_xyz(*fruit_loc): return False

        color = self.color_sensor.read_color()
        if color == UNRIPE_COLOR:
            print("Fruit is unripe. Leaving it. Task considered successful.")
            return True # Not a failure, just nothing to do

        print("Fruit is ripe or rotten. Harvesting.")
        if not self.gripper.close(): return False
        if not self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION): return False

        drop_loc = FRUIT_PIT_LOC if color == RIPE_COLOR else WASTE_PIT_LOC
        print(f"Moving arm to {'fruit pit' if color == RIPE_COLOR else 'waste pit'}")
        if not self.move_arm_to_xyz(*drop_loc): return False

        if not self.gripper.open(): return False
        if not self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION): return False
        return True

    def _execute_irrigate_task(self, task: Dict) -> bool:
        """Executes the sequence for an irrigation task."""
        print("Moving to water lever...")
        if not self.move_arm_to_xyz(*WATER_LEVER_START_LOC): return False
        if not self.gripper.close(): return False
        print("Pulling water lever...")
        if not self.move_arm_to_xyz(*WATER_LEVER_END_LOC): return False
        if not self.gripper.open(): return False
        if not self.move_arm_to_xyz(*ARM_NEUTRAL_POSITION): return False
        return True
