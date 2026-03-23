from payroll_control.features.payslip.mapper import PayslipMapper


class FakeBaseMapper:
    def __init__(self):
        self.written_rows = None

    def write(self, records, output_path):
        self.written_rows = records
        return output_path


class TestPayslipMapper:
    def test_flatten_single_record(self):
        base = FakeBaseMapper()
        mapper = PayslipMapper(base_mapper=base)

        records = [{
            "employee_id": "123",
            "employee_name": "Test",
            "month": "02/2025",
            "hourly_wage": "35.00",
            "gross_salary": "7500.00",
            "net_salary": "6200.00",
            "source_file": "payslip.pdf",
            "page_in_document": 1,
            "hours_breakdown": [
                {"category": "רגילות", "hours": "176.00", "amount_nis": "6160.00"},
                {"category": "נוספות 125%", "hours": "10.00", "amount_nis": "437.50"},
            ],
        }]

        mapper.write(records, "output.xlsx")

        rows = base.written_rows
        assert len(rows) == 2
        assert rows[0]["category"] == "רגילות"
        assert rows[0]["hours"] == "176.00"
        assert rows[0]["employee_id"] == "123"
        assert rows[0]["hourly_wage"] == "35.00"
        assert rows[1]["category"] == "נוספות 125%"
        assert rows[1]["amount_nis"] == "437.50"

    def test_flatten_multiple_records(self):
        base = FakeBaseMapper()
        mapper = PayslipMapper(base_mapper=base)

        records = [
            {
                "employee_id": "123", "employee_name": "A", "month": "02/2025",
                "hourly_wage": "35.00", "gross_salary": "7500.00", "net_salary": "6200.00",
                "source_file": "p.pdf", "page_in_document": 1,
                "hours_breakdown": [{"category": "רגילות", "hours": "176.00", "amount_nis": "6160.00"}],
            },
            {
                "employee_id": "123", "employee_name": "A", "month": "03/2025",
                "hourly_wage": "35.00", "gross_salary": "7200.00", "net_salary": "5900.00",
                "source_file": "p.pdf", "page_in_document": 2,
                "hours_breakdown": [{"category": "רגילות", "hours": "170.00", "amount_nis": "5950.00"}],
            },
        ]

        mapper.write(records, "output.xlsx")

        rows = base.written_rows
        assert len(rows) == 2
        assert rows[0]["month"] == "02/2025"
        assert rows[1]["month"] == "03/2025"

    def test_flatten_empty_breakdown(self):
        base = FakeBaseMapper()
        mapper = PayslipMapper(base_mapper=base)

        records = [{
            "employee_id": "123", "employee_name": "A", "month": "02/2025",
            "hourly_wage": "35.00", "gross_salary": "7500.00", "net_salary": "6200.00",
            "source_file": "p.pdf", "page_in_document": 1,
            "hours_breakdown": [],
        }]

        mapper.write(records, "output.xlsx")
        assert base.written_rows == []
