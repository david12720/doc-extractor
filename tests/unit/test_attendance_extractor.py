import pytest
from pathlib import Path

from payroll_control.abstractions.file_preparator import PreparedFile
from payroll_control.features.attendance.extractor import AttendanceExtractor


LLM_RESPONSE_ARRAY = """[
  {
    "employee_name": "ישראל ישראלי",
    "month": "03/2025",
    "image_number": 1,
    "is_summary": false,
    "attendance": [
      {"date": "01/03/2025", "from_time": "07:00", "to_time": "16:00"}
    ]
  },
  {
    "employee_name": "ישראל ישראלי",
    "month": "03/2025",
    "image_number": 2,
    "is_summary": true,
    "attendance": []
  },
  {
    "employee_name": "דוד כהן",
    "month": "02/2025",
    "image_number": 3,
    "is_summary": false,
    "attendance": [
      {"date": "01/02/2025", "from_time": "08:00", "to_time": "17:00"}
    ]
  }
]"""

LLM_RESPONSE_FENCED = """```json
[
  {
    "employee_name": "דוד כהן",
    "month": "02/2025",
    "image_number": 1,
    "is_summary": false,
    "attendance": [
      {"date": "01/02/2025", "from_time": "08:00", "to_time": "17:00"}
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


def test_extract_chunk_with_summaries_skipped():
    llm = MockLLM(LLM_RESPONSE_ARRAY)
    extractor = AttendanceExtractor(language_model=llm, chunk_size=40)

    files = _make_files("report.pdf", 3)
    records = extractor.extract(files)

    assert llm.call_count == 1  # single chunk
    assert len(records) == 2  # summary page skipped
    assert records[0]["employee_name"] == "ישראל ישראלי"
    assert records[0]["page_in_document"] == 1  # image_number=1, page_start=0 -> 0+1=1
    assert records[1]["employee_name"] == "דוד כהן"
    assert records[1]["page_in_document"] == 3  # image_number=3, page_start=0 -> 0+3=3
    assert records[0]["source_file"] == "report.pdf"


def test_extract_multiple_chunks():
    llm = MockLLM(LLM_RESPONSE_FENCED)
    extractor = AttendanceExtractor(language_model=llm, chunk_size=2)

    files = _make_files("doc.pdf", 5)
    records = extractor.extract(files)

    assert llm.call_count == 3  # ceil(5/2) = 3 chunks
    # Each chunk returns 1 record (image_number=1)
    # Chunk 0: pages 0-1, page_in_document = 0+1 = 1
    # Chunk 1: pages 2-3, page_in_document = 2+1 = 3
    # Chunk 2: page 4, page_in_document = 4+1 = 5
    assert len(records) == 3
    assert records[0]["page_in_document"] == 1
    assert records[1]["page_in_document"] == 3
    assert records[2]["page_in_document"] == 5


def test_page_in_document_offset():
    """Second chunk (page_start=40): image_number is offset correctly."""
    response = """[{"employee_name": "A", "month": "01/2025", "image_number": 5, "is_summary": false,
      "first_row_description": "x", "attendance": []}]"""
    llm = MockLLM(response)
    extractor = AttendanceExtractor(language_model=llm, chunk_size=40)

    # Simulate pages 40-79 (second chunk of a large PDF)
    files = [
        PreparedFile(source_path=Path("big.pdf"), data=b"img", mime_type="image/png", page_index=i)
        for i in range(40, 80)
    ]
    records = extractor.extract(files)

    assert records[0]["page_in_document"] == 40 + 5  # page_start=40, image_number=5


def test_parse_fenced_json():
    extractor = AttendanceExtractor(language_model=MockLLM(""))
    records = extractor.parse_cached_response(LLM_RESPONSE_FENCED)

    assert len(records) == 1
    assert records[0]["employee_name"] == "דוד כהן"


def test_parse_invalid_raises():
    extractor = AttendanceExtractor(language_model=MockLLM(""))
    with pytest.raises(ValueError, match="Could not find JSON"):
        extractor.parse_cached_response("no json content here")
