import unittest
from unittest.mock import MagicMock, patch, call
from io import StringIO

from src.logic.robot import Robot, RIPE_COLOR, UNRIPE_COLOR, ROTTEN_COLOR
from src.hardware.mock_hardware import MockStepper, MockGripper, MockColorSensor

class TestRobot(unittest.TestCase):

    def setUp(self):
        """Set up a robot with mock hardware for each test."""
        self.base_stepper = MockStepper(steps_per_rotation=200)
        self.shoulder_stepper = MockStepper(steps_per_rotation=200)
        self.elbow_stepper = MockStepper(steps_per_rotation=200)
        self.gripper = MockGripper()
        self.color_sensor = MockColorSensor()

        # Mock the hardware methods to check if they are called
        self.base_stepper.home = MagicMock()
        self.shoulder_stepper.home = MagicMock()
        self.elbow_stepper.home = MagicMock()
        self.shoulder_stepper.move_to_angle = MagicMock()
        self.elbow_stepper.move_to_angle = MagicMock()
        self.gripper.open = MagicMock()
        self.gripper.close = MagicMock()
        self.color_sensor.read_color = MagicMock()

        self.robot = Robot(
            base_stepper=self.base_stepper,
            shoulder_stepper=self.shoulder_stepper,
            elbow_stepper=self.elbow_stepper,
            gripper=self.gripper,
            color_sensor=self.color_sensor,
            upper_arm_length=1.0,
            forearm_length=1.0,
        )

    def test_initialization(self):
        """Test if the robot initializes correctly."""
        self.robot.initialize()
        self.base_stepper.home.assert_called_once()
        self.shoulder_stepper.home.assert_called_once()
        self.elbow_stepper.home.assert_called_once()
        self.gripper.open.assert_called_once()

    def test_move_to_xy(self):
        """Test the move_to_xy method."""
        self.robot.move_to_xy(0.5, 0.5)
        self.shoulder_stepper.move_to_angle.assert_called_once()
        self.elbow_stepper.move_to_angle.assert_called_once()

    @patch('sys.stdout', new_callable=StringIO)
    def test_sow_logic(self, mock_stdout):
        """Test the sequence of operations in the sow method."""
        self.robot.sow()

        # Check if gripper methods were called in the correct order
        self.assertEqual(self.gripper.close.call_count, 2)
        # The gripper is opened at the end of the sowing process and during the final recall
        self.assertEqual(self.gripper.open.call_count, 2)

        output = mock_stdout.getvalue()
        self.assertIn("--- Starting Sowing ---", output)
        self.assertIn("--- Sowing Complete ---", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_harvest_logic(self, mock_stdout):
        """Test the harvest logic for a sequence of fruits."""
        # Configure mock color sensor to return a sequence of colors
        self.color_sensor.read_color.side_effect = [RIPE_COLOR, UNRIPE_COLOR, ROTTEN_COLOR]

        self.robot.harvest()

        # Gripper should be closed for ripe and rotten, but not for unripe
        self.assertEqual(self.gripper.close.call_count, 2)
        self.assertEqual(self.gripper.open.call_count, 2)

        output = mock_stdout.getvalue()
        self.assertIn("Fruit is ripe, moving to fruit pit.", output)
        self.assertIn("Fruit is unripe, skipping.", output)
        self.assertIn("Fruit is rotten, moving to waste pit.", output)

if __name__ == '__main__':
    unittest.main()
