from dataclasses import dataclass, field


@dataclass
class AttendanceDay:
    date: str
    from_time: str
    to_time: str


@dataclass
class MonthlyAttendance:
    employee_name: str
    month: str
    source_file: str
    page_in_document: int
    attendance: list[AttendanceDay] = field(default_factory=list)
