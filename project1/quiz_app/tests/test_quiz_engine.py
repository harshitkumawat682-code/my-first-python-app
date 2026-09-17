"""Unit tests for quiz_app.quiz_engine."""

import json
import pytest
from pathlib import Path

from quiz_app.quiz_engine import (
    determine_next_difficulty,
    load_questions,
    start_session,
    validate_username,
    QUESTIONS_PER_QUIZ,
)


# ─── validate_username ───────────────────────────────────────────────────────

def test_validate_username_valid() -> None:
    assert validate_username("Alice") == "Alice"


def test_validate_username_strips_whitespace() -> None:
    assert validate_username("  Bob  ") == "Bob"


def test_validate_username_empty_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        validate_username("")


def test_validate_username_whitespace_only_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        validate_username("   ")


def test_validate_username_too_long_raises() -> None:
    with pytest.raises(ValueError, match="30 characters"):
        validate_username("A" * 31)


def test_validate_username_exactly_30_chars() -> None:
    name = "A" * 30
    assert validate_username(name) == name


# ─── determine_next_difficulty ───────────────────────────────────────────────

def test_next_difficulty_above_hard_threshold() -> None:
    assert determine_next_difficulty(85.0, "easy") == "hard"


def test_next_difficulty_at_hard_threshold() -> None:
    assert determine_next_difficulty(80.0, "easy") == "hard"


def test_next_difficulty_above_medium_threshold() -> None:
    assert determine_next_difficulty(65.0, "easy") == "medium"


def test_next_difficulty_at_medium_threshold() -> None:
    assert determine_next_difficulty(50.0, "easy") == "medium"


def test_next_difficulty_below_medium_threshold() -> None:
    assert determine_next_difficulty(30.0, "medium") == "easy"


def test_next_difficulty_zero_percent() -> None:
    assert determine_next_difficulty(0.0, "hard") == "easy"


# ─── load_questions ──────────────────────────────────────────────────────────

def test_load_questions_returns_all_difficulties(tmp_path: Path) -> None:
    data = {
        "easy": [{"id": "e1", "question": "Q?", "choices": ["A", "B"], "answer": "A"}],
        "medium": [{"id": "m1", "question": "Q?", "choices": ["A", "B"], "answer": "B"}],
    }
    q_file = tmp_path / "questions.json"
    q_file.write_text(json.dumps(data))
    bank = load_questions(q_file)
    assert "easy" in bank
    assert "medium" in bank
    assert bank["easy"][0].answer == "A"
    assert bank["medium"][0].difficulty == "medium"


def test_load_questions_sets_difficulty(tmp_path: Path) -> None:
    data = {
        "hard": [{"id": "h1", "question": "Hard Q?", "choices": ["X", "Y"], "answer": "X"}]
    }
    q_file = tmp_path / "questions.json"
    q_file.write_text(json.dumps(data))
    bank = load_questions(q_file)
    assert bank["hard"][0].difficulty == "hard"


# ─── start_session ───────────────────────────────────────────────────────────

def _write_questions(tmp_path: Path, count: int = 5) -> Path:
    questions = [
        {"id": f"e{i}", "question": f"Q{i}?", "choices": ["A", "B"], "answer": "A"}
        for i in range(count)
    ]
    data = {"easy": questions}
    q_file = tmp_path / "questions.json"
    q_file.write_text(json.dumps(data))
    return q_file


def test_start_session_creates_session(tmp_path: Path) -> None:
    q_file = _write_questions(tmp_path)
    session = start_session("Alice", "easy", q_file)
    assert session.username == "Alice"
    assert session.difficulty == "easy"


def test_start_session_question_count(tmp_path: Path) -> None:
    q_file = _write_questions(tmp_path, count=10)
    session = start_session("Alice", "easy", q_file)
    assert len(session.questions) == QUESTIONS_PER_QUIZ


def test_start_session_fewer_questions_than_limit(tmp_path: Path) -> None:
    q_file = _write_questions(tmp_path, count=3)
    session = start_session("Alice", "easy", q_file)
    assert len(session.questions) == 3


def test_start_session_unknown_difficulty_falls_back(tmp_path: Path) -> None:
    """Unknown difficulty should fall back to 'easy'."""
    q_file = _write_questions(tmp_path)
    session = start_session("Alice", "legendary", q_file)
    assert len(session.questions) > 0
