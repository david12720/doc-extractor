import json
from pathlib import Path

from ..abstractions.status_tracker import StatusTracker

STAGES = ("prepare", "extract", "cache", "json_output")


class JsonStatusTracker(StatusTracker):
    def __init__(self, status_path: Path):
        self._path = status_path
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            self._data = json.loads(self._path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_status(self, file_key: str, stage: str) -> str | None:
        return self._data.get(file_key, {}).get(stage)

    def set_status(self, file_key: str, stage: str, status: str) -> None:
        if file_key not in self._data:
            self._data[file_key] = {}
        self._data[file_key][stage] = status
        self._save()

    def is_complete(self, file_key: str) -> bool:
        file_status = self._data.get(file_key, {})
        return all(file_status.get(stage) == "success" for stage in STAGES)
