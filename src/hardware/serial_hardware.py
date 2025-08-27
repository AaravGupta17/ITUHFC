import serial
import time
from typing import Tuple

from src.hardware.stepper import Stepper
from src.hardware.gripper import Gripper

class SerialStepper(Stepper):
    """
    A stepper motor controlled over a serial connection.
    Conforms to the Stepper abstract base class.
    """
    def __init__(self, ser: serial.Serial, identifier: str):
        """
        Initializes the stepper with a serial connection and an identifier.

        Args:
            ser: An initialized pySerial object.
            identifier: The character used to identify this motor in commands (e.g., 'B', 'S', 'E').
        """
        self.ser = ser
        self.identifier = identifier

    def move_to_angle(self, angle: float):
        """Formats and sends the move command over serial."""
        command = f"{self.identifier},{angle:.2f}\n"
        self.ser.write(command.encode('utf-8'))
        # print(f"Sent: {command.strip()}") // For debugging

    def home(self):
        """Sends a homing command (moves to 0 degrees)."""
        # Homing logic would be handled by the Arduino sketch upon receiving a move to 0.
        self.move_to_angle(0)

class SerialGripper(Gripper):
    """
    A gripper controlled over a serial connection.
    Conforms to the Gripper abstract base class.
    """
    def __init__(self, ser: serial.Serial, identifier: str = 'G'):
        self.ser = ser
        self.identifier = identifier

    def _send_command(self, state: int):
        """Sends the gripper state command (1 for close, 0 for open)."""
        command = f"{self.identifier},{state}\n"
        self.ser.write(command.encode('utf-8'))
        # print(f"Sent: {command.strip()}") // For debugging

    def open(self):
        """Sends the command to open the gripper."""
        self._send_command(0)

    def close(self):
        """Sends the command to close the gripper."""
        self._send_command(1)
