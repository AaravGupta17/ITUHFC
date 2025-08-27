import unittest
import math

from src.kinematics.inverse_kinematics import calculate_angles_3d

class TestInverseKinematics3D(unittest.TestCase):

    def test_calculate_angles_3d_forward_kinematics(self):
        """
        Tests if the 3D angles can be used to reconstruct the original coordinates.
        """
        l1 = 1.0
        l2 = 1.0
        x, y, z = 0.5, 0.5, 0.5

        base, shoulder, elbow = calculate_angles_3d(x, y, z, l1, l2)

        # Forward kinematics for 3D
        r = l1 * math.cos(shoulder) + l2 * math.cos(shoulder + elbow)
        x_out = r * math.cos(base)
        y_out = r * math.sin(base)
        z_out = l1 * math.sin(shoulder) + l2 * math.sin(shoulder + elbow)

        self.assertAlmostEqual(x, x_out, places=5)
        self.assertAlmostEqual(y, y_out, places=5)
        self.assertAlmostEqual(z, z_out, places=5)

    def test_out_of_reach_3d(self):
        """
        Tests if a ValueError is raised for a 3D target that is out of reach.
        """
        l1 = 1.0
        l2 = 1.0
        x, y, z = 2.0, 2.0, 2.0  # Clearly out of reach

        with self.assertRaisesRegex(ValueError, "Target is out of reach"):
            calculate_angles_3d(x, y, z, l1, l2)

    def test_on_z_axis(self):
        """
        Tests a target directly on the Z-axis.
        """
        l1 = 1.0
        l2 = 1.0
        x, y, z = 0.0, 0.0, 1.5

        # The base angle can be anything when x and y are 0. atan2(0,0) is 0.
        # So we expect a base angle of 0.
        base, shoulder, elbow = calculate_angles_3d(x, y, z, l1, l2)

        self.assertAlmostEqual(base, 0.0, places=5)

        # Check forward kinematics for z
        z_out = l1 * math.sin(shoulder) + l2 * math.sin(shoulder + elbow)
        self.assertAlmostEqual(z, z_out, places=5)

if __name__ == '__main__':
    unittest.main()
