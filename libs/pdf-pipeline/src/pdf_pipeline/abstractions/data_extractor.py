from abc import ABC, abstractmethod

from .file_preparator import PreparedFile


class DataExtractor(ABC):
    @abstractmethod
    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        """Extract structured data from prepared files using LLM."""

    @abstractmethod
    def parse_cached_response(self, raw_text: str) -> list[dict]:
        """Parse a cached raw LLM response into structured records."""
