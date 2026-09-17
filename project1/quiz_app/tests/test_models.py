"""Unit tests for quiz_app.models."""

import pytest
from quiz_app.models import Question, QuizSession, LeaderboardEntry


# ─── Question ────────────────────────────────────────────────────────────────

def make_question(answer: str = "Paris") -> Question:
    return Question(
        id="t1",
        question="Capital of France?",
        choices=["Berlin", "Paris", "Rome"],
        answer=answer,
        difficulty="easy",
    )


def test_question_correct_answer() -> None:
    q = make_question("Paris")
    assert q.is_correct("Paris") is True


def test_question_wrong_answer() -> None:
    q = make_question("Paris")
    assert q.is_correct("Berlin") is False


def test_question_strips_whitespace() -> None:
    q = make_question("Paris")
    assert q.is_correct("  Paris  ") is True


# ─── QuizSession ─────────────────────────────────────────────────────────────

def make_session(num_questions: int = 3) -> QuizSession:
    questions = [
        Question(id=f"q{i}", question=f"Q{i}?", choices=["A", "B"], answer="A", difficulty="easy")
        for i in range(num_questions)
    ]
    return QuizSession(username="Alice", difficulty="easy", questions=questions)


def test_session_initial_answers_are_none() -> None:
    session = make_session(3)
    assert session.answers == [None, None, None]


def test_session_record_answer() -> None:
    session = make_session(3)
    session.record_answer(0, "A")
    assert session.answers[0] == "A"


def test_session_score_all_correct() -> None:
    session = make_session(3)
    for i in range(3):
        session.record_answer(i, "A")
    assert session.score() == 3


def test_session_score_none_correct() -> None:
    session = make_session(3)
    for i in range(3):
        session.record_answer(i, "B")
    assert session.score() == 0


def test_session_score_partial() -> None:
    session = make_session(4)
    session.record_answer(0, "A")
    session.record_answer(1, "B")
    session.record_answer(2, "A")
    session.record_answer(3, "B")
    assert session.score() == 2


def test_session_percentage_full() -> None:
    session = make_session(5)
    for i in range(5):
        session.record_answer(i, "A")
    assert session.percentage() == 100.0


def test_session_percentage_zero() -> None:
    session = make_session(5)
    for i in range(5):
        session.record_answer(i, "B")
    assert session.percentage() == 0.0


def test_session_percentage_empty() -> None:
    session = QuizSession(username="Bob", difficulty="easy", questions=[])
    assert session.percentage() == 0.0


def test_session_is_complete_true() -> None:
    session = make_session(2)
    session.record_answer(0, "A")
    session.record_answer(1, "B")
    assert session.is_complete() is True


def test_session_is_complete_false() -> None:
    session = make_session(2)
    session.record_answer(0, "A")
    assert session.is_complete() is False


def test_session_record_answer_out_of_bounds() -> None:
    """Out-of-bounds index should be silently ignored."""
    session = make_session(2)
    session.record_answer(99, "A")   # should not raise
    assert session.answers == [None, None]


# ─── LeaderboardEntry ────────────────────────────────────────────────────────

def test_leaderboard_entry_fields() -> None:
    entry = LeaderboardEntry(
        username="Carol", score=4, total=5, difficulty="medium", percentage=80.0
    )
    assert entry.username == "Carol"
    assert entry.score == 4
    assert entry.percentage == 80.0
