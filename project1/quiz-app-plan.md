# AI Gamification & Quiz App — Plan

## Top-Level Overview

Build a small, beginner-friendly Python + Streamlit web app that lets a named guest player:
1. Enter a username and start a quiz session
2. Answer 5 multiple-choice questions one at a time
3. See a score + full answer review at the end
4. Have the next quiz's difficulty adapted based on their score
5. Have their score saved to a persistent global leaderboard
6. View the top 10 all-time scores

The "AI generation" is simulated by a static bank of categorized questions split across three difficulty levels: Easy, Medium, and Hard.
All state within a session lives in Streamlit's `session_state`. Leaderboard data persists to a local JSON file.

---

## Sub-Tasks

---

### Sub-Task 1 — Define Data Models

**Intent**
Create pure data containers with no logic. Every other module imports from here.
Defining them first prevents circular imports and establishes a shared vocabulary.

**Expected Outcomes**
- `models.py` exists with three dataclasses: `Question`, `QuizSession`, `LeaderboardEntry`
- No business logic lives in this file — only field definitions and types

**Todo List**
- [ ] Create `models.py`
- [ ] Define `Question` dataclass with fields: `id`, `text`, `options`, `correct_index`, `difficulty`, `category`
- [ ] Define `QuizSession` dataclass with fields: `username`, `difficulty`, `questions`, `current_index`, `answers`, `score`
- [ ] Define `LeaderboardEntry` dataclass with fields: `username`, `score`, `difficulty`, `timestamp`

**Relevant Context**
- `options` is a `list[str]` of exactly 4 strings
- `correct_index` is an `int` in range 0–3
- `answers` in `QuizSession` is a `list` of `int | None`, same length as `questions`, initialized to all `None`
- `difficulty` is always one of the string literals: `"easy"`, `"medium"`, `"hard"`
- `timestamp` in `LeaderboardEntry` is an ISO 8601 string (e.g. `"2024-01-15T10:30:00"`)

**Status**: `[ ] pending`

---

### Sub-Task 2 — Build the Question Bank

**Intent**
Populate the static question bank that simulates AI-generated content.
This is the data layer — all quiz content lives here.

**Expected Outcomes**
- `question_bank.py` exists with at least 5 questions per difficulty level (15 total minimum)
- Questions span at least 2 categories (e.g. `"science"`, `"history"`)
- `get_questions_by_difficulty(difficulty, count)` returns a randomly sampled list of `Question` objects
- `get_all_categories()` returns a list of unique category strings
- Raises `InsufficientQuestionsError` if the bank has fewer questions than `count` for that difficulty

**Todo List**
- [ ] Create `question_bank.py`
- [ ] Define a custom exception `InsufficientQuestionsError` (can live here or in a separate `exceptions.py`)
- [ ] Write the static `QUESTION_BANK` list — at least 5 easy, 5 medium, 5 hard questions across 2+ categories
- [ ] Implement `get_questions_by_difficulty(difficulty, count)` using `random.sample`
- [ ] Implement `get_all_categories()` using a set comprehension over the bank

**Relevant Context**
- Import `Question` from `models.py`
- Use `random.sample` (not `random.choice`) to avoid duplicate questions in one quiz
- Guard against `count > len(available)` before calling `random.sample`

**Status**: `[ ] pending`

---

### Sub-Task 3 — Build the Quiz Engine

**Intent**
Encapsulate all quiz lifecycle logic: starting a session, recording answers, scoring, and deciding the next difficulty.
This module has no Streamlit dependency — it is pure Python and testable independently.

**Expected Outcomes**
- `quiz_engine.py` exists with all quiz logic
- `start_session(username, difficulty)` returns a fully initialized `QuizSession`
- `submit_answer(session, answer_index)` records the answer and increments `current_index`
- `calculate_score(session)` returns the total points (10 per correct answer)
- `get_next_difficulty(session)` applies the adaptive rules and returns a difficulty string
- `is_quiz_complete(session)` returns `True` when `current_index == len(questions)`

**Todo List**
- [ ] Create `quiz_engine.py`
- [ ] Implement `start_session(username, difficulty)`:
  - Validate username (non-empty, stripped, max 20 chars, alphanumeric + underscore only)
  - Raise `ValueError` with a clear message if invalid
  - Call `get_questions_by_difficulty` for 5 questions
  - Return a new `QuizSession`
- [ ] Implement `submit_answer(session, answer_index)`:
  - Record `answer_index` in `session.answers[session.current_index]`
  - Increment `session.current_index`
- [ ] Implement `calculate_score(session)`:
  - Compare each answer against `question.correct_index`
  - Return `correct_count * 10`
- [ ] Implement `get_next_difficulty(session)`:
  - Compute percentage: `correct / total * 100`
  - `>= 80%` → move up one level (cap at `"hard"`)
  - `<= 40%` → move down one level (floor at `"easy"`)
  - Otherwise → return current difficulty
- [ ] Implement `is_quiz_complete(session)` as a simple index comparison

**Relevant Context**
- Import `QuizSession`, `Question` from `models.py`
- Import `get_questions_by_difficulty` from `question_bank.py`
- Difficulty order: `["easy", "medium", "hard"]` — use index arithmetic for level changes
- Username validation: use `re.match(r'^[a-zA-Z0-9_]{1,20}$', username.strip())`

**Status**: `[ ] pending`

---

### Sub-Task 4 — Build the Leaderboard Module

**Intent**
Handle all persistence: reading and writing scores to a local JSON file.
Saves every score as a new entry (same username can appear multiple times).

