import unittest
from unittest.mock import MagicMock, patch
from io import StringIO

from src.logic.robot import Robot, RIPE_COLOR, UNRIPE_COLOR, PLOT_LOCATIONS, HARVEST_LOCATIONS
from src.hardware.mock_hardware import MockStepper, MockGripper, MockColorSensor

class TestIntegratedRobot(unittest.TestCase):

    def setUp(self):
        """Set up a robot with mock hardware components for each test."""
        # Mock all hardware components
        self.mock_base_stepper = MockStepper(200)
        self.mock_shoulder_stepper = MockStepper(200)
        self.mock_elbow_stepper = MockStepper(200)
        self.mock_gripper = MockGripper()
        self.mock_color_sensor = MockColorSensor()

        # Add MagicMock spies to the methods we want to track
        self.mock_base_stepper.move_to_angle = MagicMock()
        self.mock_shoulder_stepper.move_to_angle = MagicMock()
        self.mock_elbow_stepper.move_to_angle = MagicMock()
        self.mock_gripper.open = MagicMock()
        self.mock_gripper.close = MagicMock()
        self.mock_color_sensor.read_color = MagicMock()

        # Instantiate the main Robot class with all mock components
        self.robot = Robot(
            base_stepper=self.mock_base_stepper,
            shoulder_stepper=self.mock_shoulder_stepper,
            elbow_stepper=self.mock_elbow_stepper,
            gripper=self.mock_gripper,
            color_sensor=self.mock_color_sensor,
            upper_arm_length=0.5,
            forearm_length=0.5,
            active_plots=['orange', 'green'] # Test with two plots
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_sow_mission_sequence(self, mock_stdout):
        """Tests that sow mission iterates through all active plots."""
        self.robot.sow()

        # Check that the gripper was used for each plot
        num_plots = len(self.robot.active_plots)
        self.assertEqual(self.mock_gripper.close.call_count, num_plots)
        self.assertEqual(self.mock_gripper.open.call_count, num_plots)

        # Check that the arm moved for each action per plot
        # (pickup, neutral, plot, neutral) = 4 moves per plot
        self.assertEqual(self.mock_base_stepper.move_to_angle.call_count, 4 * num_plots)

        # Check for expected output
        output = mock_stdout.getvalue()
        self.assertIn("Sowing plot: ORANGE", output)
        self.assertIn("Sowing plot: GREEN", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_harvest_mission_sequence(self, mock_stdout):
        """Tests that harvest mission iterates through all locations and sorts correctly."""
        # Configure mock sensor to return a ripe fruit, then an unripe one
        self.mock_color_sensor.read_color.side_effect = [RIPE_COLOR, UNRIPE_COLOR]

        self.robot.harvest()

        # Check that the arm moved to check each location
        num_harvest_locs = len(HARVEST_LOCATIONS)
        self.assertTrue(self.mock_base_stepper.move_to_angle.call_count > num_harvest_locs)

        # Check that gripper was only used for the ripe fruit
        self.mock_gripper.close.assert_called_once()
        self.mock_gripper.open.assert_called_once()

        # Check for expected output
        output = mock_stdout.getvalue()
        self.assertIn("Moving arm to fruit pit", output)
        self.assertIn("Fruit is unripe. Leaving it.", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_irrigate_mission_sequence(self, mock_stdout):
        """Tests the sequence of the irrigate mission."""
        self.robot.irrigate()

        # Check that the arm moves and gripper operates
        self.assertTrue(self.mock_base_stepper.move_to_angle.call_count >= 2)
        self.mock_gripper.close.assert_called_once()
        self.mock_gripper.open.assert_called_once()

        # Check for expected output
        output = mock_stdout.getvalue()
        self.assertIn("--- Starting Irrigation Mission ---", output)
        self.assertIn("Pulling water lever...", output)

    @patch('src.logic.robot.Robot.harvest')
    @patch('src.logic.robot.Robot.irrigate')
    @patch('src.logic.robot.Robot.sow')
    @patch('src.logic.robot.Robot.initialize')
    def test_full_mission_order(self, mock_init, mock_sow, mock_irrigate, mock_harvest):
        """Tests that the full mission calls sub-missions in the correct order."""
        self.robot.full_mission()

        mock_init.assert_called_once()
        mock_sow.assert_called_once()
        mock_irrigate.assert_called_once()
        mock_harvest.assert_called_once()

if __name__ == '__main__':
    unittest.main()
