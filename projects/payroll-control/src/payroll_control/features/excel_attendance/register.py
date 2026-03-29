from pdf_pipeline.core.feature_registry import ExcelFeatureConfig, FeatureRegistry
from .prompt import SCHEMA_DETECTION_PROMPT
from .record_builder import build_records

FEATURE_NAME = "excel_attendance"


def register() -> None:
    FeatureRegistry.register(ExcelFeatureConfig(
        name=FEATURE_NAME,
        schema_prompt=SCHEMA_DETECTION_PROMPT,
        record_builder=build_records,
    ))
