#!/usr/bin/env python3
# feature1_chatbot/tests/test_1000_random.py
"""
Run N random KB queries against the chatbot and produce summary + failures CSV.

Usage (from project root):
  python feature1_chatbot/tests/test_1000_random.py \
    --kb feature1_chatbot/dengue_kb_seed_15000_extended.jsonl \
    --index-dir feature1_chatbot/index \
    --n 1000 --seed 42 --out feature1_chatbot/tests/failures_1000.csv
"""

import os
import sys
import json
import csv
import time
import random
import argparse
from datetime import datetime

# Ensure project root on sys.path so imports work when running tests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import chatbot engine API (must expose init_index, load_kb, get_reply)
try:
    from feature1_chatbot.chatbot_engine_final import init_index, load_kb, get_reply
except Exception as e:
    # If load_kb isn't present, try to import get_reply only (older code)
    try:
        from feature1_chatbot.chatbot_engine_final import get_reply
        init_index = None
        load_kb = None
    except Exception:
        print("Failed to import chatbot_engine functions. Ensure project root and venv are set up.", e)
        raise

def load_entries(kb_path):
    """Load KB entries (list of dicts) from JSONL file."""
    entries = []
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                it = json.loads(line)
            except Exception:
                continue
            entries.append(it)
    return entries

def choose_query_from_entry(entry):
    """Pick a single query string from a KB entry (first variant or title)."""
    if entry.get("question_variants"):
        return entry["question_variants"][0]
    return entry.get("title","")

def is_correct_reply(expected, reply, prefix_chars=40):
    """Basic heuristic to decide if reply matches expected canonical answer."""
    if not expected:
        return False
    exp = expected.lower().strip()
    rep = (reply or "").lower()
    if len(exp) >= prefix_chars:
        return exp[:prefix_chars] in rep
    words = [w for w in exp.split() if len(w) > 4]
    if not words:
        return exp in rep
    return any(w in rep for w in words[:3])

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kb", required=True, help="Path to KB jsonl file")
    p.add_argument("--index-dir", default="feature1_chatbot/index", help="Index directory (for init_index)")
    p.add_argument("--n", type=int, default=1000, help="Number of random queries to test")
    p.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    p.add_argument("--out", default="feature1_chatbot/tests/failures_1000.csv", help="Failures CSV output")
    p.add_argument("--prefix-chars", type=int, default=40, help="Prefix characters to match when checking correctness")
    args = p.parse_args()

    kb_path = args.kb
    if not os.path.exists(kb_path):
        print("KB file not found:", kb_path)
        sys.exit(2)

    # Try to initialize index (if available)
    try:
        if init_index is not None:
            init_index(args.index_dir)
            print(f"[{datetime.utcnow().isoformat()}] Index initialized from {args.index_dir}")
    except Exception as e:
        print("Warning: init_index failed or index missing. Continuing with in-memory fallback if available.", e)

    print(f"[{datetime.utcnow().isoformat()}] Loading KB entries from: {kb_path}")
    entries = load_entries(kb_path)
    total_entries = len(entries)
    if total_entries == 0:
        print("No entries found in KB.")
        return

    random.seed(args.seed)
    # sample without replacement if possible, otherwise allow repeats
    n = min(args.n, total_entries)
    sampled_indices = random.sample(range(total_entries), n) if n <= total_entries else [random.randrange(total_entries) for _ in range(n)]

    passed = 0
    failed = 0
    failures = []
    start_time = time.time()

    print(f"Running {len(sampled_indices)} random queries (seed={args.seed})...")

    for i, idx in enumerate(sampled_indices, start=1):
        entry = entries[idx]
        query = choose_query_from_entry(entry)
        expected = (entry.get("canonical_answer") or "").strip()
        kb_id = entry.get("id") or entry.get("kb_id") or f"idx_{idx}"

        try:
            result = get_reply(query)
        except Exception as e:
            print(f"Error calling get_reply for idx {idx}: {e}")
            result = {"reply": "", "confidence": 0.0}

        reply = result.get("reply","") if isinstance(result, dict) else str(result)
        confidence = float(result.get("confidence", 0.0)) if isinstance(result, dict) else 0.0

        correct = is_correct_reply(expected, reply, prefix_chars=args.prefix_chars)
        status = "PASS" if correct else "FAIL"

        if correct:
            passed += 1
        else:
            failed += 1
            failures.append({
                "index": idx,
                "kb_id": kb_id,
                "query": query,
                "expected_prefix": (expected[:200] if expected else ""),
                "reply": (reply[:1000] if reply else ""),
                "confidence": confidence
            })

        # progress every 50
        if i % 50 == 0 or i == len(sampled_indices):
            elapsed = time.time() - start_time
            print(f"[{i}/{len(sampled_indices)}] idx={idx} status={status} conf={confidence:.3f} elapsed={int(elapsed)}s")

    total_run = len(sampled_indices)
    accuracy = (passed / total_run * 100) if total_run > 0 else 0.0

    # write failures CSV
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["index","kb_id","query","expected_prefix","reply","confidence"])
        writer.writeheader()
        for r in failures:
            writer.writerow(r)

    print("\n=== RANDOM RUN SUMMARY ===")
    print(f"Total run: {total_run}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Time elapsed: {int(time.time() - start_time)}s")
    print(f"Wrote failures to: {args.out}")

if __name__ == "__main__":
    main()
