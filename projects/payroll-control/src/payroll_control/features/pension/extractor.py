import json
import re

from pdf_pipeline.abstractions.data_extractor import DataExtractor
from pdf_pipeline.abstractions.file_preparator import PreparedFile
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.config.settings import CHUNK_SIZE_PAGES
from .prompt import PROMPT


class PensionExtractor(DataExtractor):
    def __init__(self, language_model: LanguageModel, chunk_size: int = CHUNK_SIZE_PAGES):
        self._llm = language_model
        self._chunk_size = chunk_size

    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        if not prepared_files:
            return []

        raw = self._llm.extract_from_images([pf.data for pf in prepared_files], PROMPT)
        record = self._parse_response(raw)

        record["_llm_raw_text"] = raw  # pipeline will separate this to its own file
        self._fill_missing_contributions(record)

        source_file = prepared_files[0].source_path.name
        record["source_file"] = source_file
        record["page_in_document"] = prepared_files[0].page_index + 1

        return [record]

    def parse_cached_response(self, raw_text: str) -> list[dict]:
        record = self._parse_response(raw_text)
        record["_llm_raw_text"] = raw_text
        self._fill_missing_contributions(record)
        return [record]

    def _fill_missing_contributions(self, record: dict) -> None:
        for deposit in record.get("deposits", []):
            total = deposit.get("total_contribution")
            employer = deposit.get("employer_contribution")
            employee = deposit.get("employee_contribution")
            severance = deposit.get("severance_contribution") or 0.0

            if total is None:
                continue

            if employee is None and employer is not None:
                deposit["employee_contribution"] = round(total - employer - severance, 2)
            elif employer is None and employee is not None:
                deposit["employer_contribution"] = round(total - employee - severance, 2)

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
