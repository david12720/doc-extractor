import json
import re

from ...abstractions.data_extractor import DataExtractor
from ...abstractions.file_preparator import PreparedFile
from ...abstractions.language_model import LanguageModel
from .prompt import PROMPT


class PlaceholderExtractor(DataExtractor):
    def __init__(self, language_model: LanguageModel):
        self._llm = language_model

    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        all_records: list[dict] = []
        for pf in prepared_files:
            raw = self._llm.extract_from_image(pf.data, PROMPT)
            records = self.parse_cached_response(raw)
            all_records.extend(records)
        return all_records

    def parse_cached_response(self, raw_text: str) -> list[dict]:
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if not match:
            raise ValueError(f"Could not find JSON array in LLM response: {raw_text[:200]}")
        return json.loads(match.group())
