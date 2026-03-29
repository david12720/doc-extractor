from pathlib import Path

from pdf_pipeline.abstractions.excel_mapper import ExcelMapper


class PlaceholderMapper(ExcelMapper):
    """Placeholder feature mapper — delegates to an injected base mapper."""

    def __init__(self, base_mapper: ExcelMapper):
        self._base = base_mapper

    def write(self, records: list[dict], output_path: Path) -> Path:
        return self._base.write(records, output_path)
