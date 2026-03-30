"""
utils/router.py
---------------
Score threshold router — the "agentic" decision engine.
Takes the latest score and session state, returns the next action.

Actions:
  "follow_up"  → score < 5, ask a simpler question on the same concept
  "same_topic" → score 5-7, ask another question on the same topic
  "next_topic" → score >= 8, student has demonstrated understanding
  "end"        → 3 consecutive fails OR max turns reached
"""

from session_state import recent_scores

MAX_TURNS = 10
FAIL_THRESHOLD = 5
PASS_THRESHOLD = 8
CONSECUTIVE_FAIL_LIMIT = 3


def route(state: dict, latest_score: int) -> str:
    """Return next action string based on score and session history."""

    # Hard stop: max turns
    if state["turn"] >= MAX_TURNS:
        return "end"

    # Check for 3 consecutive fails
    recents = recent_scores(state, n=CONSECUTIVE_FAIL_LIMIT)
    if len(recents) >= CONSECUTIVE_FAIL_LIMIT and all(s < FAIL_THRESHOLD for s in recents):
        state["flags"].append("3_consecutive_fails")
        return "end"

    # Branch on latest score
    if latest_score < FAIL_THRESHOLD:
        return "follow_up"
    elif latest_score >= PASS_THRESHOLD:
        return "next_topic"
    else:
        return "same_topic"
