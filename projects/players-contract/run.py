"""Players Contract — CLI entry point."""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent / "src"))


def _resolve_path(path: Path) -> Path:
    if path.exists():
        return path
    parent = path.parent
    if not parent.exists():
        return path
    target = Counter(path.name)
    matches = [c for c in parent.iterdir() if c.is_file() and Counter(c.name) == target]
    if len(matches) == 1:
        print(f"[path] RTL-reordered filename recovered: {path.name!r} -> {matches[0].name!r}")
        return matches[0]
    return path


def cmd_run(args: argparse.Namespace) -> None:
    import json

    from pdf_pipeline.core.feature_registry import FeatureRegistry
    from pdf_pipeline.core.file_key import build_file_key
    from players_contract.factories.factory import bootstrap, create_excel_mapper, create_pipeline

    work_dir = args.work_dir.resolve()
    bootstrap(work_dir, enable_ocr=args.ocr)

    if args.list_features:
        print("Registered features:", ", ".join(FeatureRegistry.list_features()))
        return

    if args.base_dir is not None and args.input_files:
        raise SystemExit("Pass either --base-dir or input_files, not both.")
    if args.base_dir is None and not args.input_files:
        raise SystemExit("Must pass either --base-dir or one or more input files.")

    pipeline = create_pipeline(args.feature, work_dir)
    mapper = create_excel_mapper(args.feature)

    if args.base_dir is not None:
        _run_base_dir(args, pipeline, mapper, work_dir)
        return

    input_files = [_resolve_path(p) for p in args.input_files]
    file_key = build_file_key(args.feature, input_files)
    output = args.output or (work_dir / "output" / f"{file_key}.json")
    json_path = pipeline.run(input_files, output)

    records = json.loads(json_path.read_text(encoding="utf-8"))
    xlsx_path = mapper.write(records, json_path.with_suffix(".xlsx"))
    print(f"[{args.feature}] Saved Excel -> {xlsx_path}")


def _run_base_dir(args: argparse.Namespace, pipeline, mapper, work_dir: Path) -> None:
    import json

    base_dir = args.base_dir.resolve()
    if not base_dir.is_dir():
        raise SystemExit(f"--base-dir is not a directory: {base_dir}")

    pdf_files = sorted(
        p for p in base_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".pdf"
    )
    if not pdf_files:
        raise SystemExit(f"No PDF files found in {base_dir}")

    print(f"[{args.feature}] Found {len(pdf_files)} PDF file(s) in {base_dir}")

    per_file_dir = work_dir / "output" / "_per_file"
    aggregated: list[dict] = []
    failed: list[tuple[Path, str]] = []

    for pdf in pdf_files:
        print(f"[{args.feature}] --- Processing {pdf.name} ---")
        try:
            per_file_json = pipeline.run([pdf], per_file_dir / f"{pdf.stem}.json")
            records = json.loads(per_file_json.read_text(encoding="utf-8"))
            aggregated.extend(records)
        except Exception as e:
            print(f"[{args.feature}] FAILED on {pdf.name}: {e}")
            failed.append((pdf, str(e)))

    if args.output is not None:
        combined_json = args.output.with_suffix(".json")
    else:
        combined_json = base_dir / f"{base_dir.name}.json"
    combined_json.parent.mkdir(parents=True, exist_ok=True)
    combined_json.write_text(
        json.dumps(aggregated, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[{args.feature}] Saved combined JSON ({len(aggregated)} record(s)) -> {combined_json}")

    xlsx_path = mapper.write(aggregated, combined_json.with_suffix(".xlsx"))
    print(f"[{args.feature}] Saved combined Excel -> {xlsx_path}")

    if failed:
        print(f"[{args.feature}] {len(failed)} file(s) failed:")
        for pdf, err in failed:
            print(f"  - {pdf.name}: {err}")


def cmd_history(args: argparse.Namespace) -> None:
    from pdf_pipeline.config.settings import COST_LOG_FILE_NAME
    from pdf_pipeline.implementations.csv_cost_logger import CsvCostLogger

    work_dir = args.work_dir.resolve()
    logger = CsvCostLogger(work_dir / COST_LOG_FILE_NAME)
    logger.history(last=args.last)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Players Contract — extract salary data from IFA player contracts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a feature pipeline.")
    run_parser.add_argument("feature", help="Feature name (e.g., 'contract_salary').")
    run_parser.add_argument("input_files", nargs="*", type=Path, default=[], help="Input PDF file(s).")
    run_parser.add_argument("-b", "--base-dir", type=Path, default=None, help="Directory of PDFs to process individually (top-level only).")
    run_parser.add_argument("-o", "--output", type=Path, default=None, help="Output JSON path.")
    run_parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory.")
    run_parser.add_argument("--ocr", action="store_true", default=False, help="Enable Cloud Vision OCR for handwriting.")
    run_parser.add_argument("--list-features", action="store_true", help="List registered features and exit.")
    run_parser.set_defaults(func=cmd_run)

    hist_parser = subparsers.add_parser("history", help="Show API cost history.")
    hist_parser.add_argument("-n", "--last", type=int, default=None, help="Show only last N entries.")
    hist_parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory.")
    hist_parser.set_defaults(func=cmd_history)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
