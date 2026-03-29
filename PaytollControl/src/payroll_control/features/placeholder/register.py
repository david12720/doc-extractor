from ...abstractions.excel_mapper import ExcelMapper
from ...abstractions.language_model import LanguageModel
from ...core.feature_registry import FeatureConfig, FeatureRegistry
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
