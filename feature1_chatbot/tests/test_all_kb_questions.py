"""
Test Script — Runs all 500 KB questions (shuffled) against chatbot
Save as: feature1_chatbot/tests/test_all_kb_questions.py

Run from project root:
    python feature1_chatbot/tests/test_all_kb_questions.py
"""

import os
import json
import random
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import chatbot engine (since feature1_chatbot is at project root)
from feature1_chatbot.chatbot_engine import load_kb, get_reply

# KB path (points to expanded 500-entry file with same name)
KB_PATH = os.path.join(os.path.dirname(__file__), "..", "dengue_kb_seed_500.jsonl")


def load_test_questions():
    questions = []
    with open(KB_PATH, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            # pick the FIRST variant as the test query
            if entry.get("question_variants"):
                questions.append(
                    (entry["id"], entry["question_variants"][0], entry["canonical_answer"])
                )
            else:
                questions.append(
                    (entry["id"], entry.get("title", ""), entry["canonical_answer"])
                )
    return questions


def run_tests():
    print("Loading KB...")
    total = load_kb(KB_PATH)
    print(f"Loaded {total} KB entries (should be 500).")

    print("\nPreparing test questions...")
    questions = load_test_questions()
    random.shuffle(questions)

    passed = 0
    failed = 0

    print("\n=== Running tests on all 500 KB questions ===\n")

    for kb_id, q_text, expected_answer in questions:
        result = get_reply(q_text)

        bot_reply = result["reply"].lower()
        expected = expected_answer.lower()

        # Simple correctness check: check if canonical answer's first 20 chars appear in reply
        is_correct = expected[:20] in bot_reply

        status = "PASS" if is_correct else "FAIL"

        print(f"ID: {kb_id}")
        print(f"Q: {q_text}")
        print(f"Bot Confidence: {result['confidence']:.3f}")
        print(f"Urgency: {result['urgency']}")
        print(f"Status: {status}")
        print("-" * 60)

        if is_correct:
            passed += 1
        else:
            failed += 1

    print("\n=== Test Summary ===")
    print(f"Total: {len(questions)} (expected 500)")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {passed / len(questions) * 100:.2f}%")

if __name__ == "__main__":
    run_tests()
