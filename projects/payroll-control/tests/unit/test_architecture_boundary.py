"""Verify architectural boundaries between payroll-control and pdf-pipeline.

Feature code must depend on pdf_pipeline abstractions only, never on
pdf_pipeline.implementations directly. Only factories/ may import implementations.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "payroll_control"


def _collect_imports(file_path: Path) -> list[str]:
    """Return all import module strings from a Python file."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _get_python_files(package: str) -> list[Path]:
    pkg_dir = SRC / package
    if not pkg_dir.exists():
        return []
    return list(pkg_dir.rglob("*.py"))


def test_features_do_not_import_implementations():
    """Feature code must depend on abstractions only, not concrete implementations."""
    violations = []
    for py_file in _get_python_files("features"):
        imports = _collect_imports(py_file)
        for imp in imports:
            if "implementations" in imp.split("."):
                rel = py_file.relative_to(SRC)
                violations.append(f"{rel} imports '{imp}'")
    assert violations == [], (
        "Features import implementations directly:\n" + "\n".join(f"  - {v}" for v in violations)
    )


def test_features_do_not_import_core_pipeline():
    """Feature code must not import pipeline orchestration classes."""
    violations = []
    for py_file in _get_python_files("features"):
        imports = _collect_imports(py_file)
        for imp in imports:
            parts = imp.split(".")
            if "pdf_pipeline" in parts and "core" in parts and "pipeline" in parts:
                rel = py_file.relative_to(SRC)
                violations.append(f"{rel} imports '{imp}'")
    assert violations == [], (
        "Features import pipeline orchestration:\n" + "\n".join(f"  - {v}" for v in violations)
    )
