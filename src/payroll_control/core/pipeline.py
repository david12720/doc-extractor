import json
from pathlib import Path

from ..abstractions.cache_manager import CacheManager
from ..abstractions.file_preparator import PreparedFile, PreparationPipeline
from ..abstractions.status_tracker import StatusTracker
from .feature_registry import FeatureConfig
from .file_key import build_file_key


class FeaturePipeline:
    def __init__(
        self,
        feature: FeatureConfig,
        preparation: PreparationPipeline,
        cache: CacheManager,
        status: StatusTracker,
    ):
        self._feature = feature
        self._preparation = preparation
        self._cache = cache
        self._status = status

    def run(self, input_files: list[Path], output_path: Path) -> Path:
        file_key = build_file_key(self._feature.name, input_files)

        if self._status.is_complete(file_key):
            print(f"[{file_key}] All stages complete -- skipping.")
            return output_path

        records = self._try_load_from_cache(file_key)
        if records is None:
            records = self._extract(input_files, file_key)

        json_path = self._write_json(records, output_path, file_key)
        self._status.set_status(file_key, "json_output", "success")
        return json_path

    def _try_load_from_cache(self, file_key: str) -> list[dict] | None:
        if not self._cache.has_cache(file_key):
            return None

        json_data = self._cache.load_json(file_key)
        if json_data is not None:
            print(f"[{file_key}] Loaded {len(json_data)} records from JSON cache.")
            self._status.set_status(file_key, "extract", "success")
            self._status.set_status(file_key, "cache", "success")
            return json_data

        raw = self._cache.load_raw(file_key)
        if raw is not None:
            print(f"[{file_key}] Parsing cached raw response...")
            records = self._feature.extractor.parse_cached_response(raw)
            self._cache.save_json(file_key, records)
            self._status.set_status(file_key, "extract", "success")
            self._status.set_status(file_key, "cache", "success")
            return records

        return None

    def _extract(self, input_files: list[Path], file_key: str) -> list[dict]:
        if self._feature.raw_pdf:
            return self._extract_raw_pdf(input_files, file_key)

        print(f"[{file_key}] Preparing files...")
        prepared = self._preparation.prepare(input_files)
        self._save_debug_pages(prepared, file_key)
        self._status.set_status(file_key, "prepare", "success")

        print(f"[{file_key}] Extracting data from {len(prepared)} prepared file(s)...")
        try:
            records = self._feature.extractor.extract(prepared)
            self._status.set_status(file_key, "extract", "success")
        except Exception as e:
            self._status.set_status(file_key, "extract", f"failed: {e}")
            raise

        self._cache.save_json(file_key, records)
        self._status.set_status(file_key, "cache", "success")
        print(f"[{file_key}] Cached {len(records)} record(s).")
        return records

    def _extract_raw_pdf(self, input_files: list[Path], file_key: str) -> list[dict]:
        print(f"[{file_key}] Sending raw PDF to LLM...")
        prepared = []
        for path in input_files:
            prepared.append(PreparedFile(
                source_path=path,
                data=path.read_bytes(),
                mime_type="application/pdf",
                page_index=0,
            ))
        self._status.set_status(file_key, "prepare", "success")

        print(f"[{file_key}] Extracting data from {len(prepared)} PDF file(s)...")
        try:
            records = self._feature.extractor.extract(prepared)
            self._status.set_status(file_key, "extract", "success")
        except Exception as e:
            self._status.set_status(file_key, "extract", f"failed: {e}")
            raise

        self._cache.save_json(file_key, records)
        self._status.set_status(file_key, "cache", "success")
        print(f"[{file_key}] Cached {len(records)} record(s).")
        return records

    def _save_debug_pages(self, prepared: list, file_key: str) -> None:
        debug_dir = Path("cache/debug_pages")
        if not debug_dir.exists():
            return
        for pf in prepared:
            page = pf.page_index if pf.page_index is not None else 0
            path = debug_dir / f"{file_key}_page_{page + 1:03d}.png"
            path.write_bytes(pf.data)
        print(f"[{file_key}] Saved {len(prepared)} debug PNGs to {debug_dir}")

    def _write_json(self, records: list[dict], output_path: Path, file_key: str) -> Path:
        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)

        raw_texts = self._strip_raw_texts(records)
        if raw_texts:
            raw_path = json_path.with_suffix(".llm_raw.txt")
            raw_path.write_text(
                "\n---\n".join(raw_texts),
                encoding="utf-8",
            )
            print(f"[{file_key}] Saved LLM raw response -> {raw_path}")

        json_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[{file_key}] Saved {len(records)} record(s) -> {json_path}")
        return json_path

    def _strip_raw_texts(self, records: list[dict]) -> list[str]:
        raw_texts = []
        for record in records:
            raw = record.pop("_llm_raw_text", None)
            if raw:
                raw_texts.append(raw)
        return raw_texts
