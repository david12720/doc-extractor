from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PreparedFile:
    """A single prepared file ready for LLM extraction."""
    source_path: Path
    data: bytes
    mime_type: str
    page_index: int | None = None
    metadata: dict = field(default_factory=dict)


class FileConverter(ABC):
    @abstractmethod
    def convert(self, input_files: list[Path]) -> list[PreparedFile]:
        """Convert input files (PDF/PNG) into a list of PreparedFiles."""


class PreparationStep(ABC):
    @abstractmethod
    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        """Apply a post-conversion processing step to prepared files."""


class PreparationPipeline:
    """Runs a FileConverter followed by zero or more PreparationSteps."""

    def __init__(self, converter: FileConverter, steps: list[PreparationStep] | None = None):
        self._converter = converter
        self._steps = steps or []

    def prepare(self, input_files: list[Path]) -> list[PreparedFile]:
        files = self._converter.convert(input_files)
        for step in self._steps:
            files = step.process(files)
        return files
