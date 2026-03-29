from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnMapping:
    person_id_column: str
    date_column: str
    from_time_column: str
    to_time_column: str
    header_row: int
    data_start_row: int


class SchemaDetector(ABC):
    @abstractmethod
    def detect(self, headers_text: str, cache_key: str = "schema") -> ColumnMapping:
        """Detect column mapping from header text."""
