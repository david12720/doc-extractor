from datetime import datetime, time

from pdf_pipeline.abstractions.schema_detector import ColumnMapping
from payroll_control.features.excel_attendance.record_builder import build_records


MAPPING = ColumnMapping(
    person_id_column="A",
    date_column="B",
    from_time_column="C",
    to_time_column="D",
    header_row=1,
    data_start_row=2,
)


class TestBuildRecords:
    def test_basic_string_values(self):
        rows = [
            ["12345", "01/02/2025", "06:00", "18:00"],
            ["12345", "02/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "02.25")
        assert len(result) == 2
        assert result[0] == {
            "person_id": "12345",
            "date": "01/02/2025",
            "from_time": "06:00",
            "to_time": "18:00",
            "sheet": "02.25",
        }
        assert result[1]["date"] == "02/02/2025"

    def test_datetime_objects_formatted(self):
        rows = [
            ["12345", datetime(2025, 2, 1), time(6, 0), time(18, 0)],
        ]
        result = build_records(rows, MAPPING, "sheet1")
        assert result[0]["date"] == "01/02/2025"
        assert result[0]["from_time"] == "06:00"
        assert result[0]["to_time"] == "18:00"

    def test_skips_rows_with_missing_date(self):
        rows = [
            ["12345", None, "06:00", "18:00"],
            ["12345", "01/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1
        assert result[0]["date"] == "01/02/2025"

    def test_skips_rows_with_missing_times(self):
        rows = [
            ["12345", "01/02/2025", None, "18:00"],
            ["12345", "02/02/2025", "07:00", None],
            ["12345", "03/02/2025", "08:00", "16:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1
        assert result[0]["date"] == "03/02/2025"

    def test_skips_rows_with_empty_strings(self):
        rows = [
            ["12345", "01/02/2025", "", "18:00"],
            ["12345", "02/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1

    def test_skips_short_rows(self):
        rows = [
            ["12345", "01/02/2025", "06:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 0

    def test_non_a_columns(self):
        mapping = ColumnMapping(
            person_id_column="A",
            date_column="D",
            from_time_column="E",
            to_time_column="F",
            header_row=2,
            data_start_row=3,
        )
        rows = [
            ["12345", None, None, "01/02/2025", "06:00", "18:00"],
        ]
        result = build_records(rows, mapping, "sheet1")
        assert len(result) == 1
        assert result[0]["date"] == "01/02/2025"

    def test_empty_rows_returns_empty(self):
        result = build_records([], MAPPING, "s1")
        assert result == []

    def test_skips_rows_with_missing_person_id(self):
        rows = [
            [None, "01/02/2025", "06:00", "18:00"],
            ["12345", "02/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1
        assert result[0]["person_id"] == "12345"
