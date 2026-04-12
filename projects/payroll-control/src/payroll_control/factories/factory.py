import os
from pathlib import Path

from pdf_pipeline.abstractions.file_preparator import PreparationPipeline
from pdf_pipeline.config.settings import CACHE_DIR_NAME, COST_LOG_FILE_NAME, GEMINI_MODEL, GEMINI_MODEL_HANDWRITING, STATUS_FILE_NAME
from pdf_pipeline.core.excel_pipeline import ExcelPipeline
from pdf_pipeline.core.feature_registry import ExcelFeatureConfig, FeatureConfig, FeatureRegistry
from pdf_pipeline.core.pipeline import FeaturePipeline
from ..features.attendance.register import register as register_attendance
from ..features.excel_attendance.register import register as register_excel_attendance
from ..features.payslip.register import register as register_payslip
from ..features.placeholder.register import register as register_placeholder
from ..features.pension.register import register as register_pension
from ..features.employment_contract.register import register as register_employment_contract
from pdf_pipeline.implementations.csv_cost_logger import CsvCostLogger
from pdf_pipeline.implementations.file_cache_manager import FileCacheManager
from pdf_pipeline.implementations.gemini_model import GeminiModel
from pdf_pipeline.implementations.json_status_tracker import JsonStatusTracker
from pdf_pipeline.implementations.image_enhancer import ImageEnhancer
from pdf_pipeline.implementations.line_remover import LineRemover
from pdf_pipeline.implementations.llm_schema_detector import LlmSchemaDetector
from pdf_pipeline.implementations.openpyxl_reader import OpenpyxlReader
from pdf_pipeline.implementations.page_deskewer import PageDeskewer
from pdf_pipeline.implementations.page_rotator import PageRotator
from pdf_pipeline.implementations.pdf_to_image_converter import PdfToImageConverter
from pdf_pipeline.implementations.xlwings_mapper import XlwingsMapper

_llm: GeminiModel | None = None


def bootstrap(work_dir: Path, enable_ocr: bool = False) -> None:
    """Create shared infrastructure and register all features."""
    global _llm

    cost_logger = CsvCostLogger(work_dir / COST_LOG_FILE_NAME)
    fallback_dir = work_dir / CACHE_DIR_NAME / "fallback"

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    _llm = GeminiModel(api_key=api_key, model=GEMINI_MODEL, cost_logger=cost_logger, fallback_dir=fallback_dir)
    llm_handwriting = GeminiModel(api_key=api_key, model=GEMINI_MODEL_HANDWRITING, cost_logger=cost_logger, fallback_dir=fallback_dir)
    base_mapper = XlwingsMapper()

    ocr_engine = None
    if enable_ocr:
        from pdf_pipeline.implementations.cloud_vision_ocr import CloudVisionOcr
        ocr_engine = CloudVisionOcr(api_key=api_key, cost_logger=cost_logger)

    from pdf_pipeline.implementations.cloud_vision_ocr import CloudVisionOcr
    contract_ocr = CloudVisionOcr(api_key=api_key, cost_logger=cost_logger)

    register_attendance(language_model=_llm, base_mapper=base_mapper)
    register_payslip(language_model=_llm, base_mapper=base_mapper)
    register_placeholder(language_model=_llm, base_mapper=base_mapper)
    register_pension(language_model=_llm, base_mapper=base_mapper)
    register_employment_contract(language_model=llm_handwriting, base_mapper=base_mapper, ocr_engine=contract_ocr)
    register_excel_attendance()


def _default_steps() -> list:
    return [PageRotator(), PageDeskewer(), LineRemover(), ImageEnhancer()]


def _build_preparation(feature: FeatureConfig) -> PreparationPipeline:
    converter = PdfToImageConverter()
    steps = feature.preparation_steps if feature.preparation_steps is not None else _default_steps()
    return PreparationPipeline(converter=converter, steps=steps)


def create_pipeline(feature_name: str, work_dir: Path) -> FeaturePipeline | ExcelPipeline:
    feature = FeatureRegistry.get(feature_name)
    cache = FileCacheManager(work_dir / CACHE_DIR_NAME / feature_name)
    status = JsonStatusTracker(work_dir / STATUS_FILE_NAME)

    if isinstance(feature, ExcelFeatureConfig):
        return _build_excel_pipeline(feature, cache, status)

    preparation = _build_preparation(feature)
    return FeaturePipeline(
        feature=feature,
        preparation=preparation,
        cache=cache,
        status=status,
    )


def _build_excel_pipeline(
    feature: ExcelFeatureConfig,
    cache: FileCacheManager,
    status: JsonStatusTracker,
) -> ExcelPipeline:
    reader = OpenpyxlReader()
    schema_cache = FileCacheManager(cache._cache_dir / "schema")
    detector = LlmSchemaDetector(
        language_model=_llm,
        prompt=feature.schema_prompt,
        cache=schema_cache,
    )
    return ExcelPipeline(
        feature=feature,
        reader=reader,
        schema_detector=detector,
        cache=cache,
        status=status,
    )
