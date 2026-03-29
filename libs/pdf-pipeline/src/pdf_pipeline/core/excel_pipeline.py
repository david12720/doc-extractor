import json
from collections import defaultdict
from pathlib import Path

from ..abstractions.cache_manager import CacheManager
from ..abstractions.schema_detector import SchemaDetector
from ..abstractions.spreadsheet_reader import SpreadsheetReader
from ..abstractions.status_tracker import StatusTracker
from .feature_registry import ExcelFeatureConfig
from .file_key import build_file_key

HEADER_ROWS_TO_READ = 5


class ExcelPipeline:
    def __init__(
        self,
        feature: ExcelFeatureConfig,
        reader: SpreadsheetReader,
        schema_detector: SchemaDetector,
        cache: CacheManager,
        status: StatusTracker,
    ):
        self._feature = feature
        self._reader = reader
        self._schema_detector = schema_detector
        self._cache = cache
        self._status = status

    def run(self, input_files: list[Path], output_path: Path) -> Path:
        file_key = build_file_key(self._feature.name, input_files)

        if self._status.is_complete(file_key):
            print(f"[{file_key}] All stages complete -- skipping.")
            return output_path

        cached = self._cache.load_json(file_key)
        if cached is not None:
            print(f"[{file_key}] Loaded results from JSON cache.")
            self._status.set_status(file_key, "extract", "success")
            self._status.set_status(file_key, "cache", "success")
            return self._write_json(cached, output_path, file_key)

        all_records: dict[str, dict] = {}
        for file_path in input_files:
            first_sheet = self._reader.get_sheet_names(file_path)[0]
            headers_text = self._format_headers(file_path, first_sheet)
            mapping = self._schema_detector.detect(headers_text, cache_key=file_path.stem)

            flat_records: list[dict] = []
            for sheet in self._reader.get_sheet_names(file_path):
                rows = self._reader.read_data_rows(file_path, sheet, mapping.data_start_row)
                records = self._feature.record_builder(rows, mapping, sheet)
                flat_records.extend(records)
            all_records[file_path.name] = self._group_by_person_and_month(flat_records)
        self._status.set_status(file_key, "prepare", "success")

        self._cache.save_json(file_key, all_records)
        self._status.set_status(file_key, "extract", "success")
        self._status.set_status(file_key, "cache", "success")
        total = self._count_records(all_records)
        print(f"[{file_key}] Extracted {total} record(s) from {len(input_files)} file(s).")
        return self._write_json(all_records, output_path, file_key)

    def _format_headers(self, path: Path, sheet: str) -> str:
        rows = self._reader.read_header_rows(path, sheet, max_rows=HEADER_ROWS_TO_READ)
        lines: list[str] = []
        for row_idx, row in enumerate(rows, start=1):
            cells = [str(cell) if cell is not None else "" for cell in row]
            lines.append(f"Row {row_idx}: {' | '.join(cells)}")
        return "\n".join(lines)

    @staticmethod
    def _group_by_person_and_month(records: list[dict]) -> dict[str, dict[str, list[dict]]]:
        grouped: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for rec in records:
            person_id = rec.pop("person_id")
            month = rec.pop("sheet")
            grouped[person_id][month].append(rec)
        return {pid: dict(months) for pid, months in grouped.items()}

    @staticmethod
    def _count_records(all_records: dict) -> int:
        total = 0
        for file_data in all_records.values():
            for person_data in file_data.values():
                for month_records in person_data.values():
                    total += len(month_records)
        return total

    def _write_json(self, data: dict | list, output_path: Path, file_key: str) -> Path:
        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[{file_key}] Saved output -> {json_path}")
        self._status.set_status(file_key, "json_output", "success")
        return json_path
