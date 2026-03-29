from dataclasses import dataclass


@dataclass
class ExcelAttendanceRecord:
    person_id: str
    date: str
    from_time: str
    to_time: str
    sheet: str
