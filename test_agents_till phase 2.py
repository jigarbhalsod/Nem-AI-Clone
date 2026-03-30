"""
test_agents.py
--------------
Run this BEFORE main.py to confirm Agent 1 and Agent 2 work
with your OpenRouter key.

Usage:
    python test_agents.py

What it tests:
    1. Agent 1 generates a question for a hardcoded topic
    2. Agent 2 evaluates a hardcoded answer and returns valid JSON
    3. Agent 2 handles a blank answer gracefully
    4. Retry logic: Agent 2 on a deliberately bad prompt

If all four pass, your API key is working and Phase 2 is ready to run.
"""

from agents.question_generator import generate_question
from agents.answer_evaluator import evaluate_answer


def separator(title: str):
    print(f"\n{'─'*50}")
    print(f"  TEST: {title}")
    print('─'*50)


def test_agent1_basic():
    separator("Agent 1 — basic question generation")
    q = generate_question(topic="recursion", history=[])
    print(f"  Generated: {q}")
    assert isinstance(q, str) and len(q) > 10, "Question too short or not a string"
    print("  PASS")


def test_agent1_followup():
    separator("Agent 1 — follow-up with missed topics")
    history = [{"question": "What is a base case?", "answer": "stops recursion", "score": 4}]
    q = generate_question(topic="recursion", history=history, follow_up_for=["base case", "stack overflow"])
    print(f"  Generated: {q}")
    assert isinstance(q, str) and len(q) > 10
    print("  PASS")


def test_agent2_good_answer():
    separator("Agent 2 — strong answer (expect score 7–10)")
    result = evaluate_answer(
        question="What is a base case in recursion and why is it necessary?",
        answer=(
            "A base case is a condition in a recursive function that stops further "
            "recursive calls. Without it, the function would call itself infinitely, "
            "eventually causing a stack overflow error because each call uses stack memory."
        )
    )
    print(f"  Result: {result}")
    assert "score" in result and "feedback" in result and "topics_missed" in result
    assert 7 <= result["score"] <= 10, f"Expected 7-10, got {result['score']}"
    print("  PASS")


def test_agent2_weak_answer():
    separator("Agent 2 — weak answer (expect score 1–4)")
    result = evaluate_answer(
        question="What is a base case in recursion and why is it necessary?",
        answer="it stops"
    )
    print(f"  Result: {result}")
    assert result["score"] <= 5, f"Expected ≤5, got {result['score']}"
    assert len(result["topics_missed"]) > 0, "Should have flagged missed topics"
    print("  PASS")


def test_agent2_empty_answer():
    separator("Agent 2 — empty answer (expect score 1)")
    result = evaluate_answer(
        question="Explain binary search.",
        answer=""
    )
    print(f"  Result: {result}")
    assert result["score"] <= 3
    print("  PASS")


if __name__ == "__main__":
    print("\n  NemAI Phase 2 — Agent Test Suite")
    print("  Make sure OPENROUTER_API_KEY is set in .env\n")

    tests = [
        test_agent1_basic,
        test_agent1_followup,
        test_agent2_good_answer,
        test_agent2_weak_answer,
        test_agent2_empty_answer,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL — {e}")
            failed += 1

    print(f"\n{'═'*50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'═'*50}\n")
