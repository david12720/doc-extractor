import pytest
from pathlib import Path

from pdf_pipeline.abstractions.file_preparator import PreparedFile
from payroll_control.features.payslip.extractor import PayslipExtractor


LLM_RESPONSE_ARRAY = """[
  {
    "employee_id": "123456789",
    "employee_name": "כהן אליהו",
    "month": "02/2025",
    "image_number": 1,
    "hourly_wage": "35.00",
    "gross_salary": "7500.00",
    "net_salary": "6200.00",
    "hours_breakdown": [
      {"category": "רגילות", "hours": "176.00", "amount_nis": "6160.00"},
      {"category": "נוספות 125%", "hours": "10.00", "amount_nis": "437.50"},
      {"category": "נוספות 150%", "hours": "5.00", "amount_nis": "262.50"},
      {"category": "שבת 150%", "hours": "8.00", "amount_nis": "420.00"},
      {"category": "שבת 175%", "hours": "0.00", "amount_nis": "0.00"},
      {"category": "שבת 200%", "hours": "0.00", "amount_nis": "0.00"}
    ]
  },
  {
    "employee_id": "123456789",
    "employee_name": "כהן אליהו",
    "month": "03/2025",
    "image_number": 2,
    "hourly_wage": "35.00",
    "gross_salary": "7200.00",
    "net_salary": "5900.00",
    "hours_breakdown": [
      {"category": "רגילות", "hours": "170.00", "amount_nis": "5950.00"},
      {"category": "נוספות 125%", "hours": "8.00", "amount_nis": "350.00"},
      {"category": "נוספות 150%", "hours": "0.00", "amount_nis": "0.00"},
      {"category": "שבת 150%", "hours": "0.00", "amount_nis": "0.00"},
      {"category": "שבת 175%", "hours": "0.00", "amount_nis": "0.00"},
      {"category": "שבת 200%", "hours": "0.00", "amount_nis": "0.00"}
    ]
  }
]"""

LLM_RESPONSE_FENCED = """```json
[
  {
    "employee_id": "123456789",
    "employee_name": "כהן אליהו",
    "month": "02/2025",
    "image_number": 1,
    "hourly_wage": "35.00",
    "gross_salary": "7500.00",
    "net_salary": "6200.00",
    "hours_breakdown": [
      {"category": "רגילות", "hours": "176.00", "amount_nis": "6160.00"}
    ]
  }
]
```"""


class MockLLM:
    def __init__(self, response: str):
        self._response = response
        self.call_count = 0

    def extract_from_image(self, image_bytes: bytes, prompt: str) -> str:
        self.call_count += 1
        return self._response

    def extract_from_images(self, images: list[bytes], prompt: str) -> str:
        self.call_count += 1
        return self._response

    def extract_from_pdf(self, pdf_bytes: bytes, prompt: str) -> str:
        self.call_count += 1
        return self._response


def _make_files(source: str, count: int) -> list[PreparedFile]:
    return [
        PreparedFile(source_path=Path(source), data=b"img", mime_type="image/png", page_index=i)
        for i in range(count)
    ]


def test_extract_two_months():
    llm = MockLLM(LLM_RESPONSE_ARRAY)
    extractor = PayslipExtractor(language_model=llm, chunk_size=40)

    files = _make_files("payslip.pdf", 2)
    records = extractor.extract(files)

    assert llm.call_count == 1
    assert len(records) == 2
    assert records[0]["employee_id"] == "123456789"
    assert records[0]["month"] == "02/2025"
    assert records[0]["hourly_wage"] == "35.00"
    assert len(records[0]["hours_breakdown"]) == 6
    assert records[0]["hours_breakdown"][0]["category"] == "רגילות"
    assert records[0]["hours_breakdown"][0]["hours"] == "176.00"
    assert records[0]["source_file"] == "payslip.pdf"
    assert records[0]["page_in_document"] == 1

    assert records[1]["month"] == "03/2025"
    assert records[1]["page_in_document"] == 2


def test_extract_multiple_chunks():
    llm = MockLLM(LLM_RESPONSE_FENCED)
    extractor = PayslipExtractor(language_model=llm, chunk_size=2)

    files = _make_files("payslip.pdf", 5)
    records = extractor.extract(files)

    assert llm.call_count == 3
    assert len(records) == 3
    assert records[0]["page_in_document"] == 1
    assert records[1]["page_in_document"] == 3
    assert records[2]["page_in_document"] == 5


def test_page_in_document_offset():
    response = """[{"employee_id": "111", "employee_name": "A", "month": "01/2025",
      "image_number": 3, "hourly_wage": "30.00", "gross_salary": "5000.00",
      "net_salary": "4000.00", "hours_breakdown": []}]"""
    llm = MockLLM(response)
    extractor = PayslipExtractor(language_model=llm, chunk_size=40)

    files = [
        PreparedFile(source_path=Path("big.pdf"), data=b"img", mime_type="image/png", page_index=i)
        for i in range(40, 80)
    ]
    records = extractor.extract(files)

    assert records[0]["page_in_document"] == 40 + 3


def test_parse_fenced_json():
    extractor = PayslipExtractor(language_model=MockLLM(""))
    records = extractor.parse_cached_response(LLM_RESPONSE_FENCED)

    assert len(records) == 1
    assert records[0]["employee_id"] == "123456789"
    assert records[0]["gross_salary"] == "7500.00"


def test_parse_invalid_raises():
    extractor = PayslipExtractor(language_model=MockLLM(""))
    with pytest.raises(ValueError, match="Could not find JSON"):
        extractor.parse_cached_response("no json content here")
