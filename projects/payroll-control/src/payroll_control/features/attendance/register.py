from pdf_pipeline.abstractions.excel_mapper import ExcelMapper
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import AttendanceExtractor
from .mapper import AttendanceMapper

FEATURE_NAME = "attendance"


def register(language_model: LanguageModel, base_mapper: ExcelMapper) -> None:
    extractor = AttendanceExtractor(language_model=language_model)
    mapper = AttendanceMapper(base_mapper=base_mapper)
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
    ))
