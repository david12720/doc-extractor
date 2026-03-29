from pathlib import Path

from payroll_control.implementations.file_cache_manager import FileCacheManager


def test_save_and_load_raw(tmp_path: Path):
    cache = FileCacheManager(tmp_path / "cache")
    cache.save_raw("test_key", "raw response text")
    assert cache.load_raw("test_key") == "raw response text"


def test_save_and_load_json(tmp_path: Path):
    cache = FileCacheManager(tmp_path / "cache")
    data = [{"name": "Alice", "id": "123"}]
    cache.save_json("test_key", data)
    assert cache.load_json("test_key") == data


def test_has_cache_false_then_true(tmp_path: Path):
    cache = FileCacheManager(tmp_path / "cache")
    assert not cache.has_cache("key1")
    cache.save_json("key1", [])
    assert cache.has_cache("key1")


def test_load_missing_returns_none(tmp_path: Path):
    cache = FileCacheManager(tmp_path / "cache")
    assert cache.load_raw("nonexistent") is None
    assert cache.load_json("nonexistent") is None
