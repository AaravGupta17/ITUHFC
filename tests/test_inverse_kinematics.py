import unittest
import math

from src.kinematics.inverse_kinematics import calculate_angles

class TestInverseKinematics(unittest.TestCase):

    def test_calculate_angles_forward_kinematics(self):
        """
        Tests if the calculated angles can be used to reconstruct the original coordinates.
        """
        l1 = 1.0
        l2 = 1.0
        x, y = 0.5, 0.5

        theta1, theta2 = calculate_angles(x, y, l1, l2)

        # Forward kinematics
        x_out = l1 * math.cos(theta1) + l2 * math.cos(theta1 + theta2)
        y_out = l1 * math.sin(theta1) + l2 * math.sin(theta1 + theta2)

        self.assertAlmostEqual(x, x_out, places=5)
        self.assertAlmostEqual(y, y_out, places=5)

    def test_out_of_reach(self):
        """
        Tests if a ValueError is raised for a target that is out of reach.
        """
        l1 = 1.0
        l2 = 1.0
        x, y = 3.0, 0.0  # Out of reach

        with self.assertRaises(ValueError):
            calculate_angles(x, y, l1, l2)

    def test_max_reach(self):
        """
        Tests the case where the target is at the maximum reach of the arm.
        """
        l1 = 1.0
        l2 = 1.0
        x, y = 2.0, 0.0 # Max reach

        theta1, theta2 = calculate_angles(x, y, l1, l2)

        self.assertAlmostEqual(theta1, 0.0, places=5)
        self.assertAlmostEqual(theta2, 0.0, places=5)

if __name__ == '__main__':
    unittest.main()
