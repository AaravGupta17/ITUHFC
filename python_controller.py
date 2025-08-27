# ==============================================================================
# HOW THIS SYSTEM PERFORMS THE MISSION
# ==============================================================================
# This Python script acts as the "brain" of the robot. It contains all the
# high-level logic and strategy for the mission.
#
# 1. The `Robot` class (from `src/logic/robot.py`) defines the sequence of
#    actions for the "sow" and "harvest" missions based on the mission rules.
#
# 2. The kinematics module (`src/kinematics/`) calculates the 3D path and
#    joint angles needed for each movement.
#
# 3. This script sends very simple commands (e.g., "B,90.5") over the USB
#    serial port to the Arduino.
#
# 4. The Arduino acts as the "muscle", receiving these simple commands and
#    translating them into the low-level electrical signals to move the motors.
#
# The speed of the mission is NOT limited by this Python script; it is
# limited by how fast the physical motors can move. See the comments in the
# `robot_arm_controller.ino` file for how to tune the motor speed using the
# AccelStepper library to meet the 2-minute time limit.
# ==============================================================================

import serial
import time

from src.logic.robot import Robot
from src.hardware.serial_hardware import SerialStepper, SerialGripper
from src.hardware.mock_hardware import (
    MockStepper, MockGripper, MockColorSensor,
    RIPE_COLOR, UNRIPE_COLOR, ROTTEN_COLOR
)

# --- Configuration ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
UPPER_ARM_LENGTH = 0.5
FOREARM_LENGTH = 0.5
ACTIVE_PLOTS = ['orange']

def main():
    """
    Main function to initialize the serial connection and run the robot.
    """
    print("--- Python Robot Controller ---")

    # In a real scenario, you would connect to the Arduino.
    # For this simulation, we will comment out the serial connection
    # and use the MockBase to simulate driving.
    # try:
    #     ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    #     time.sleep(2)
    # except serial.SerialException as e:
    #     print(f"Error: Could not open serial port {SERIAL_PORT}.")
    #     return
    ser = None # Placeholder for the serial object

    # Initialize all robot components
    # Using mocks for everything to run a full simulation without hardware.
    base_stepper = MockStepper(200)
    shoulder_stepper = MockStepper(200)
    elbow_stepper = MockStepper(200)
    gripper = MockGripper()
    color_sensor = MockColorSensor()

    # Create a robot instance
    robot = Robot(
        base_stepper=base_stepper,
        shoulder_stepper=shoulder_stepper,
        elbow_stepper=elbow_stepper,
        gripper=gripper,
        color_sensor=color_sensor,
        upper_arm_length=UPPER_ARM_LENGTH,
        forearm_length=FOREARM_LENGTH,
        active_plots=ACTIVE_PLOTS,
    )

    # --- Run the robot's program ---
    # Configure the mock sensor for the harvest mission
    color_sensor.read_color = lambda: RIPE_COLOR

    # Run the full, integrated mission
    robot.full_mission()

    print("\n--- Simulation Complete ---")
    # if ser:
    #     ser.close()


if __name__ == "__main__":
    main()
