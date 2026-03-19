"""Integration test: full pipeline with mocked LLM.

Verifies: prepare -> extract (mocked) -> cache -> JSON output -> resume skips LLM.
"""
import json
from pathlib import Path

import pytest

from payroll_control.abstractions.data_extractor import DataExtractor
from payroll_control.abstractions.excel_mapper import ExcelMapper
from payroll_control.abstractions.file_preparator import (
    FileConverter,
    PreparationPipeline,
    PreparedFile,
)
from payroll_control.core.feature_registry import FeatureConfig, FeatureRegistry
from payroll_control.core.pipeline import FeaturePipeline
from payroll_control.implementations.file_cache_manager import FileCacheManager
from payroll_control.implementations.json_status_tracker import JsonStatusTracker


LLM_RESPONSE = '[{"employee_name": "Test User", "employee_id": "123456789", "gross_salary": "10000"}]'


class FakeConverter(FileConverter):
    def convert(self, input_files: list[Path]) -> list[PreparedFile]:
        return [
            PreparedFile(source_path=p, data=b"fake_image", mime_type="image/png", page_index=0)
            for p in input_files
        ]


class FakeLLM:
    def __init__(self):
        self.call_count = 0

    def extract_from_image(self, image_bytes: bytes, prompt: str) -> str:
        self.call_count += 1
        return LLM_RESPONSE

    def extract_from_pdf(self, pdf_bytes: bytes, prompt: str) -> str:
        self.call_count += 1
        return LLM_RESPONSE


class FakeExtractor(DataExtractor):
    def __init__(self, llm: FakeLLM):
        self._llm = llm

    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        all_records = []
        for pf in prepared_files:
            raw = self._llm.extract_from_image(pf.data, "prompt")
            all_records.extend(json.loads(raw))
        return all_records

    def parse_cached_response(self, raw_text: str) -> list[dict]:
        return json.loads(raw_text)


class FakeMapper(ExcelMapper):
    def write(self, records: list[dict], output_path: Path) -> Path:
        return output_path


@pytest.fixture(autouse=True)
def clean_registry():
    FeatureRegistry.clear()
    yield
    FeatureRegistry.clear()


@pytest.fixture
def work_dir(tmp_path: Path) -> Path:
    return tmp_path / "work"


def _build_pipeline(work_dir: Path, llm: FakeLLM) -> FeaturePipeline:
    extractor = FakeExtractor(llm)
    mapper = FakeMapper()
    config = FeatureConfig(name="test_feature", extractor=extractor, mapper=mapper)
    FeatureRegistry.register(config)

    converter = FakeConverter()
    preparation = PreparationPipeline(converter=converter)
    cache = FileCacheManager(work_dir / "cache" / "test_feature")
    status = JsonStatusTracker(work_dir / "status.json")

    return FeaturePipeline(
        feature=config,
        preparation=preparation,
        cache=cache,
        status=status,
    )


def test_full_pipeline_extract_cache_json(work_dir: Path, tmp_path: Path):
    llm = FakeLLM()
    pipeline = _build_pipeline(work_dir, llm)

    input_file = tmp_path / "input.pdf"
    input_file.write_bytes(b"fake pdf")
    output_path = work_dir / "output" / "result.json"

    result = pipeline.run([input_file], output_path)

    assert result == output_path
    assert output_path.exists()
    assert llm.call_count == 1

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["employee_name"] == "Test User"

    # Verify cache was created
    cache_dir = work_dir / "cache" / "test_feature"
    assert (cache_dir / "test_feature.json").exists()

    # Verify status was set
    status = JsonStatusTracker(work_dir / "status.json")
    assert status.is_complete("test_feature")


def test_resume_skips_llm(work_dir: Path, tmp_path: Path):
    llm = FakeLLM()
    pipeline = _build_pipeline(work_dir, llm)

    input_file = tmp_path / "input.pdf"
    input_file.write_bytes(b"fake pdf")
    output_path = work_dir / "output" / "result.json"

    # First run -- LLM is called
    pipeline.run([input_file], output_path)
    assert llm.call_count == 1

    # Second run -- rebuild pipeline (simulates new process), LLM should be skipped
    llm2 = FakeLLM()
    pipeline2 = _build_pipeline(work_dir, llm2)
    pipeline2.run([input_file], output_path)

    assert llm2.call_count == 0  # LLM not called -- loaded from cache
