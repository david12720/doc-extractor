from ...abstractions.excel_mapper import ExcelMapper
from ...abstractions.language_model import LanguageModel
from ...core.feature_registry import FeatureConfig, FeatureRegistry
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
