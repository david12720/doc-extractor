from pathlib import Path

from pdf_pipeline.abstractions.excel_mapper import ExcelMapper


class PayslipMapper(ExcelMapper):

    def __init__(self, base_mapper: ExcelMapper):
        self._base = base_mapper

    def write(self, records: list[dict], output_path: Path) -> Path:
        flat_rows = self._flatten(records)
        return self._base.write(flat_rows, output_path)

    def _flatten(self, records: list[dict]) -> list[dict]:
        rows: list[dict] = []
        for record in records:
            employee_id = record.get("employee_id", "")
            employee_name = record.get("employee_name", "")
            month = record.get("month", "")
            hourly_wage = record.get("hourly_wage", "")
            gross_salary = record.get("gross_salary", "")
            net_salary = record.get("net_salary", "")
            source_file = record.get("source_file", "")
            page_in_document = record.get("page_in_document", "")

            for cat in record.get("hours_breakdown", []):
                rows.append({
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "month": month,
                    "source_file": source_file,
                    "page_in_document": page_in_document,
                    "category": cat.get("category", ""),
                    "hours": cat.get("hours", ""),
                    "amount_nis": cat.get("amount_nis", ""),
                    "hourly_wage": hourly_wage,
                    "gross_salary": gross_salary,
                    "net_salary": net_salary,
                })
        return rows
