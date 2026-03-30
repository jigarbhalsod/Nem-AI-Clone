"""
main.py — NemAI Phase 1 Skeleton
---------------------------------
No API calls yet. Fake agents return hardcoded responses.
Goal: verify the loop, state management, and router all work correctly
before touching OpenRouter.

Run: python main.py
"""

import json
import time
from session_state import new_session, append_turn, average_score, end_session
from utils.router import route

# ── Topic bank (expand this later) ──────────────────────────────────────────
TOPICS = [
    "recursion",
    "binary search",
    "time complexity (Big-O)",
    "linked lists",
    "hash maps",
]

# ── Fake agents (Phase 1 stubs — replace with real API calls in Phase 2) ────

def fake_question_generator(topic: str, context: str = "") -> str:
    """
    STUB: Returns a hardcoded question.
    Phase 2: replace with OpenRouter API call using Agent 1 system prompt.
    """
    questions = {
        "recursion":               "Explain what a base case is in recursion and why it's necessary.",
        "binary search":           "What is the time complexity of binary search and why?",
        "time complexity (Big-O)": "What's the difference between O(n) and O(n²) with an example?",
        "linked lists":            "How does inserting a node at the head of a linked list differ from an array?",
        "hash maps":               "What happens when two keys hash to the same index?",
    }
    base = questions.get(topic, f"Explain the concept of {topic}.")
    if context:
        return f"[Follow-up] {base} Be specific about: {context}"
    return base


def fake_answer_evaluator(question: str, answer: str) -> dict:
    """
    STUB: Returns a hardcoded evaluation dict.
    Phase 2: replace with OpenRouter API call using Agent 2 system prompt.
    Output schema must match this exactly — Agent 2 will be prompted to return this JSON.
    """
    # Simulate varying scores based on answer length (just for testing)
    word_count = len(answer.split())
    if word_count < 5:
        score = 3
        feedback = "Answer too brief. Provide a clear explanation with an example."
    elif word_count < 15:
        score = 6
        feedback = "Decent answer. Could elaborate more on edge cases."
    else:
        score = 8
        feedback = "Good explanation. Covers the core concept clearly."

    return {
        "score": score,          # int 1–10
        "feedback": feedback,    # str: specific critique
        "topics_missed": [],     # list[str]: gaps identified
    }


def fake_report_compiler(state: dict) -> dict:
    """
    STUB: Builds a structured report from session state.
    Phase 2: pass state to Agent 3 for a narrative summary.
    """
    return {
        "student": state["student_name"],
        "topic": state["topic"],
        "turns_completed": state["turn"],
        "average_score": average_score(state),
        "flags": state["flags"],
        "history": state["history"],
        "attention_data": None,   # CV pipeline fills this in Phase 5
    }


# ── Display helpers ──────────────────────────────────────────────────────────

def print_separator():
    print("\n" + "─" * 55 + "\n")

def print_score_bar(score: int):
    filled = "█" * score
    empty  = "░" * (10 - score)
    print(f"  Score: [{filled}{empty}] {score}/10")

def print_report(report: dict):
    print_separator()
    print("  SESSION REPORT")
    print(f"  Student : {report['student']}")
    print(f"  Topic   : {report['topic']}")
    print(f"  Turns   : {report['turns_completed']}")
    print(f"  Avg score: {report['average_score']}/10")
    if report["flags"]:
        print(f"  Flags   : {', '.join(report['flags'])}")
    print("\n  Turn-by-turn:")
    for t in report["history"]:
        print(f"\n  Q{t['turn']+1}: {t['question']}")
        print(f"  A : {t['answer']}")
        print_score_bar(t["score"])
        print(f"  Feedback: {t['feedback']}")
    print_separator()


# ── Main viva loop ───────────────────────────────────────────────────────────

def run_viva():
    print("\n" + "═" * 55)
    print("  NemAI — AI Viva Examiner  [Phase 1 / Skeleton]")
    print("═" * 55)

    # Setup
    student_name = input("\n  Student name: ").strip() or "Jigar"
    print("\n  Available topics:")
    for i, t in enumerate(TOPICS, 1):
        print(f"    {i}. {t}")
    choice = input("\n  Choose topic number: ").strip()
    topic_index = int(choice) - 1 if choice.isdigit() else 0
    topic = TOPICS[min(topic_index, len(TOPICS) - 1)]

    state = new_session(topic=topic, student_name=student_name)
    follow_up_context = ""

    print(f"\n  Starting viva on: {topic}")
    print("  (Type your answer and press Enter. Type 'quit' to end.)\n")

    # Viva loop
    while state["status"] == "active":
        print_separator()
        print(f"  Turn {state['turn'] + 1}")

        # Agent 1: generate question
        question = fake_question_generator(topic, context=follow_up_context)
        print(f"\n  Examiner: {question}\n")

        # Student input
        answer = input("  You: ").strip()
        if answer.lower() in ("quit", "exit", "q"):
            print("\n  Session ended by student.")
            break
        if not answer:
            answer = "(no answer given)"

        # Agent 2: evaluate answer
        evaluation = fake_answer_evaluator(question, answer)
        score    = evaluation["score"]
        feedback = evaluation["feedback"]

        print(f"\n  [Evaluating...]")
        time.sleep(0.4)           # simulate API latency — remove in Phase 2
        print_score_bar(score)
        print(f"  Feedback: {feedback}")

        # Update state
        append_turn(state, question, answer, score, feedback)

        # Router: decide next action
        action = route(state, score)

        if action == "end":
            print("\n  [Session complete]")
            end_session(state)

        elif action == "follow_up":
            follow_up_context = evaluation.get("topics_missed", [])
            follow_up_context = ", ".join(follow_up_context) if follow_up_context else topic
            print(f"\n  [Router → follow-up on: {follow_up_context}]")

        elif action == "next_topic":
            follow_up_context = ""
            # Cycle to next topic
            current_index = TOPICS.index(topic)
            next_index = (current_index + 1) % len(TOPICS)
            topic = TOPICS[next_index]
            print(f"\n  [Router → advancing to: {topic}]")

        else:  # same_topic
            follow_up_context = ""
            print(f"\n  [Router → same topic: {topic}]")

    # Agent 3: compile report
    report = fake_report_compiler(state)

    # Save report to JSON
    report_path = f"reports/{state['student_name'].lower()}_session.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print_report(report)
    print(f"  Report saved → {report_path}")


if __name__ == "__main__":
    run_viva()
