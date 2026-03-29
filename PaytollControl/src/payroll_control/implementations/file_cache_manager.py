import json
from pathlib import Path

from ..abstractions.cache_manager import CacheManager


class FileCacheManager(CacheManager):
    def __init__(self, cache_dir: Path):
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _raw_path(self, key: str) -> Path:
        return self._cache_dir / f"{key}.txt"

    def _json_path(self, key: str) -> Path:
        return self._cache_dir / f"{key}.json"

    def has_cache(self, key: str) -> bool:
        return self._json_path(key).exists()

    def load_raw(self, key: str) -> str | None:
        path = self._raw_path(key)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def load_json(self, key: str) -> list[dict] | None:
        path = self._json_path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save_raw(self, key: str, raw_text: str) -> None:
        self._raw_path(key).write_text(raw_text, encoding="utf-8")

    def save_json(self, key: str, data: list[dict]) -> None:
        self._json_path(key).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
