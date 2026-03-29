from payroll_control.features.attendance.mapper import AttendanceMapper


class FakeBaseMapper:
    def __init__(self):
        self.written_records = []

    def write(self, records, output_path):
        self.written_records = records
        return output_path


def test_flatten_single_record():
    base = FakeBaseMapper()
    mapper = AttendanceMapper(base_mapper=base)

    records = [{
        "employee_id": "Test",
        "month": "01/2025",
        "source_file": "doc.pdf",
        "page_in_document": 0,
        "attendance": [
            {"date": "01/01/2025", "from_time": "07:00", "to_time": "16:00", },
            {"date": "02/01/2025", "from_time": "ריק", "to_time": "ריק", },
        ],
    }]

    from pathlib import Path
    mapper.write(records, Path("out.xlsx"))

    assert len(base.written_records) == 2
    assert base.written_records[0]["employee_id"] == "Test"
    assert base.written_records[0]["date"] == "01/01/2025"
    assert base.written_records[1]["from_time"] == "ריק"


def test_flatten_multiple_records():
    base = FakeBaseMapper()
    mapper = AttendanceMapper(base_mapper=base)

    records = [
        {
            "employee_id": "A",
            "month": "01/2025",
            "source_file": "a.pdf",
            "page_in_document": 0,
            "attendance": [{"date": "01/01/2025", "from_time": "07:00", "to_time": "16:00", }],
        },
        {
            "employee_id": "B",
            "month": "02/2025",
            "source_file": "b.pdf",
            "page_in_document": 1,
            "attendance": [{"date": "01/02/2025", "from_time": "08:00", "to_time": "17:00", }],
        },
    ]

    from pathlib import Path
    mapper.write(records, Path("out.xlsx"))

    assert len(base.written_records) == 2
    assert base.written_records[0]["employee_id"] == "A"
    assert base.written_records[1]["employee_id"] == "B"


def test_flatten_empty_attendance():
    base = FakeBaseMapper()
    mapper = AttendanceMapper(base_mapper=base)

    records = [{"employee_id": "C", "month": "03/2025", "source_file": "c.pdf", "page_in_document": 0, "attendance": []}]

    from pathlib import Path
    mapper.write(records, Path("out.xlsx"))

    assert len(base.written_records) == 0
