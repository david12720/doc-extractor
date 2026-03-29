from abc import ABC, abstractmethod
from pathlib import Path


class OcrEngine(ABC):
    @abstractmethod
    def ocr_pages(self, pdf_path: Path) -> list[str]:
        """Run OCR on each page of a PDF. Returns a list of text strings, one per page.
        Implementations should log costs internally if a CostLogger is provided."""
