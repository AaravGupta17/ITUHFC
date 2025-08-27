from src.logic.robot import Robot
from src.hardware.mock_hardware import MockStepper, MockGripper, MockColorSensor

# Define robot parameters
UPPER_ARM_LENGTH = 1.0
FOREARM_LENGTH = 1.0
STEPS_PER_ROTATION = 200

def main():
    """
    Main function to initialize and run the robot.
    """
    print("--- Initializing Robot ---")

    # Initialize mock hardware
    base_stepper = MockStepper(STEPS_PER_ROTATION)
    shoulder_stepper = MockStepper(STEPS_PER_ROTATION)
    elbow_stepper = MockStepper(STEPS_PER_ROTATION)
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

    # Run the robot's program
    robot.initialize()
    robot.sow()
    robot.harvest()

    print("--- Robot has finished its tasks ---")

if __name__ == "__main__":
    main()
