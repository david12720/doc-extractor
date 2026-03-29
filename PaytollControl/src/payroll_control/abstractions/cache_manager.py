from abc import ABC, abstractmethod


class CacheManager(ABC):
    @abstractmethod
    def has_cache(self, key: str) -> bool:
        """Check if cached data exists for the given key."""

    @abstractmethod
    def load_raw(self, key: str) -> str | None:
        """Load cached raw LLM response text."""

    @abstractmethod
    def load_json(self, key: str) -> list[dict] | None:
        """Load cached structured JSON data."""

    @abstractmethod
    def save_raw(self, key: str, raw_text: str) -> None:
        """Save raw LLM response text to cache."""

    @abstractmethod
    def save_json(self, key: str, data: list[dict]) -> None:
        """Save structured JSON data to cache."""
