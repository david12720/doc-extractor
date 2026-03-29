import json
import re

from pdf_pipeline.abstractions.data_extractor import DataExtractor
from pdf_pipeline.abstractions.file_preparator import PreparedFile
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.config.settings import CHUNK_SIZE_PAGES
from .prompt import PROMPT


class AttendanceExtractor(DataExtractor):
    def __init__(self, language_model: LanguageModel, chunk_size: int = CHUNK_SIZE_PAGES):
        self._llm = language_model
        self._chunk_size = chunk_size

    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        all_records: list[dict] = []
        chunks = self._group_into_chunks(prepared_files)

        for chunk_idx, chunk in enumerate(chunks):
            page_start = chunk[0].page_index
            print(f"  Chunk {chunk_idx + 1}/{len(chunks)}: {len(chunk)} images (pages {page_start + 1}-{chunk[-1].page_index + 1})")

            image_data = [pf.data for pf in chunk]
            raw = self._llm.extract_from_images(image_data, PROMPT)
            records = self._parse_response(raw)

            for record in records:
                if record.get("is_summary", False):
                    continue
                source_file = chunk[0].source_path.name
                image_number = record.get("image_number", 1)
                record["source_file"] = source_file
                record["page_in_document"] = page_start + image_number
                all_records.append(record)

        return all_records

    def parse_cached_response(self, raw_text: str) -> list[dict]:
        cleaned = self._extract_json_text(raw_text)
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
        return [parsed]

    def _group_into_chunks(self, files: list[PreparedFile]) -> list[list[PreparedFile]]:
        chunks: list[list[PreparedFile]] = []
        for i in range(0, len(files), self._chunk_size):
            chunks.append(files[i:i + self._chunk_size])
        return chunks

    def _parse_response(self, raw_text: str) -> list[dict]:
        cleaned = self._extract_json_text(raw_text)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return [parsed]
        return parsed

    def _extract_json_text(self, raw_text: str) -> str:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if fence_match:
            return fence_match.group(1).strip()

        brace_match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw_text)
        if brace_match:
            return brace_match.group(1).strip()

        raise ValueError(f"Could not find JSON in LLM response: {raw_text[:200]}")
