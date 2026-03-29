import json

from pdf_pipeline.abstractions.schema_detector import ColumnMapping
from pdf_pipeline.implementations.llm_schema_detector import LlmSchemaDetector


class FakeLanguageModel:
    def __init__(self, response: str):
        self._response = response
        self.calls: list[tuple[str, str]] = []

    def extract_from_text(self, text: str, prompt: str) -> str:
        self.calls.append((text, prompt))
        return self._response

    def extract_from_image(self, image_bytes, prompt):
        raise NotImplementedError

    def extract_from_images(self, images, prompt):
        raise NotImplementedError

    def extract_from_pdf(self, pdf_bytes, prompt):
        raise NotImplementedError


class FakeCacheManager:
    def __init__(self):
        self._raw: dict[str, str] = {}
        self._json: dict[str, list] = {}

    def has_cache(self, key: str) -> bool:
        return key in self._json

    def load_raw(self, key: str) -> str | None:
        return self._raw.get(key)

    def load_json(self, key: str) -> list | None:
        return self._json.get(key)

    def save_raw(self, key: str, raw_text: str) -> None:
        self._raw[key] = raw_text

    def save_json(self, key: str, data) -> None:
        self._json[key] = data


LLM_RESPONSE = json.dumps({
    "person_id_column": "A",
    "date_column": "D",
    "from_time_column": "E",
    "to_time_column": "F",
    "header_row": 2,
    "data_start_row": 3,
})


class TestLlmSchemaDetector:
    def test_detect_calls_llm_and_returns_mapping(self):
        llm = FakeLanguageModel(LLM_RESPONSE)
        cache = FakeCacheManager()
        detector = LlmSchemaDetector(llm, "detect columns", cache)

        result = detector.detect("Row 1: foo | bar")

        assert result == ColumnMapping(
            person_id_column="A",
            date_column="D",
            from_time_column="E",
            to_time_column="F",
            header_row=2,
            data_start_row=3,
        )
        assert len(llm.calls) == 1

    def test_caches_result_after_detection(self):
        llm = FakeLanguageModel(LLM_RESPONSE)
        cache = FakeCacheManager()
        detector = LlmSchemaDetector(llm, "detect columns", cache)

        detector.detect("Row 1: foo | bar")

        assert cache.load_json("schema") is not None
        assert cache.load_raw("schema") == LLM_RESPONSE

    def test_uses_cache_on_second_call(self):
        llm = FakeLanguageModel(LLM_RESPONSE)
        cache = FakeCacheManager()
        detector = LlmSchemaDetector(llm, "detect columns", cache)

        detector.detect("Row 1: foo | bar")
        result = detector.detect("Row 1: different | data")

        assert len(llm.calls) == 1
        assert result.date_column == "D"

    def test_parses_fenced_json(self):
        fenced = "```json\n" + LLM_RESPONSE + "\n```"
        llm = FakeLanguageModel(fenced)
        cache = FakeCacheManager()
        detector = LlmSchemaDetector(llm, "detect", cache)

        result = detector.detect("headers")
        assert result.date_column == "D"

    def test_parses_json_with_surrounding_text(self):
        response = "Here is the result:\n" + LLM_RESPONSE + "\nDone."
        llm = FakeLanguageModel(response)
        cache = FakeCacheManager()
        detector = LlmSchemaDetector(llm, "detect", cache)

        result = detector.detect("headers")
        assert result.from_time_column == "E"
