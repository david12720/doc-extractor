from pathlib import Path

from pdf_pipeline.abstractions.excel_mapper import ExcelMapper

class PensionMapper(ExcelMapper):
    def write(self, records: list[dict], output_path: Path) -> Path:
        # The FeaturePipeline handles JSON writing.
        # This mapper is a placeholder for now.
        return output_path.with_suffix(".json")
