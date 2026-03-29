import pytest

from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry


class FakeExtractor:
    def extract(self, prepared_files):
        return []

    def parse_cached_response(self, raw_text):
        return []


class FakeMapper:
    def write(self, records, output_path):
        return output_path


@pytest.fixture(autouse=True)
def clean_registry():
    FeatureRegistry.clear()
    yield
    FeatureRegistry.clear()


def test_register_and_get():
    config = FeatureConfig(name="test", extractor=FakeExtractor(), mapper=FakeMapper())
    FeatureRegistry.register(config)
    assert FeatureRegistry.get("test") is config


def test_get_missing_raises():
    with pytest.raises(KeyError, match="not registered"):
        FeatureRegistry.get("nonexistent")


def test_list_features():
    FeatureRegistry.register(FeatureConfig(name="a", extractor=FakeExtractor(), mapper=FakeMapper()))
    FeatureRegistry.register(FeatureConfig(name="b", extractor=FakeExtractor(), mapper=FakeMapper()))
    assert sorted(FeatureRegistry.list_features()) == ["a", "b"]
