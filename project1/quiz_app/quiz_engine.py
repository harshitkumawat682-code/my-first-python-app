"""Quiz engine: loads questions and drives adaptive difficulty."""

import json
import random
from pathlib import Path
from typing import List

from quiz_app.models import Question, QuizSession

# Default path relative to this file
_DEFAULT_QUESTIONS_PATH = Path(__file__).parent / "data" / "questions.json"

# Thresholds for adaptive difficulty
_HARD_THRESHOLD = 80.0   # % → promote to hard
_MEDIUM_THRESHOLD = 50.0  # % → promote to medium

QUESTIONS_PER_QUIZ = 5


def load_questions(path: Path = _DEFAULT_QUESTIONS_PATH) -> dict[str, List[Question]]:
    """Load questions from a JSON file and return them grouped by difficulty."""
    with open(path, "r", encoding="utf-8") as fh:
        raw: dict = json.load(fh)

    bank: dict[str, List[Question]] = {}
    for difficulty, items in raw.items():
        bank[difficulty] = [
            Question(
                id=item["id"],
                question=item["question"],
                choices=item["choices"],
                answer=item["answer"],
                difficulty=difficulty,
            )
            for item in items
        ]
    return bank


def determine_next_difficulty(percentage: float, current: str) -> str:
    """
    Return the recommended difficulty for the next quiz based on
    the user's last score percentage.
    """
    if percentage >= _HARD_THRESHOLD:
        return "hard"
    if percentage >= _MEDIUM_THRESHOLD:
        return "medium"
    return "easy"


def start_session(
    username: str,
    difficulty: str = "easy",
    path: Path = _DEFAULT_QUESTIONS_PATH,
) -> QuizSession:
    """
    Create and return a new QuizSession for *username* at *difficulty*.

    Questions are randomly sampled from the bank for that difficulty level.
    Falls back to easy if the requested difficulty has no questions.
    """
    bank = load_questions(path)
    pool = bank.get(difficulty, [])
    if not pool:
        pool = bank.get("easy", [])

    count = min(QUESTIONS_PER_QUIZ, len(pool))
    selected = random.sample(pool, count)
    return QuizSession(username=username, difficulty=difficulty, questions=selected)


def validate_username(username: str) -> str:
    """
    Validate *username* and return a cleaned version.

    Raises ValueError with a descriptive message on failure.
    """
    cleaned = username.strip()
    if not cleaned:
        raise ValueError("Username cannot be empty.")
    if len(cleaned) > 30:
        raise ValueError("Username must be 30 characters or fewer.")
    return cleaned
