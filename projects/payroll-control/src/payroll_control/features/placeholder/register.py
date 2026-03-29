from pdf_pipeline.abstractions.excel_mapper import ExcelMapper
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import PlaceholderExtractor
from .mapper import PlaceholderMapper

FEATURE_NAME = "placeholder"


def register(language_model: LanguageModel, base_mapper: ExcelMapper) -> None:
    extractor = PlaceholderExtractor(language_model=language_model)
    mapper = PlaceholderMapper(base_mapper=base_mapper)
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
    ))
