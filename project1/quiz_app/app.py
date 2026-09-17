"""Streamlit UI for the AI Gamification and Quiz App."""

import streamlit as st

from quiz_app.models import LeaderboardEntry
from quiz_app.quiz_engine import (
    determine_next_difficulty,
    start_session,
    validate_username,
)
from quiz_app.storage import load_leaderboard, save_score

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(page_title="🎮 Quiz App", page_icon="🧠", layout="centered")


# ─────────────────────────────────────────────
# Session-state helpers
# ─────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "page": "home",          # home | quiz | result | leaderboard
        "username": "",
        "difficulty": "easy",
        "session": None,
        "current_q": 0,
        "error": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ─────────────────────────────────────────────
# Navigation helpers
# ─────────────────────────────────────────────
def _go(page: str) -> None:
    st.session_state["page"] = page


# ─────────────────────────────────────────────
# Page: Home / Username entry
# ─────────────────────────────────────────────
def page_home() -> None:
    st.title("🧠 AI Quiz App")
    st.markdown("Test your knowledge, climb the leaderboard, and level up!")
    st.divider()

    with st.form("start_form"):
        username = st.text_input(
            "Enter your username",
            placeholder="e.g. QuizMaster99",
            max_chars=30,
        )
        difficulty = st.selectbox(
            "Starting difficulty",
            options=["easy", "medium", "hard"],
            index=0,
        )
        submitted = st.form_submit_button("Start Quiz 🚀")

    if submitted:
        try:
            clean_name = validate_username(username)
        except ValueError as exc:
            st.error(str(exc))
            return

        st.session_state["username"] = clean_name
        st.session_state["difficulty"] = difficulty
        st.session_state["session"] = start_session(clean_name, difficulty)
        st.session_state["current_q"] = 0
        st.session_state["error"] = ""
        _go("quiz")
        st.rerun()

    st.divider()
    if st.button("🏆 View Leaderboard"):
        _go("leaderboard")
        st.rerun()


# ─────────────────────────────────────────────
# Page: Quiz
# ─────────────────────────────────────────────
def page_quiz() -> None:
    session = st.session_state["session"]
    current = st.session_state["current_q"]
    total = len(session.questions)

    st.title("🧠 Quiz Time!")
    st.caption(
        f"Player: **{session.username}** | Difficulty: **{session.difficulty.upper()}** | "
        f"Question {current + 1} of {total}"
    )
    st.progress((current) / total)
    st.divider()

    q = session.questions[current]
    st.subheader(f"Q{current + 1}. {q.question}")

    with st.form(f"question_form_{current}"):
        choice = st.radio(
            "Choose your answer:",
            options=q.choices,
            index=None,
            key=f"choice_{current}",
        )
        submitted = st.form_submit_button("Submit Answer ✅")

    if submitted:
        if choice is None:
            st.warning("Please select an answer before submitting.")
            return

        session.record_answer(current, choice)

        if current + 1 < total:
            st.session_state["current_q"] = current + 1
            st.rerun()
        else:
            # Quiz complete
            entry = LeaderboardEntry(
                username=session.username,
                score=session.score(),
                total=total,
                difficulty=session.difficulty,
                percentage=session.percentage(),
            )
            save_score(entry)
            _go("result")
            st.rerun()

    # Quick-exit button
    if st.button("🏠 Back to Home"):
        _go("home")
        st.rerun()


# ─────────────────────────────────────────────
# Page: Result
# ─────────────────────────────────────────────
def page_result() -> None:
    session = st.session_state["session"]
    score = session.score()
    total = len(session.questions)
    pct = session.percentage()
    next_diff = determine_next_difficulty(pct, session.difficulty)

    st.title("🎉 Quiz Complete!")
    st.divider()

    # Score display
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score} / {total}")
    col2.metric("Percentage", f"{pct:.0f}%")
    col3.metric("Difficulty", session.difficulty.upper())

    # Emoji feedback
    if pct == 100:
        st.success("🏆 Perfect score! You're a genius!")
    elif pct >= 80:
        st.success("🌟 Excellent work! Almost perfect!")
    elif pct >= 60:
        st.info("👍 Good job! Keep practising.")
    elif pct >= 40:
        st.warning("🙂 Not bad, but there's room to improve.")
    else:
        st.error("😅 Keep studying — you'll get there!")

    # Adaptive difficulty hint
    st.divider()
    if next_diff != session.difficulty:
        st.info(
            f"🎯 **Adaptive difficulty:** Based on your score, your next quiz will be "
            f"at **{next_diff.upper()}** level!"
        )
    else:
        st.info(f"🎯 Keep going at **{next_diff.upper()}** level!")

    # Answer review
    with st.expander("📋 Review your answers"):
        for i, (q, a) in enumerate(zip(session.questions, session.answers), 1):
            correct = q.is_correct(a) if a else False
            icon = "✅" if correct else "❌"
            st.markdown(f"**Q{i}. {q.question}**")
            st.markdown(f"- Your answer: `{a}` {icon}")
            if not correct:
                st.markdown(f"- Correct answer: `{q.answer}`")

    st.divider()
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("🔄 Play Again (same difficulty)"):
            st.session_state["session"] = start_session(
                session.username, session.difficulty
            )
            st.session_state["current_q"] = 0
            _go("quiz")
            st.rerun()

    with col_b:
        if st.button(f"⬆️ Try {next_diff.upper()}"):
            st.session_state["difficulty"] = next_diff
            st.session_state["session"] = start_session(
                session.username, next_diff
            )
            st.session_state["current_q"] = 0
            _go("quiz")
            st.rerun()

    with col_c:
        if st.button("🏆 Leaderboard"):
            _go("leaderboard")
            st.rerun()


# ─────────────────────────────────────────────
# Page: Leaderboard
# ─────────────────────────────────────────────
def page_leaderboard() -> None:
    st.title("🏆 Leaderboard")
    st.caption("Top scores across all players (best attempt per player shown).")
    st.divider()

    entries = load_leaderboard()

    if not entries:
        st.info("No scores yet. Be the first to play!")
    else:
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for rank, entry in enumerate(entries, 1):
            medal = medals.get(rank, f"#{rank}")
            st.markdown(
                f"{medal} **{entry.username}** — "
                f"`{entry.score}/{entry.total}` ({entry.percentage:.0f}%) "
                f"| Difficulty: *{entry.difficulty}*"
            )
        st.divider()

    if st.button("🏠 Back to Home"):
        _go("home")
        st.rerun()


# ─────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────
PAGE_MAP = {
    "home": page_home,
    "quiz": page_quiz,
    "result": page_result,
    "leaderboard": page_leaderboard,
}

current_page = st.session_state.get("page", "home")
PAGE_MAP.get(current_page, page_home)()
