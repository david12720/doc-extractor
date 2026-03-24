from ...abstractions.language_model import LanguageModel
from ...core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import EmploymentContractExtractor
from .mapper import EmploymentContractMapper

FEATURE_NAME = "employment_contract"


def register(language_model: LanguageModel, **_kwargs) -> None:
    extractor = EmploymentContractExtractor(language_model=language_model)
    mapper = EmploymentContractMapper()
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
    ))
