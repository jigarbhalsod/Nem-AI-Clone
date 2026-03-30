"""
session_state.py
----------------
Single source of truth for a viva session.
All agents read from and write to this dict.
Keep it a plain dict for now — easy to serialize to JSON later.
"""


def new_session(topic: str, student_name: str = "Student") -> dict:
    """Create a fresh session state for one viva exam."""
    return {
        "student_name": student_name,
        "topic": topic,
        "turn": 0,                  # current question number
        "history": [],              # list of {question, answer, score, feedback}
        "scores": [],               # just the numeric scores, for quick math
        "flags": [],                # e.g. "3_consecutive_fails", "topic_gap: recursion"
        "status": "active",         # active | ended
    }


def append_turn(state: dict, question: str, answer: str, score: int, feedback: str) -> None:
    """Record one completed Q&A turn into the session."""
    state["history"].append({
        "turn": state["turn"],
        "question": question,
        "answer": answer,
        "score": score,
        "feedback": feedback,
    })
    state["scores"].append(score)
    state["turn"] += 1


def recent_scores(state: dict, n: int = 3) -> list:
    """Return the last n scores. Used by the router to detect consecutive fails."""
    return state["scores"][-n:]


def average_score(state: dict) -> float:
    if not state["scores"]:
        return 0.0
    return round(sum(state["scores"]) / len(state["scores"]), 2)


def end_session(state: dict) -> None:
    state["status"] = "ended"
