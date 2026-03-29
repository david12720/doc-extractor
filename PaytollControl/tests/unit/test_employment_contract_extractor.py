import pytest
from pathlib import Path

from payroll_control.abstractions.file_preparator import PreparedFile
from payroll_control.features.employment_contract.extractor import EmploymentContractExtractor

LLM_RESPONSE_FULL = """
{
  "employee_name": "ישראל ישראלי",
  "employee_id": "012345678",
  "employer_name": "חברת דוגמה בע\\"מ",
  "start_date": "01/03/2024",
  "shortened_workday": "ערב שבת",
  "weekly_rest_day": "שבת",
  "employment_type": "משרה מלאה",
  "overtime_calculation_after": "8 שעות",
  "payment_type": "שעתי",
  "workdays_per_week": 5
}
"""

LLM_RESPONSE_PARTIAL = """
{
  "employee_name": "אבו נגמה זהיר",
  "employee_id": "201007499",
  "employer_name": null,
  "start_date": "15/01/2025",
  "shortened_workday": null,
  "weekly_rest_day": "שבת",
  "employment_type": null,
  "overtime_calculation_after": null,
  "payment_type": "גלובלי",
  "workdays_per_week": 6
}
"""

LLM_RESPONSE_FENCED = f"""```json
{LLM_RESPONSE_FULL}
```"""


class MockLLM:
    def __init__(self, response: str):
        self._response = response
        self.call_count = 0

    def extract_from_images(self, images: list[bytes], prompt: str) -> str:
        self.call_count += 1
        return self._response


def _make_file(source: str, page: int = 0) -> PreparedFile:
    return PreparedFile(source_path=Path(source), data=b"img", mime_type="image/png", page_index=page)


def test_extract_full_contract():
    llm = MockLLM(LLM_RESPONSE_FULL)
    extractor = EmploymentContractExtractor(language_model=llm)

    records = extractor.extract([_make_file("contract.pdf")])

    assert llm.call_count == 1
    assert len(records) == 1
    record = records[0]
    assert record["employee_name"] == "ישראל ישראלי"
    assert record["employee_id"] == "012345678"
    assert record["employer_name"] == 'חברת דוגמה בע"מ'
    assert record["start_date"] == "01/03/2024"
    assert record["shortened_workday"] == "ערב שבת"
    assert record["weekly_rest_day"] == "שבת"
    assert record["employment_type"] == "משרה מלאה"
    assert record["overtime_calculation_after"] == "8 שעות"
    assert record["payment_type"] == "שעתי"
    assert record["workdays_per_week"] == 5
    assert record["source_file"] == "contract.pdf"
    assert record["page_in_document"] == 1
    assert "_llm_raw_text" in record


def test_extract_partial_contract():
    llm = MockLLM(LLM_RESPONSE_PARTIAL)
    extractor = EmploymentContractExtractor(language_model=llm)

    records = extractor.extract([_make_file("contract.pdf")])

    record = records[0]
    assert record["employee_name"] == "אבו נגמה זהיר"
    assert record["employee_id"] == "201007499"
    assert record["employer_name"] is None
    assert record["shortened_workday"] is None
    assert record["employment_type"] is None
    assert record["overtime_calculation_after"] is None
    assert record["weekly_rest_day"] == "שבת"
    assert record["payment_type"] == "גלובלי"
    assert record["workdays_per_week"] == 6


def test_parse_fenced_json():
    extractor = EmploymentContractExtractor(language_model=MockLLM(""))
    records = extractor.parse_cached_response(LLM_RESPONSE_FENCED)

    assert len(records) == 1
    record = records[0]
    assert record["employee_name"] == "ישראל ישראלי"
    assert record["workdays_per_week"] == 5
    assert "_llm_raw_text" in record


def test_parse_invalid_raises():
    extractor = EmploymentContractExtractor(language_model=MockLLM(""))
    with pytest.raises(ValueError, match="Could not find JSON"):
        extractor.parse_cached_response("no json content here")


def test_extract_empty_files():
    extractor = EmploymentContractExtractor(language_model=MockLLM(""))
    assert extractor.extract([]) == []
