"""Unit tests for quiz_app.storage."""

import csv
import pytest
from pathlib import Path

from quiz_app.models import LeaderboardEntry
from quiz_app.storage import save_score, load_leaderboard


def make_entry(username: str = "Alice", score: int = 4, total: int = 5,
               difficulty: str = "easy", percentage: float = 80.0) -> LeaderboardEntry:
    return LeaderboardEntry(
        username=username,
        score=score,
        total=total,
        difficulty=difficulty,
        percentage=percentage,
    )


# ─── save_score ──────────────────────────────────────────────────────────────

def test_save_score_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    assert not path.exists()
    save_score(make_entry(), path)
    assert path.exists()


def test_save_score_writes_header(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    save_score(make_entry(), path)
    with open(path) as fh:
        header = fh.readline().strip()
    assert "username" in header
    assert "score" in header
    assert "percentage" in header


def test_save_score_writes_row(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    save_score(make_entry("Bob", 5, 5, "hard", 100.0), path)
    rows = list(csv.DictReader(open(path)))
    assert len(rows) == 1
    assert rows[0]["username"] == "Bob"
    assert rows[0]["score"] == "5"
    assert rows[0]["percentage"] == "100.00"


def test_save_score_appends_multiple(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    save_score(make_entry("Alice", 3, 5), path)
    save_score(make_entry("Bob", 5, 5), path)
    rows = list(csv.DictReader(open(path)))
    assert len(rows) == 2


# ─── load_leaderboard ────────────────────────────────────────────────────────

def test_load_leaderboard_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    result = load_leaderboard(path)
    assert result == []


def test_load_leaderboard_returns_entries(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    save_score(make_entry("Alice", 4, 5, "easy", 80.0), path)
    save_score(make_entry("Bob", 3, 5, "easy", 60.0), path)
    lb = load_leaderboard(path)
    assert len(lb) == 2


def test_load_leaderboard_sorted_desc(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    save_score(make_entry("Alice", 3, 5, "easy", 60.0), path)
    save_score(make_entry("Bob", 5, 5, "hard", 100.0), path)
    lb = load_leaderboard(path)
    assert lb[0].username == "Bob"
    assert lb[1].username == "Alice"


def test_load_leaderboard_best_score_per_user(tmp_path: Path) -> None:
    """Only the highest score for each user should appear."""
    path = tmp_path / "scores.csv"
    save_score(make_entry("Alice", 2, 5, "easy", 40.0), path)
    save_score(make_entry("Alice", 5, 5, "hard", 100.0), path)
    lb = load_leaderboard(path)
    assert len(lb) == 1
    assert lb[0].percentage == 100.0


def test_load_leaderboard_skips_malformed_rows(tmp_path: Path) -> None:
    path = tmp_path / "scores.csv"
    path.write_text("username,score,total,difficulty,percentage\nbadrow,,,\n")
    lb = load_leaderboard(path)
    assert lb == []
