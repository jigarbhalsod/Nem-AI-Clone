"""
agents/question_generator.py
-----------------------------
Agent 1: generates one viva question per call.

Inputs:
  - topic:          the CS concept being examined (e.g. "recursion")
  - history:        list of prior {question, answer, score} turns
  - follow_up_for:  optional list of concepts missed — triggers a targeted follow-up

Output:
  - a single question string
"""

import os
from utils.openrouter_client import chat

# Load system prompt once at import time
_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/question_generator.txt")
with open(_PROMPT_PATH) as f:
    SYSTEM_PROMPT = f.read().strip()


def generate_question(topic: str, history: list[dict], follow_up_for: list[str] = None) -> str:
    """
    Call Agent 1 to produce the next viva question.

    Args:
        topic:         CS topic being examined.
        history:       Full session history — gives the model context of what was already asked.
        follow_up_for: If provided, a list of concepts the student missed. Agent will probe these.

    Returns:
        A question string.
    """
    # Build the user message — tells the agent exactly what it needs to do this turn
    if follow_up_for:
        missed = ", ".join(follow_up_for)
        user_content = (
            f"Topic: {topic}\n"
            f"The student's last answer was weak. Concepts missed: {missed}\n"
            f"Ask a simpler follow-up question targeting these gaps."
        )
    else:
        # Summarise what's been covered so the agent doesn't repeat questions
        covered = [t["question"] for t in history] if history else []
        covered_str = "\n".join(f"- {q}" for q in covered) if covered else "None yet."
        user_content = (
            f"Topic: {topic}\n"
            f"Questions already asked:\n{covered_str}\n"
            f"Ask the next question. Do not repeat any of the above."
        )

    messages = [{"role": "user", "content": user_content}]

    return chat(SYSTEM_PROMPT, messages, temperature=0.8)
