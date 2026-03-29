from abc import ABC, abstractmethod
from pathlib import Path


class SpreadsheetReader(ABC):
    @abstractmethod
    def read_header_rows(self, path: Path, sheet: str, max_rows: int = 5) -> list[list]:
        """Read the first max_rows rows from a sheet."""

    @abstractmethod
    def read_data_rows(self, path: Path, sheet: str, start_row: int) -> list[list]:
        """Read all rows starting from start_row."""

    @abstractmethod
    def get_sheet_names(self, path: Path) -> list[str]:
        """Return all sheet names in the workbook."""
