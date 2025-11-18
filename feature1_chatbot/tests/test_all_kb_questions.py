# feature1_chatbot/tests/test_all_kb_questions.py
"""
Test script — runs all KB entries (shuffled) and reports PASS/FAIL.

Usage (from project root, with venv active):
    python feature1_chatbot/tests/test_all_kb_questions.py
"""

import os
import json
import random
import sys

# Ensure project root on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from feature1_chatbot.chatbot_engine import load_kb, get_reply

# Semantic model for evaluating reply vs canonical answer
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except Exception:
    SentenceTransformer = None
    np = None

# Point to your KB file (change if you use a different filename)
KB_FILENAME = "dengue_kb_seed_1500.jsonl"
KB_PATH = os.path.join(os.path.dirname(__file__), "..", KB_FILENAME)

# Evaluation thresholds (tune if needed)
SEMANTIC_SIM_THRESHOLD = 0.70  # similarity between canonical answer and bot reply
KEYWORD_OVERLAP_REQUIRED = 1   # number of significant words overlap to accept as pass

# instantiate model lazily
EVAL_MODEL = None
def get_eval_model():
    global EVAL_MODEL
    if EVAL_MODEL is None:
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers not installed in this environment.")
        EVAL_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return EVAL_MODEL

def embed_text(text):
    """Return a normalized numpy embedding for the given text."""
    model = get_eval_model()
    emb = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return emb[0]

def load_test_questions():
    questions = []
    with open(KB_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line.strip())
            q = None
            if entry.get("question_variants"):
                q = entry["question_variants"][0]
            else:
                q = entry.get("title", "")
            questions.append((entry.get("id"), q, entry.get("canonical_answer","")))
    return questions

def significant_words(text, min_len=4):
    words = []
    for w in (text or "").lower().split():
        w_clean = "".join([c for c in w if c.isalnum()])
        if len(w_clean) >= min_len:
            words.append(w_clean)
    return words

def run_tests():
    print("Loading KB...")
    total = load_kb(KB_PATH)
    print(f"Loaded {total} KB entries")

    print("\nPreparing test questions...")
    questions = load_test_questions()
    random.shuffle(questions)

    passed = 0
    failed = 0

    # pre-warm model (optional) to make the first call faster
    try:
        get_eval_model()
    except Exception as e:
        print("Warning: failed to load evaluation model:", e)
        print("Semantic checks will not run. Install sentence-transformers to enable them.")
        # proceed; fallback will only use kb_id match and keyword overlap

    print("\n=== Running tests on KB questions ===\n")

    for kb_id, q_text, expected_answer in questions:
        result = get_reply(q_text)

        bot_reply = (result.get("reply") or "").strip()
        bot_reply_l = bot_reply.lower()
        expected = (expected_answer or "").strip()
        expected_l = expected.lower()

        is_correct = False
        reason = ""

        # 1) If the engine itself matched the same KB id -> PASS
        matched_kb = result.get("kb_id")
        if matched_kb and str(matched_kb) == str(kb_id):
            is_correct = True
            reason = "matched_kb_id"

        # 2) Semantic similarity between canonical answer and bot reply
        if not is_correct and SentenceTransformer is not None and bot_reply:
            try:
                a_emb = embed_text(expected)
                b_emb = embed_text(bot_reply)
                sim = float(np.dot(a_emb, b_emb))
            except Exception as e:
                sim = 0.0
            if sim >= SEMANTIC_SIM_THRESHOLD:
                is_correct = True
                reason = f"semantic_sim:{sim:.3f}"

        # 3) Keyword overlap fallback (simple)
        if not is_correct:
            sig = significant_words(expected, min_len=4)
            overlap = 0
            for w in sig[:5]:  # check up to first 5 significant words
                if w in bot_reply_l:
                    overlap += 1
            if overlap >= KEYWORD_OVERLAP_REQUIRED and len(sig) > 0:
                is_correct = True
                reason = f"keyword_overlap:{overlap}"

        status = "PASS" if is_correct else "FAIL"

        # Print detailed info for debugging
        sim_display = ""
        try:
            sim_display = f"{sim:.3f}" if 'sim' in locals() else ""
        except Exception:
            sim_display = ""
        print(f"ID: {kb_id}")
        print(f"Q: {q_text}")
        print(f"Matched KB ID: {matched_kb}  |  SemanticSim: {sim_display}")
        print(f"Bot Confidence: {result.get('confidence',0):.3f}")
        print(f"Urgency: {result.get('urgency')}")
        print(f"Status: {status}  ({reason})")
        print("-" * 60)

        if is_correct:
            passed += 1
        else:
            failed += 1

    print("\n=== Test Summary ===")
    total_q = len(questions)
    print(f"Total: {total_q}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {passed / total_q * 100:.2f}%")

if __name__ == "__main__":
    run_tests()
