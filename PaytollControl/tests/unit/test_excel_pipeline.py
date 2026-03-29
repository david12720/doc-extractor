from pathlib import Path

from payroll_control.abstractions.schema_detector import ColumnMapping
from payroll_control.core.excel_pipeline import ExcelPipeline
from payroll_control.core.feature_registry import ExcelFeatureConfig


class FakeReader:
    def __init__(self, sheet_names: list[str], header_rows: list[list], data_rows: list[list]):
        self._sheet_names = sheet_names
        self._header_rows = header_rows
        self._data_rows = data_rows

    def get_sheet_names(self, path: Path) -> list[str]:
        return self._sheet_names

    def read_header_rows(self, path: Path, sheet: str, max_rows: int = 5) -> list[list]:
        return self._header_rows[:max_rows]

    def read_data_rows(self, path: Path, sheet: str, start_row: int) -> list[list]:
        return self._data_rows


class FakeDetector:
    def __init__(self, mapping: ColumnMapping):
        self._mapping = mapping
        self.detect_calls: list[str] = []

    def detect(self, headers_text: str, cache_key: str = "schema") -> ColumnMapping:
        self.detect_calls.append(headers_text)
        return self._mapping


class FakeCache:
    def __init__(self):
        self._json: dict[str, object] = {}

    def has_cache(self, key: str) -> bool:
        return key in self._json

    def load_json(self, key: str):
        return self._json.get(key)

    def save_json(self, key: str, data) -> None:
        self._json[key] = data

    def load_raw(self, key: str):
        return None

    def save_raw(self, key: str, raw_text: str) -> None:
        pass


class FakeStatus:
    def __init__(self):
        self._data: dict[str, dict[str, str]] = {}

    def is_complete(self, file_key: str) -> bool:
        return False

    def get_status(self, file_key: str, stage: str) -> str | None:
        return self._data.get(file_key, {}).get(stage)

    def set_status(self, file_key: str, stage: str, status: str) -> None:
        if file_key not in self._data:
            self._data[file_key] = {}
        self._data[file_key][stage] = status


MAPPING = ColumnMapping(
    person_id_column="A",
    date_column="B",
    from_time_column="C",
    to_time_column="D",
    header_row=1,
    data_start_row=2,
)


def _simple_builder(rows, mapping, sheet):
    return [{"person_id": r[0], "date": r[1], "from_time": r[2], "to_time": r[3], "sheet": sheet} for r in rows]


class TestExcelPipeline:
    def test_run_extracts_and_writes_json(self, tmp_path):
        reader = FakeReader(
            sheet_names=["Sheet1"],
            header_rows=[["ת.ז", "תאריך", "כניסה", "יציאה"]],
            data_rows=[["12345", "01/02/2025", "06:00", "18:00"]],
        )
        detector = FakeDetector(MAPPING)
        cache = FakeCache()
        status = FakeStatus()

        feature = ExcelFeatureConfig(
            name="test_excel",
            schema_prompt="detect",
            record_builder=_simple_builder,
        )

        input_file = tmp_path / "test.xlsx"
        input_file.touch()
        output_path = tmp_path / "output" / "result.json"

        pipeline = ExcelPipeline(
            feature=feature,
            reader=reader,
            schema_detector=detector,
            cache=cache,
            status=status,
        )

        result = pipeline.run([input_file], output_path)

        assert result.suffix == ".json"
        assert result.exists()

        import json
        data = json.loads(result.read_text(encoding="utf-8"))
        assert "test.xlsx" in data
        assert "12345" in data["test.xlsx"]
        assert "Sheet1" in data["test.xlsx"]["12345"]
        assert data["test.xlsx"]["12345"]["Sheet1"][0]["date"] == "01/02/2025"

    def test_run_uses_cache_on_second_call(self, tmp_path):
        reader = FakeReader(["Sheet1"], [["h"]], [["12345", "01/02/2025", "06:00", "18:00"]])
        detector = FakeDetector(MAPPING)
        cache = FakeCache()
        status = FakeStatus()

        feature = ExcelFeatureConfig(
            name="test_excel",
            schema_prompt="detect",
            record_builder=_simple_builder,
        )

        input_file = tmp_path / "test.xlsx"
        input_file.touch()
        output_path = tmp_path / "output" / "result.json"

        pipeline = ExcelPipeline(
            feature=feature, reader=reader, schema_detector=detector,
            cache=cache, status=status,
        )

        pipeline.run([input_file], output_path)
        detector.detect_calls.clear()
        pipeline.run([input_file], output_path)

        assert len(detector.detect_calls) == 0

    def test_run_multiple_files(self, tmp_path):
        reader = FakeReader(
            sheet_names=["S1"],
            header_rows=[["h"]],
            data_rows=[["12345", "01/02/2025", "06:00", "18:00"], ["12345", "02/02/2025", "07:00", "17:00"]],
        )
        detector = FakeDetector(MAPPING)
        cache = FakeCache()
        status = FakeStatus()

        feature = ExcelFeatureConfig(
            name="test_excel",
            schema_prompt="detect",
            record_builder=_simple_builder,
        )

        file1 = tmp_path / "file1.xlsx"
        file2 = tmp_path / "file2.xlsx"
        file1.touch()
        file2.touch()
        output_path = tmp_path / "output" / "result.json"

        pipeline = ExcelPipeline(
            feature=feature, reader=reader, schema_detector=detector,
            cache=cache, status=status,
        )

        result = pipeline.run([file1, file2], output_path)

        import json
        data = json.loads(result.read_text(encoding="utf-8"))
        assert "file1.xlsx" in data
        assert "file2.xlsx" in data
        assert "12345" in data["file1.xlsx"]
        assert len(data["file1.xlsx"]["12345"]["S1"]) == 2

    def test_status_set_on_completion(self, tmp_path):
        reader = FakeReader(["S1"], [["h"]], [["12345", "01/02/2025", "06:00", "18:00"]])
        detector = FakeDetector(MAPPING)
        cache = FakeCache()
        status = FakeStatus()

        feature = ExcelFeatureConfig(
            name="test_excel",
            schema_prompt="detect",
            record_builder=_simple_builder,
        )

        input_file = tmp_path / "test.xlsx"
        input_file.touch()
        output_path = tmp_path / "output" / "result.json"

        pipeline = ExcelPipeline(
            feature=feature, reader=reader, schema_detector=detector,
            cache=cache, status=status,
        )
        pipeline.run([input_file], output_path)

        assert status.get_status("test_excel_test", "prepare") == "success"
        assert status.get_status("test_excel_test", "extract") == "success"
        assert status.get_status("test_excel_test", "cache") == "success"
        assert status.get_status("test_excel_test", "json_output") == "success"
