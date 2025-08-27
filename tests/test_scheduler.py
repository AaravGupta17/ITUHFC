import unittest
from unittest.mock import MagicMock, patch
from io import StringIO

# We need to import the functions and variables from the controller script
from python_controller import select_best_task, main as run_competition

class TestScheduler(unittest.TestCase):

    def test_select_best_task(self):
        """Tests the task selection strategy."""
        tasks = [
            {"name": "low_score", "score": 5, "estimated_time": 10},
            {"name": "high_score", "score": 30, "estimated_time": 20},
            {"name": "too_long", "score": 50, "estimated_time": 100},
        ]

        # Test 1: With enough time, should pick the highest score
        best_task = select_best_task(tasks, time_remaining=50)
        self.assertEqual(best_task["name"], "high_score")

        # Test 2: With limited time, should pick the one that fits
        best_task = select_best_task(tasks, time_remaining=15)
        self.assertEqual(best_task["name"], "low_score")

        # Test 3: With not enough time for any task
        best_task = select_best_task(tasks, time_remaining=5)
        self.assertIsNone(best_task)

    @patch('python_controller.Robot') # Mock the Robot class
    @patch('python_controller.time')   # Mock the time module
    def test_main_competition_loop(self, mock_time, MockRobot):
        """Tests the main competition loop logic, including retries."""
        # --- Setup Mocks ---
        # Mock the robot instance and its methods
        mock_robot_instance = MockRobot.return_value
        # Simulate a single failure on the very first task attempt, then success.
        mock_robot_instance.execute_task.side_effect = [False, True, True, True, True]

        # Mock the time to simulate the timer running out
        # Start at 0, then advance time for each loop iteration
        mock_time.time.side_effect = [0, 30, 60, 90, 110, 121]

        # --- Run the main function ---
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            run_competition()

        # --- Assertions ---
        # Check that execute_task was called 5 times:
        # Task 1 (Irrigate): Fail, Retry -> Success (2 calls)
        # Task 2 (Harvest): Success (1 call)
        # Task 3 (Harvest): Success (1 call)
        # Task 4 (Sow): Success (1 call)
        self.assertEqual(mock_robot_instance.execute_task.call_count, 5)

        # Check the output for signs of the retry logic
        output = mock_stdout.getvalue()
        self.assertIn("Retrying task...", output)
        # Check final score: 30 (irrigate) + 10 (harvest) + 10 (harvest) + 5 (sow) = 55
        self.assertIn("Final Score: 55", output)

if __name__ == '__main__':
    unittest.main()
