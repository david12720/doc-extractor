from pathlib import Path

from pdf_pipeline.abstractions.excel_mapper import ExcelMapper


class AttendanceMapper(ExcelMapper):
    """Maps attendance records to an Excel file with one row per attendance day."""

    def __init__(self, base_mapper: ExcelMapper):
        self._base = base_mapper

    def write(self, records: list[dict], output_path: Path) -> Path:
        flat_rows = self._flatten(records)
        return self._base.write(flat_rows, output_path)

    def _flatten(self, records: list[dict]) -> list[dict]:
        rows: list[dict] = []
        for record in records:
            employee_id = record.get("employee_id", "")
            month = record.get("month", "")
            source_file = record.get("source_file", "")
            page_in_document = record.get("page_in_document", "")

            for day in record.get("attendance", []):
                rows.append({
                    "employee_id": employee_id,
                    "month": month,
                    "source_file": source_file,
                    "page_in_document": page_in_document,
                    "date": day.get("date", ""),
                    "from_time": day.get("from_time", ""),
                    "to_time": day.get("to_time", ""),
                })
        return rows
