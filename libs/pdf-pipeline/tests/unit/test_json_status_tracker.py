from pathlib import Path

from pdf_pipeline.implementations.json_status_tracker import JsonStatusTracker


def test_set_and_get_status(tmp_path: Path):
    tracker = JsonStatusTracker(tmp_path / "status.json")
    tracker.set_status("file1", "prepare", "success")
    assert tracker.get_status("file1", "prepare") == "success"


def test_get_missing_status_returns_none(tmp_path: Path):
    tracker = JsonStatusTracker(tmp_path / "status.json")
    assert tracker.get_status("file1", "extract") is None


def test_is_complete(tmp_path: Path):
    tracker = JsonStatusTracker(tmp_path / "status.json")
    assert not tracker.is_complete("file1")

    for stage in ("prepare", "extract", "cache", "json_output"):
        tracker.set_status("file1", stage, "success")

    assert tracker.is_complete("file1")


def test_persistence(tmp_path: Path):
    path = tmp_path / "status.json"
    tracker1 = JsonStatusTracker(path)
    tracker1.set_status("file1", "prepare", "success")

    tracker2 = JsonStatusTracker(path)
    assert tracker2.get_status("file1", "prepare") == "success"
