"""
agents/answer_evaluator.py
--------------------------
Agent 2: evaluates a student's answer and returns a structured score.

Inputs:
  - question: the question that was asked
  - answer:   the student's response

Output dict (guaranteed schema):
  {
    "score":         int (1-10),
    "feedback":      str,
    "topics_missed": list[str]
  }

This agent uses chat_json() — it forces JSON output and parses it.
If the model returns malformed JSON, we retry once before failing.
"""

import os
from utils.openrouter_client import chat_json

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/answer_evaluator.txt")
with open(_PROMPT_PATH) as f:
    SYSTEM_PROMPT = f.read().strip()

# Fallback evaluation when the model fails to return valid JSON
_FALLBACK = {
    "score": 1,
    "feedback": "Evaluation failed — could not parse model response. Treating as unanswered.",
    "topics_missed": [],
}


def evaluate_answer(question: str, answer: str) -> dict:
    """
    Call Agent 2 to score a student's answer.

    Args:
        question: The viva question that was posed.
        answer:   The student's typed response.

    Returns:
        Dict with keys: score (int), feedback (str), topics_missed (list[str])
    """
    user_content = f"Question: {question}\n\nStudent's answer: {answer}"
    messages = [{"role": "user", "content": user_content}]

    # First attempt
    try:
        result = chat_json(SYSTEM_PROMPT, messages, temperature=0.2)
        return _validate(result)
    except ValueError:
        pass

    # Retry once with an explicit reminder to return only JSON
    try:
        reminder = (
            "IMPORTANT: Your previous response was not valid JSON. "
            "Respond with ONLY a JSON object — no text, no fences, no explanation."
        )
        messages.append({"role": "user", "content": reminder})
        result = chat_json(SYSTEM_PROMPT, messages, temperature=0.0)
        return _validate(result)
    except ValueError:
        return _FALLBACK


def _validate(data: dict) -> dict:
    """
    Ensure the returned dict has the expected keys and types.
    Coerces types where possible; raises ValueError if critically malformed.
    """
    if not isinstance(data, dict):
        raise ValueError("Response is not a dict")

    score = data.get("score", 1)
    if not isinstance(score, int):
        try:
            score = int(score)
        except (TypeError, ValueError):
            score = 1
    score = max(1, min(10, score))   # clamp to 1–10

    feedback = str(data.get("feedback", "No feedback provided."))

    topics_missed = data.get("topics_missed", [])
    if not isinstance(topics_missed, list):
        topics_missed = []

    return {
        "score": score,
        "feedback": feedback,
        "topics_missed": topics_missed,
    }
