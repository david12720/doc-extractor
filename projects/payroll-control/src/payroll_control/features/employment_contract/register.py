from pdf_pipeline.abstractions.file_preparator import PreparationStep
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.abstractions.ocr_engine import OcrEngine
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import EmploymentContractExtractor
from .mapper import EmploymentContractMapper

FEATURE_NAME = "employment_contract"


def register(
    language_model: LanguageModel,
    preparation_steps: list[PreparationStep] | None = None,
    raw_pdf: bool = True,
    ocr_engine: OcrEngine | None = None,
    **_kwargs,
) -> None:
    extractor = EmploymentContractExtractor(language_model=language_model)
    mapper = EmploymentContractMapper()
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
        preparation_steps=preparation_steps,
        raw_pdf=raw_pdf,
        ocr_engine=ocr_engine,
    ))
