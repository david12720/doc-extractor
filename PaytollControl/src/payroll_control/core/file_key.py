import hashlib
from pathlib import Path


def build_file_key(feature_name: str, input_files: list[Path]) -> str:
    stems = sorted(p.stem for p in input_files)
    if len(stems) == 1:
        return f"{feature_name}_{stems[0]}"
    digest = hashlib.sha256("_".join(stems).encode()).hexdigest()[:10]
    return f"{feature_name}_{digest}"
