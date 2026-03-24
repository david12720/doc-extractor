"""PaytollControl — CLI entry point."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def cmd_run(args: argparse.Namespace) -> None:
    from payroll_control.core.feature_registry import FeatureRegistry
    from payroll_control.core.file_key import build_file_key
    from payroll_control.factories.factory import bootstrap, create_pipeline

    work_dir = args.work_dir.resolve()
    bootstrap(work_dir)

    if args.list_features:
        print("Registered features:", ", ".join(FeatureRegistry.list_features()))
        return

    input_files = [Path(f) for f in args.input_files]
    output_path = Path(args.output) if args.output else None

    file_key = build_file_key(args.feature, input_files)
    output = output_path or (work_dir / "output" / f"{file_key}.json")
    pipeline = create_pipeline(args.feature, work_dir)
    pipeline.run(input_files, output)


def cmd_history(args: argparse.Namespace) -> None:
    from payroll_control.config.settings import COST_LOG_FILE_NAME
    from payroll_control.implementations.csv_cost_logger import CsvCostLogger

    work_dir = args.work_dir.resolve()
    logger = CsvCostLogger(work_dir / COST_LOG_FILE_NAME)
    logger.history(last=args.last)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PaytollControl — extract payroll data from scanned documents and map to Excel.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run a feature pipeline.")
    run_parser.add_argument("feature", help="Feature name to run (e.g., 'attendance').")
    run_parser.add_argument("input_files", nargs="+", type=str, help="Input PDF/PNG file(s).")
    run_parser.add_argument("-o", "--output", type=str, default=None, help="Output Excel path.")
    run_parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory.")
    run_parser.add_argument("--list-features", action="store_true", help="List registered features and exit.")
    run_parser.set_defaults(func=cmd_run)

    # history command
    hist_parser = subparsers.add_parser("history", help="Show API cost history.")
    hist_parser.add_argument("-n", "--last", type=int, default=None, help="Show only last N entries.")
    hist_parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory.")
    hist_parser.set_defaults(func=cmd_history)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
