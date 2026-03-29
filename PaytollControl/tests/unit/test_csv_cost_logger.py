import csv
from pathlib import Path

from payroll_control.implementations.csv_cost_logger import CsvCostLogger


def test_log_creates_csv_and_records_cost(tmp_path: Path):
    log_path = tmp_path / "cost.csv"
    logger = CsvCostLogger(log_path)

    logger.log("gemini-2.5-flash", 1000, 500)

    assert log_path.exists()
    with open(log_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["model"] == "gemini-2.5-flash"
    assert float(rows[0]["cost_usd"]) > 0


def test_log_unknown_model_does_not_crash(tmp_path: Path):
    logger = CsvCostLogger(tmp_path / "cost.csv")
    logger.log("unknown-model", 100, 100)
    assert logger._call_count == 0


def test_summary_prints_total(tmp_path: Path, capsys):
    logger = CsvCostLogger(tmp_path / "cost.csv")
    logger.log("gemini-2.5-flash", 1000, 500)
    logger.summary()
    captured = capsys.readouterr()
    assert "session total" in captured.out


def test_tiered_pricing(tmp_path: Path):
    logger = CsvCostLogger(tmp_path / "cost.csv")
    logger.log("gemini-2.5-pro", 100_000, 5000)
    assert logger._call_count == 1
    assert logger._total_usd > 0
