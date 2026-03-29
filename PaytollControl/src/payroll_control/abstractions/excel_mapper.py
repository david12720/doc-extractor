from abc import ABC, abstractmethod
from pathlib import Path


class ExcelMapper(ABC):
    @abstractmethod
    def write(self, records: list[dict], output_path: Path) -> Path:
        """Write extracted records to an Excel file. Returns the output path."""
