import pytest
from pathlib import Path

from payroll_control.abstractions.file_preparator import PreparedFile
from payroll_control.features.pension.extractor import PensionExtractor

LLM_RESPONSE = """
{
  "company_name": "מגדל חברה לביטוח בעמ",
  "insured_person_name": "אבו נגמה זהיר",
  "insured_person_id": "201007499",
  "report_date": "10/12/2025",
  "deposits": [
    {
      "account_number": "44783603",
      "value_date": "16/11/2025",
      "salary_month": "10/2025",
      "employer_contribution": 356.94,
      "employee_contribution": null,
      "severance_contribution": 0.00,
      "total_contribution": 475.92
    },
    {
      "account_number": "44783603",
      "value_date": "15/10/2025",
      "salary_month": "09/2025",
      "employer_contribution": null,
      "employee_contribution": 98.21,
      "severance_contribution": 0.00,
      "total_contribution": 392.83
    }
  ]
}
"""

LLM_RESPONSE_FENCED = f"""```json
{LLM_RESPONSE}
```"""


class MockLLM:
    def __init__(self, response: str):
        self._response = response
        self.call_count = 0

    def extract_from_images(self, images: list[bytes], prompt: str) -> str:
        self.call_count += 1
        return self._response

def _make_file(source: str) -> PreparedFile:
    return PreparedFile(source_path=Path(source), data=b"img", mime_type="image/png", page_index=0)


def test_extract_single_report():
    llm = MockLLM(LLM_RESPONSE)
    extractor = PensionExtractor(language_model=llm)

    file = _make_file("pension.pdf")
    records = extractor.extract([file])

    assert llm.call_count == 1
    assert len(records) == 1
    record = records[0]
    assert record["company_name"] == "מגדל חברה לביטוח בעמ"
    assert record["insured_person_id"] == "201007499"
    assert record["source_file"] == "pension.pdf"
    assert record["page_in_document"] == 1
    assert "_llm_raw_text" in record


def test_fill_missing_employee_contribution():
    llm = MockLLM(LLM_RESPONSE)
    extractor = PensionExtractor(language_model=llm)

    records = extractor.extract([_make_file("pension.pdf")])
    deposit = records[0]["deposits"][0]

    # employer=356.94, total=475.92, severance=0 -> employee=118.98
    assert deposit["employee_contribution"] == 118.98


def test_fill_missing_employer_contribution():
    llm = MockLLM(LLM_RESPONSE)
    extractor = PensionExtractor(language_model=llm)

    records = extractor.extract([_make_file("pension.pdf")])
    deposit = records[0]["deposits"][1]

    # employee=98.21, total=392.83, severance=0 -> employer=294.62
    assert deposit["employer_contribution"] == 294.62


def test_parse_fenced_json():
    extractor = PensionExtractor(language_model=MockLLM(""))
    records = extractor.parse_cached_response(LLM_RESPONSE_FENCED)

    assert len(records) == 1
    record = records[0]
    assert record["company_name"] == "מגדל חברה לביטוח בעמ"
    assert len(record["deposits"]) == 2
    assert "_llm_raw_text" in record


def test_parse_invalid_raises():
    extractor = PensionExtractor(language_model=MockLLM(""))
    with pytest.raises(ValueError, match="Could not find JSON"):
        extractor.parse_cached_response("no json content here")
