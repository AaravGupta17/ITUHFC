import unittest
from unittest.mock import MagicMock, patch
from io import StringIO

from src.logic.robot import Robot, RIPE_COLOR, UNRIPE_COLOR
from src.hardware.mock_hardware import MockStepper, MockGripper, MockColorSensor

class TestRobotExecution(unittest.TestCase):

    def setUp(self):
        """Set up a robot with mock hardware components for each test."""
        self.mock_base_stepper = MockStepper(200)
        self.mock_shoulder_stepper = MockStepper(200)
        self.mock_elbow_stepper = MockStepper(200)
        self.mock_gripper = MockGripper()
        self.mock_color_sensor = MockColorSensor()

        # Spy on the hardware methods to track calls
        self.mock_base_stepper.move_to_angle = MagicMock(return_value=True)
        self.mock_gripper.open = MagicMock(return_value=True)
        self.mock_gripper.close = MagicMock(return_value=True)
        self.mock_color_sensor.read_color = MagicMock()

        self.robot = Robot(
            base_stepper=self.mock_base_stepper,
            shoulder_stepper=self.mock_shoulder_stepper,
            elbow_stepper=self.mock_elbow_stepper,
            gripper=self.mock_gripper,
            color_sensor=self.mock_color_sensor,
            upper_arm_length=0.5,
            forearm_length=0.5,
        )

    def test_execute_sow_task_success(self):
        """Tests that a 'sow' task calls the correct hardware methods."""
        sow_task = {"type": "sow", "location": (0.5, -0.5, 0.0)}

        result = self.robot.execute_task(sow_task)

        self.assertTrue(result)
        # Check that the gripper was used
        self.mock_gripper.close.assert_called_once()
        self.mock_gripper.open.assert_called_once()
        # Check that the arm moved multiple times
        self.assertTrue(self.mock_base_stepper.move_to_angle.call_count >= 3)

    def test_execute_harvest_task_ripe_fruit(self):
        """Tests that a 'harvest' task correctly handles a ripe fruit."""
        self.mock_color_sensor.read_color.return_value = RIPE_COLOR
        harvest_task = {"type": "harvest", "location": (0.6, 0.2, 0.2)}

        result = self.robot.execute_task(harvest_task)

        self.assertTrue(result)
        # Check that the gripper was used
        self.mock_gripper.close.assert_called_once()
        self.mock_gripper.open.assert_called_once()
        # Check that the color sensor was read
        self.mock_color_sensor.read_color.assert_called_once()

    def test_execute_harvest_task_unripe_fruit(self):
        """Tests that a 'harvest' task does nothing for an unripe fruit."""
        self.mock_color_sensor.read_color.return_value = UNRIPE_COLOR
        harvest_task = {"type": "harvest", "location": (0.6, 0.2, 0.2)}

        result = self.robot.execute_task(harvest_task)

        self.assertTrue(result)
        # Gripper should not be used for unripe fruit
        self.mock_gripper.close.assert_not_called()
        self.mock_gripper.open.assert_not_called()

    def test_execute_irrigate_task_success(self):
        """Tests that an 'irrigate' task calls the correct hardware methods."""
        irrigate_task = {"type": "irrigate"}

        result = self.robot.execute_task(irrigate_task)

        self.assertTrue(result)
        self.mock_gripper.close.assert_called_once()
        self.mock_gripper.open.assert_called_once()
        self.assertTrue(self.mock_base_stepper.move_to_angle.call_count >= 2)

    def test_task_failure_propagates(self):
        """Tests that a hardware failure causes the task to fail."""
        # Simulate a gripper failure
        self.mock_gripper.close.return_value = False
        sow_task = {"type": "sow", "location": (0.5, -0.5, 0.0)}

        result = self.robot.execute_task(sow_task)

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
