from dataclasses import dataclass, field


@dataclass
class PayslipHoursCategory:
    category: str
    hours: str
    amount_nis: str


@dataclass
class MonthlyPayslip:
    employee_id: str
    employee_name: str
    month: str
    hourly_wage: str
    hours_breakdown: list[PayslipHoursCategory] = field(default_factory=list)
    gross_salary: str = ""
    net_salary: str = ""
