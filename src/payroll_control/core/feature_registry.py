from dataclasses import dataclass, field
from typing import Callable

from ..abstractions.data_extractor import DataExtractor
from ..abstractions.excel_mapper import ExcelMapper
from ..abstractions.file_preparator import PreparationStep
from ..abstractions.schema_detector import ColumnMapping


@dataclass(frozen=True)
class FeatureConfig:
    name: str
    extractor: DataExtractor
    mapper: ExcelMapper
    preparation_steps: list[PreparationStep] | None = field(default=None)
    raw_pdf: bool = False


@dataclass(frozen=True)
class ExcelFeatureConfig:
    name: str
    schema_prompt: str
    record_builder: Callable[[list[list], ColumnMapping, str], list[dict]]


class FeatureRegistry:
    _features: dict[str, FeatureConfig | ExcelFeatureConfig] = {}

    @classmethod
    def register(cls, config: FeatureConfig | ExcelFeatureConfig) -> None:
        cls._features[config.name] = config

    @classmethod
    def get(cls, name: str) -> FeatureConfig | ExcelFeatureConfig:
        if name not in cls._features:
            available = ", ".join(cls._features.keys()) or "(none)"
            raise KeyError(f"Feature '{name}' not registered. Available: {available}")
        return cls._features[name]

    @classmethod
    def list_features(cls) -> list[str]:
        return list(cls._features.keys())

    @classmethod
    def clear(cls) -> None:
        cls._features.clear()
