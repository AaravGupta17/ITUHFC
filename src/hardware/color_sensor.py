from abc import ABC, abstractmethod
from typing import Tuple

class ColorSensor(ABC):
    @abstractmethod
    def read_color(self) -> Tuple[int, int, int]:
        """Reads the color and returns an (R, G, B) tuple."""
        pass
