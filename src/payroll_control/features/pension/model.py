from dataclasses import dataclass
from typing import List

@dataclass
class PensionDeposit:
    account_number: str
    value_date: str
    salary_month: str
    employer_contribution: float
    employee_contribution: float
    severance_contribution: float
    total_contribution: float

@dataclass
class PensionReport:
    company_name: str
    insured_person_name: str
    insured_person_id: str
    report_date: str
    deposits: List[PensionDeposit]
