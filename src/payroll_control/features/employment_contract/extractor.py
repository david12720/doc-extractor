import json
import re

from ...abstractions.data_extractor import DataExtractor
from ...abstractions.file_preparator import PreparedFile
from ...abstractions.language_model import LanguageModel
from ...config.settings import CHUNK_SIZE_PAGES
from .prompt import PROMPT


class EmploymentContractExtractor(DataExtractor):
    def __init__(self, language_model: LanguageModel, chunk_size: int = CHUNK_SIZE_PAGES):
        self._llm = language_model
        self._chunk_size = chunk_size

    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        if not prepared_files:
            return []

        raw = self._llm.extract_from_images([pf.data for pf in prepared_files], PROMPT)
        record = self._parse_response(raw)

        record["_llm_raw_text"] = raw

        source_file = prepared_files[0].source_path.name
        record["source_file"] = source_file
        record["page_in_document"] = prepared_files[0].page_index + 1

        return [record]

    def parse_cached_response(self, raw_text: str) -> list[dict]:
        record = self._parse_response(raw_text)
        record["_llm_raw_text"] = raw_text
        return [record]

    def _parse_response(self, raw_text: str) -> dict:
        cleaned = self._extract_json_text(raw_text)
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            if len(parsed) == 1:
                return parsed[0]
            else:
                raise ValueError(f"Expected a single JSON object, but got a list with {len(parsed)} items.")
        return parsed

    def _extract_json_text(self, raw_text: str) -> str:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if fence_match:
            return fence_match.group(1).strip()

        brace_match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw_text)
        if brace_match:
            return brace_match.group(1).strip()

        raise ValueError(f"Could not find JSON in LLM response: {raw_text[:200]}")
