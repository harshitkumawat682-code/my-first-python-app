"""Data models for the Quiz App."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    """Represents a single quiz question."""

    id: str
    question: str
    choices: List[str]
    answer: str
    difficulty: str = "easy"

    def is_correct(self, user_answer: str) -> bool:
        """Return True if the user_answer matches the correct answer."""
        return user_answer.strip() == self.answer.strip()


@dataclass
class QuizSession:
    """Holds the state for one quiz attempt by a user."""

    username: str
    difficulty: str
    questions: List[Question]
    answers: List[Optional[str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.answers:
            self.answers = [None] * len(self.questions)

    def record_answer(self, index: int, answer: str) -> None:
        """Record the user's answer for the question at *index*."""
        if 0 <= index < len(self.questions):
            self.answers[index] = answer

    def score(self) -> int:
        """Return the number of correct answers."""
        return sum(
            1
            for q, a in zip(self.questions, self.answers)
            if a is not None and q.is_correct(a)
        )

    def percentage(self) -> float:
        """Return the score as a percentage (0–100)."""
        total = len(self.questions)
        return (self.score() / total * 100) if total > 0 else 0.0

    def is_complete(self) -> bool:
        """Return True when all questions have been answered."""
        return all(a is not None for a in self.answers)


@dataclass
class LeaderboardEntry:
    """One row in the leaderboard."""

    username: str
    score: int
    total: int
    difficulty: str
    percentage: float