**Expected Outcomes**
- `leaderboard.py` exists with load, save, and query functions
- Scores persist to `leaderboard.json` in the project root
- `save_score(entry)` appends a new entry to the file
- `get_top_scores(n)` returns the top N entries sorted by score descending
- Missing or corrupt file is handled gracefully (returns empty list, does not crash)

**Todo List**
- [ ] Create `leaderboard.py`
- [ ] Define `LEADERBOARD_FILE = "leaderboard.json"` as a module-level constant
- [ ] Implement `load_leaderboard()`:
  - Return `[]` if file does not exist
  - Return `[]` (and print a warning) if JSON is malformed
  - Otherwise deserialize and return `list[LeaderboardEntry]`
- [ ] Implement `save_score(entry: LeaderboardEntry)`:
  - Load current data, append new entry as a dict, write back
- [ ] Implement `get_top_scores(n: int)`:
  - Call `load_leaderboard()`, sort by `score` descending, return first `n`
- [ ] Implement `_write_leaderboard(data: list[dict])` as a private helper that writes JSON

**Relevant Context**
- Import `LeaderboardEntry` from `models.py`
- Use `dataclasses.asdict` to serialize a `LeaderboardEntry` to a plain dict
- Use `json.dumps` with `indent=2` for readable file storage
- `timestamp` should be generated with `datetime.datetime.now().isoformat()` at save time

**Status**: `[ ] pending`

---

### Sub-Task 5 — Build the Streamlit UI

**Intent**
Wire all modules together into a multi-screen Streamlit app using `st.session_state` to track which screen the user is on and the active `QuizSession`.

**Expected Outcomes**
- `app.py` exists and is the single entry point (`streamlit run app.py`)
- Four distinct screens render correctly based on session state: Start, Quiz, Results, Leaderboard
- Quiz shows one question at a time with a radio button for answer selection and a Next button
- Results screen shows score, difficulty feedback, and a full answer review (correct answers highlighted)
- Leaderboard screen shows a table of top 10 scores

**Todo List**
- [ ] Create `app.py`
- [ ] Initialize `st.session_state` keys on first load: `screen`, `quiz_session`, `last_score`, `next_difficulty`
- [ ] Implement `render_start_screen()`:
  - Text input for username
  - "Start Quiz" button that calls `start_session` and transitions to `"quiz"` screen
  - Show validation errors inline using `st.error`
- [ ] Implement `render_question_screen()`:
  - Display question number (e.g. "Question 3 of 5") and progress bar
  - Display question text
  - Radio buttons for the 4 options (no default selection)
  - "Next" button: disabled until an option is selected; calls `submit_answer`; advances screen to `"results"` when quiz is complete
- [ ] Implement `render_results_screen()`:
  - Call `calculate_score` and display the score (e.g. "You scored 30 / 50")
  - Show next difficulty with an explanation (e.g. "Great job! Next quiz will be Medium")
  - Loop through all questions showing: question text, user's answer, correct answer, pass/fail indicator
  - "Save & View Leaderboard" button: calls `save_score`, transitions to `"leaderboard"` screen
  - "Play Again" button: starts a new session at `next_difficulty`, stays on `"quiz"` screen
- [ ] Implement `render_leaderboard_screen()`:
  - Show top 10 entries as a styled `st.dataframe` or `st.table`
  - "Play Again" button: transitions to `"start"` screen
- [ ] Add a top-level router: `if screen == "start": render_start_screen()` etc.

**Relevant Context**
- Import from `quiz_engine`, `leaderboard`, `models`
- Use `st.session_state` exclusively for cross-render state — do not use global variables
- Streamlit re-runs the entire script on every interaction; guard initialization with `if "screen" not in st.session_state`
- Radio button with no default: use `index=None` in `st.radio` (Streamlit >= 1.26)
- Disable a button conditionally: use `st.button("Next", disabled=answer_not_selected)`

**Status**: `[ ] pending`

---

### Sub-Task 6 — Add Project Setup Files

**Intent**
Make the project easy to install and run with a single command.

**Expected Outcomes**
- `requirements.txt` lists `streamlit`
- `README.md` explains setup and how to run the app

**Todo List**
- [ ] Create `requirements.txt` with `streamlit` as the only dependency
- [ ] Create `README.md` with:
  - Project title and one-line description
  - Setup instructions (`pip install -r requirements.txt`)
  - Run instructions (`streamlit run app.py`)
  - Brief description of the 3 difficulty levels and scoring rules

**Status**: `[ ] pending`

---

## File Structure

```
quiz_app/
├── app.py               ← Streamlit entry point + all UI screens
├── quiz_engine.py       ← Session lifecycle, scoring, adaptive difficulty
├── question_bank.py     ← Static question data + filtering + InsufficientQuestionsError
├── leaderboard.py       ← JSON persistence for scores
├── models.py            ← Dataclasses: Question, QuizSession, LeaderboardEntry
├── leaderboard.json     ← Auto-created on first score save (gitignore this)
├── requirements.txt     ← streamlit
└── README.md
```

## Key Business Rules (Reference)

- Difficulty starts at `"easy"` for every new session
- Quiz always contains exactly 5 questions per round
- Scoring: +10 points per correct answer, max 50 points
- Adaptive thresholds: ≥ 80% score → level up; ≤ 40% score → level down
- Difficulty is capped at `"hard"` and floored at `"easy"`
- Every score submission creates a new leaderboard entry
- Leaderboard displays top 10 by score descending

## Validation Rules (Reference)

- Username: non-empty, stripped, max 20 chars, regex `^[a-zA-Z0-9_]{1,20}$`
- Answer selection: user must select before "Next" is enabled
- Question bank: must have ≥ 5 questions per difficulty level
