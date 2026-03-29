from abc import ABC, abstractmethod


class StatusTracker(ABC):
    @abstractmethod
    def get_status(self, file_key: str, stage: str) -> str | None:
        """Get the status of a specific stage for a file. Returns None if not tracked."""

    @abstractmethod
    def set_status(self, file_key: str, stage: str, status: str) -> None:
        """Set the status of a specific stage for a file."""

    @abstractmethod
    def is_complete(self, file_key: str) -> bool:
        """Check if all stages for a file are complete."""
