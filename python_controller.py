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
# Note: The ColorSensor is not included in this physical setup yet.
# We would need a real implementation for it, e.g., SerialColorSensor.
# For now, we will use the MockColorSensor to simulate its input.
from src.hardware.mock_hardware import MockColorSensor, RIPE_COLOR, UNRIPE_COLOR, ROTTEN_COLOR

# --- Configuration ---
# Update this to your Arduino's serial port
SERIAL_PORT = '/dev/ttyACM0'  # Example for Linux. On Windows, it might be 'COM3'
BAUD_RATE = 9600

# Robot arm dimensions (in meters)
UPPER_ARM_LENGTH = 1.0
FOREARM_LENGTH = 1.0

# Mission parameters
# The two plots that are active for this match
ACTIVE_PLOTS = ['orange', 'green']

def main():
    """
    Main function to initialize the serial connection and run the robot.
    """
    print("--- Python Robot Controller ---")

    try:
        # Initialize serial connection
        print(f"Connecting to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        # Wait for the Arduino to reset
        time.sleep(2)
        print("Connection successful.")
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}.")
        print(f"Please check that the Arduino is connected and the port is correct.")
        print(e)
        return

    # Initialize hardware interfaces with the serial connection
    base_stepper = SerialStepper(ser, 'B')
    shoulder_stepper = SerialStepper(ser, 'S')
    elbow_stepper = SerialStepper(ser, 'E')
    gripper = SerialGripper(ser, 'G')

    # We don't have a physical color sensor connected via serial yet,
    # so we'll use the mock one to provide simulated data for the logic.
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
    # The robot will now send commands to the Arduino

    # Initialize to home positions
    robot.initialize()

    # Run the sowing mission
    robot.sow()

    # Run the harvesting mission
    # For demonstration, we'll configure the mock sensor to return a sequence of colors
    color_sensor._color_sequence = [
        RIPE_COLOR, ROTTEN_COLOR,
        UNRIPE_COLOR, RIPE_COLOR,
        UNRIPE_COLOR, ROTTEN_COLOR
    ]
    # We also need to modify the mock sensor to use this sequence
    def read_color_from_sequence(self):
        if hasattr(self, '_color_sequence') and self._color_sequence:
            color = self._color_sequence.pop(0)
            print(f"Simulated color sensor reading: {color}")
            return color
        return (0,0,0) # Default

    MockColorSensor.read_color = read_color_from_sequence
    MockColorSensor._color_sequence = [
        RIPE_COLOR, ROTTEN_COLOR,
        UNRIPE_COLOR, RIPE_COLOR,
        UNRIPE_COLOR, ROTTEN_COLOR
    ]

    robot.harvest()

    print("\n--- All missions complete ---")
    ser.close()
    print("Serial port closed.")


if __name__ == "__main__":
    main()
