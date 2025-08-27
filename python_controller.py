# ==============================================================================
# This Python script acts as the "brain" of the robot. It contains the
# competition timer, the strategy engine, and the main scheduler loop.
# ==============================================================================

import time
from typing import List, Dict, Optional
from unittest.mock import MagicMock

# In a real deployment, you would not mock the hardware.
# You would replace the mock imports with the serial hardware imports.
# import serial
# from src.hardware.serial_hardware import SerialStepper, SerialGripper

from src.logic.robot import Robot, PLOT_LOCATIONS, HARVEST_LOCATIONS, RIPE_COLOR, UNRIPE_COLOR
from src.hardware.mock_hardware import MockStepper, MockGripper, MockColorSensor

# --- Configuration ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
UPPER_ARM_LENGTH = 0.5
FOREARM_LENGTH = 0.5
COMPETITION_DURATION = 120 # seconds

# --- Task Definitions ---
# This is where we define all possible tasks the robot can perform,
# along with their scores and estimated times.
ALL_TASKS = []
for plot_name, location in PLOT_LOCATIONS.items():
    ALL_TASKS.append({
        "name": f"Sow plot {plot_name}",
        "type": "sow",
        "score": 5,
        "estimated_time": 15,
        "location": location,
    })

for i, location in enumerate(HARVEST_LOCATIONS):
    ALL_TASKS.append({
        "name": f"Harvest fruit at {location}",
        "type": "harvest",
        "score": 10, # Score for a ripe fruit
        "estimated_time": 20,
        "location": location,
    })

ALL_TASKS.append({
    "name": "Irrigate field",
    "type": "irrigate",
    "score": 30,
    "estimated_time": 25,
})


def select_best_task(tasks: List[Dict], time_remaining: float) -> Optional[Dict]:
    """
    A simple strategy engine to select the best task.
    Currently, it just picks the highest score task that fits in the time.
    A more advanced strategy could use score / time.
    """
    eligible_tasks = [t for t in tasks if t["estimated_time"] <= time_remaining]
    if not eligible_tasks:
        return None

    # Sort by score, highest first
    return sorted(eligible_tasks, key=lambda x: x["score"], reverse=True)[0]


def main():
    """
    Main function to initialize the robot and run the competition scheduler.
    """
    print("--- Python Robot Controller ---")

    # Initialize hardware (using mocks for simulation)
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
    )

    # Initialize the robot's physical systems
    robot.initialize()

    # --- Competition Loop ---
    start_time = time.time()
    time_remaining = COMPETITION_DURATION
    total_score = 0
    remaining_tasks = list(ALL_TASKS)

    # Configure the mock sensor for the harvest mission. In a real robot,
    # this would not be needed. Here we make the first fruit ripe, the second not.
    color_sensor.read_color = MagicMock(side_effect=[RIPE_COLOR, UNRIPE_COLOR])


    print(f"\n--- Starting Competition! Timer set for {COMPETITION_DURATION} seconds. ---")
    while time_remaining > 0:
        print(f"\nTime remaining: {time_remaining:.2f}s, Current Score: {total_score}")

        best_task = select_best_task(remaining_tasks, time_remaining)

        if not best_task:
            print("No more eligible tasks that can be completed in the remaining time. Ending run.")
            break

        print(f"Selected task: {best_task['name']} (Score: {best_task['score']}, Time: {best_task['estimated_time']}s)")

        # --- Execute the task with retry logic ---
        MAX_RETRIES = 2
        success = False
        for i in range(MAX_RETRIES + 1):
            if i > 0:
                print(f"Retrying task... (Attempt {i + 1}/{MAX_RETRIES + 1})")

            success = robot.execute_task(best_task)
            if success:
                break

        if success:
            total_score += best_task["score"]
            print(f"Task '{best_task['name']}' successful. New score: {total_score}")
        else:
            print(f"Task '{best_task['name']}' failed after {MAX_RETRIES} retries.")

        remaining_tasks.remove(best_task)

        # Update timer
        time_remaining = COMPETITION_DURATION - (time.time() - start_time)

    print(f"\n--- Competition Over! ---")
    print(f"Final Score: {total_score}")


if __name__ == "__main__":
    main()
