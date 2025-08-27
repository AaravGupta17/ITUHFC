from abc import ABC, abstractmethod

class Gripper(ABC):
    @abstractmethod
    def open(self):
        """Opens the gripper."""
        pass

    @abstractmethod
    def close(self):
        """Closes the gripper."""
        pass
