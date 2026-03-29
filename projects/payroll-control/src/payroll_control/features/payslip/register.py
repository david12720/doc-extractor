from pdf_pipeline.abstractions.excel_mapper import ExcelMapper
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import PayslipExtractor
from .mapper import PayslipMapper

FEATURE_NAME = "payslip"


def register(language_model: LanguageModel, base_mapper: ExcelMapper) -> None:
    extractor = PayslipExtractor(language_model=language_model)
    mapper = PayslipMapper(base_mapper=base_mapper)
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
    ))
