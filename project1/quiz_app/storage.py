"""Persistence layer: read/write scores to CSV."""

import csv
from pathlib import Path
from typing import List

from quiz_app.models import LeaderboardEntry

_DEFAULT_SCORES_PATH = Path(__file__).parent / "data" / "scores.csv"
_CSV_FIELDS = ["username", "score", "total", "difficulty", "percentage"]


def _ensure_file(path: Path) -> None:
    """Create the CSV file with a header row if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
            writer.writeheader()


def save_score(
    entry: LeaderboardEntry,
    path: Path = _DEFAULT_SCORES_PATH,
) -> None:
    """Append a LeaderboardEntry to the CSV scores file."""
    _ensure_file(path)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writerow(
            {
                "username": entry.username,
                "score": entry.score,
                "total": entry.total,
                "difficulty": entry.difficulty,
                "percentage": f"{entry.percentage:.2f}",
            }
        )


def load_leaderboard(path: Path = _DEFAULT_SCORES_PATH) -> List[LeaderboardEntry]:
    """
    Load all scores from CSV and return the *best* result per username,
    sorted by percentage descending.
    """
    _ensure_file(path)
    best: dict[str, LeaderboardEntry] = {}

    with open(path, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                entry = LeaderboardEntry(
                    username=row["username"],
                    score=int(row["score"]),
                    total=int(row["total"]),
                    difficulty=row["difficulty"],
                    percentage=float(row["percentage"]),
                )
            except (KeyError, ValueError):
                # Skip malformed rows
                continue

            existing = best.get(entry.username)
            if existing is None or entry.percentage > existing.percentage:
                best[entry.username] = entry

    return sorted(best.values(), key=lambda e: e.percentage, reverse=True)
