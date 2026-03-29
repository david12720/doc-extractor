import json
import re

from ..abstractions.cache_manager import CacheManager
from ..abstractions.language_model import LanguageModel
from ..abstractions.schema_detector import ColumnMapping, SchemaDetector

class LlmSchemaDetector(SchemaDetector):
    def __init__(self, language_model: LanguageModel, prompt: str, cache: CacheManager):
        self._llm = language_model
        self._prompt = prompt
        self._cache = cache

    def detect(self, headers_text: str, cache_key: str = "schema") -> ColumnMapping:
        cached = self._load_cached(cache_key)
        if cached is not None:
            print(f"[schema] Loaded column mapping from cache ({cache_key}).")
            return cached

        raw = self._llm.extract_from_text(headers_text, self._prompt)
        self._cache.save_raw(cache_key, raw)
        mapping = self._parse_response(raw)
        self._cache.save_json(cache_key, [self._mapping_to_dict(mapping)])
        print(f"[schema] Detected columns: person_id={mapping.person_id_column}, "
              f"date={mapping.date_column}, from={mapping.from_time_column}, "
              f"to={mapping.to_time_column}, header_row={mapping.header_row}, "
              f"data_start={mapping.data_start_row}")
        return mapping

    def _load_cached(self, cache_key: str) -> ColumnMapping | None:
        data = self._cache.load_json(cache_key)
        if data is None:
            return None
        entry = data[0]
        return ColumnMapping(
            person_id_column=entry["person_id_column"],
            date_column=entry["date_column"],
            from_time_column=entry["from_time_column"],
            to_time_column=entry["to_time_column"],
            header_row=entry["header_row"],
            data_start_row=entry["data_start_row"],
        )

    def _parse_response(self, raw_text: str) -> ColumnMapping:
        cleaned = self._extract_json_text(raw_text)
        data = json.loads(cleaned)
        return ColumnMapping(
            person_id_column=str(data["person_id_column"]),
            date_column=str(data["date_column"]),
            from_time_column=str(data["from_time_column"]),
            to_time_column=str(data["to_time_column"]),
            header_row=int(data["header_row"]),
            data_start_row=int(data["data_start_row"]),
        )

    def _extract_json_text(self, raw_text: str) -> str:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if fence_match:
            return fence_match.group(1).strip()
        brace_match = re.search(r"(\{[\s\S]*\})", raw_text)
        if brace_match:
            return brace_match.group(1).strip()
        raise ValueError(f"Could not find JSON in LLM response: {raw_text[:200]}")

    def _mapping_to_dict(self, mapping: ColumnMapping) -> dict:
        return {
            "person_id_column": mapping.person_id_column,
            "date_column": mapping.date_column,
            "from_time_column": mapping.from_time_column,
            "to_time_column": mapping.to_time_column,
            "header_row": mapping.header_row,
            "data_start_row": mapping.data_start_row,
        }
