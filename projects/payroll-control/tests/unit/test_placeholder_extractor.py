import pytest

from pdf_pipeline.abstractions.file_preparator import PreparedFile
from payroll_control.features.placeholder.extractor import PlaceholderExtractor
from pathlib import Path


class MockLLM:
    def __init__(self, response: str):
        self._response = response
        self.call_count = 0

    def extract_from_image(self, image_bytes: bytes, prompt: str) -> str:
        self.call_count += 1
        return self._response

    def extract_from_pdf(self, pdf_bytes: bytes, prompt: str) -> str:
        return self._response


def test_extract_parses_json_from_llm():
    response = '[{"employee_name": "Test", "employee_id": "123", "gross_salary": "5000"}]'
    llm = MockLLM(response)
    extractor = PlaceholderExtractor(language_model=llm)

    files = [PreparedFile(source_path=Path("f.png"), data=b"img", mime_type="image/png", page_index=0)]
    records = extractor.extract(files)

    assert len(records) == 1
    assert records[0]["employee_name"] == "Test"
    assert llm.call_count == 1


def test_parse_cached_response():
    extractor = PlaceholderExtractor(language_model=MockLLM(""))
    raw = 'Some text before [{"employee_name": "A", "employee_id": "1", "gross_salary": "100"}] after'
    records = extractor.parse_cached_response(raw)
    assert len(records) == 1
    assert records[0]["employee_id"] == "1"


def test_parse_invalid_response_raises():
    extractor = PlaceholderExtractor(language_model=MockLLM(""))
    with pytest.raises(ValueError, match="Could not find JSON"):
        extractor.parse_cached_response("no json here")
