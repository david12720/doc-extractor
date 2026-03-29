from ...abstractions.language_model import LanguageModel
from ...core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import PensionExtractor
from .mapper import PensionMapper

FEATURE_NAME = "pension"


def register(language_model: LanguageModel, **_kwargs) -> None:
    extractor = PensionExtractor(language_model=language_model)
    mapper = PensionMapper()
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
    ))
