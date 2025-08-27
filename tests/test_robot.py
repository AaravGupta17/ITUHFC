import unittest
from unittest.mock import MagicMock, patch
from io import StringIO

from src.logic.robot import Robot, RIPE_COLOR, UNRIPE_COLOR, ROTTEN_COLOR, ALL_FRUIT_LOCATIONS
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
        self.base_stepper.move_to_angle = MagicMock()
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
            active_plots=['orange', 'green']  # Test with two active plots
        )

    def test_initialization(self):
        """Test if the robot initializes correctly."""
        self.robot.initialize()
        self.base_stepper.home.assert_called_once()
        self.shoulder_stepper.home.assert_called_once()
        self.elbow_stepper.home.assert_called_once()
        self.gripper.open.assert_called_once()
        # Check that it moves to the neutral position
        self.base_stepper.move_to_angle.assert_called()

    def test_move_to_xyz(self):
        """Test the move_to_xyz method."""
        self.robot.move_to_xyz(0.5, 0.5, 0.5)
        self.base_stepper.move_to_angle.assert_called_once()
        self.shoulder_stepper.move_to_angle.assert_called_once()
        self.elbow_stepper.move_to_angle.assert_called_once()

    @patch('sys.stdout', new_callable=StringIO)
    def test_sow_logic(self, mock_stdout):
        """Test the sequence of operations in the sow method for two plots."""
        self.robot.sow()

        # For each of the 2 active plots, we grab (close) and release (open)
        self.assertEqual(self.gripper.close.call_count, 2)
        self.assertEqual(self.gripper.open.call_count, 2)

        # Check that the output contains the correct plot colors
        output = mock_stdout.getvalue()
        self.assertIn("Sowing plot: ORANGE", output)
        self.assertIn("Sowing plot: GREEN", output)
        self.assertNotIn("Sowing plot: GRAY", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_harvest_logic(self, mock_stdout):
        """Test the harvest logic for all fruits."""
        # There are 6 fruits in total in ALL_FRUIT_LOCATIONS
        # Let's say 2 are ripe, 2 are unripe, 2 are rotten
        self.color_sensor.read_color.side_effect = [
            RIPE_COLOR, ROTTEN_COLOR,
            UNRIPE_COLOR, RIPE_COLOR,
            UNRIPE_COLOR, ROTTEN_COLOR
        ]

        self.robot.harvest()

        # Gripper should be closed for ripe and rotten fruits (4 total)
        self.assertEqual(self.gripper.close.call_count, 4)
        self.assertEqual(self.gripper.open.call_count, 4)

        output = mock_stdout.getvalue()
        self.assertIn("Fruit is ripe (red), moving to fruit pit.", output)
        self.assertIn("Fruit is unripe (green), skipping.", output)
        self.assertIn("Fruit is diseased (black), moving to waste pit.", output)

if __name__ == '__main__':
    unittest.main()
