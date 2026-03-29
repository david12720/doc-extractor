"""Verify the library-extractable core never imports from application-level code.

Core pipeline modules (core/, implementations/, abstractions/) must not import
from features/, factories/, or the CLI. This ensures the PDF-to-JSON pipeline
can be extracted as a standalone library without breaking the code.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "payroll_control"

CORE_PACKAGES = ("abstractions", "core", "implementations", "config")
APP_PACKAGES = ("features", "factories")

FORBIDDEN_IMPORTS_FOR_CORE = {
    "features",
    "factories",
}


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


def test_core_does_not_import_features_or_factories():
    """Core pipeline code must never import from features/ or factories/."""
    violations = []
    for pkg in CORE_PACKAGES:
        for py_file in _get_python_files(pkg):
            imports = _collect_imports(py_file)
            for imp in imports:
                for forbidden in FORBIDDEN_IMPORTS_FOR_CORE:
                    if forbidden in imp.split("."):
                        rel = py_file.relative_to(SRC)
                        violations.append(f"{rel} imports '{imp}'")
    assert violations == [], (
        "Core pipeline imports application code:\n" + "\n".join(f"  - {v}" for v in violations)
    )


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


def test_core_does_not_reference_specific_data_schemas():
    """Core pipeline must not import feature-specific data models."""
    violations = []
    for pkg in ("core",):
        for py_file in _get_python_files(pkg):
            imports = _collect_imports(py_file)
            for imp in imports:
                if "model" in imp.split(".") and "features" in imp:
                    rel = py_file.relative_to(SRC)
                    violations.append(f"{rel} imports '{imp}'")
    assert violations == [], (
        "Core imports feature-specific schemas:\n" + "\n".join(f"  - {v}" for v in violations)
    )
