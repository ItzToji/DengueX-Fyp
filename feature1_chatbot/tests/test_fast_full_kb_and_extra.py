# feature1_chatbot/tests/test_fast_full_kb_and_extra.py
"""
Optimized FAST full-KB tester (fixed unpack bug).
 - Loads model once
 - Precomputes canonical embeddings once
 - Batches bot reply embeddings
 - Vectorized semantic similarity checks
"""

import os, sys, json, csv, argparse
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from feature1_chatbot.chatbot_engine import init_index, load_kb, get_reply
from sentence_transformers import SentenceTransformer

SIM_THRESHOLD = 0.70


def load_all_queries(kb_path):
    queries = []
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            it = json.loads(line)
            kb_id = str(it.get("id"))
            canonical = it.get("canonical_answer", "")
            variants = it.get("question_variants") or [it.get("title", "")]
            for q in variants:
                queries.append((kb_id, q.strip(), canonical))
    return queries


def embed_texts(model, texts, batch=256):
    out = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i+batch]
        e = model.encode(chunk, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        out.append(e)
    if out:
        return np.vstack(out)
    return np.zeros((0, model.get_sentence_embedding_dimension()), dtype="float32")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", required=True)
    parser.add_argument("--index-dir", required=True)
    parser.add_argument("--extra", default=None)
    args = parser.parse_args()

    print("Loading FAISS index…")
    try:
        init_index(args.index_dir)
        print("FAISS index loaded.")
    except Exception as e:
        print("Index missing or failed to load → Using in-memory load():", e)
        load_kb(args.kb)

    print("Reading KB…")
    tests = load_all_queries(args.kb)

    if args.extra and os.path.exists(args.extra):
        with open(args.extra, "r", encoding="utf-8") as f:
            for ln in f:
                q = ln.strip()
                if q:
                    tests.append(("__extra__", q, ""))

    total = len(tests)
    print(f"Loaded {total} variant queries.")
    print("Loading SBERT model (semantic evaluator)…")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Precompute canonical embeddings (one per test entry)
    canonical_list = [c for (_, _, c) in tests]
    print("Embedding canonical answers…")
    canonical_embs = embed_texts(model, canonical_list)

    bot_replies = []
    bot_meta = []   # stores tuples: (index, expected_kb, query_text, canonical, matched_kb, confidence)

    print("Running retrieval (FAISS/in-memory)…")
    for i, (kb_id, q, can) in enumerate(tests):
        r = get_reply(q)
        bot = r.get("reply", "") or ""
        matched_kb = r.get("kb_id")
        conf = r.get("confidence", 0.0)
        # store a 6-tuple so unpacking later is consistent
        bot_replies.append(bot)
        bot_meta.append((i, kb_id, q, can, matched_kb, conf))

    # If there are zero bot replies, avoid embedding
    if len(bot_replies) == 0:
        print("No queries to evaluate.")
        return

    print("Embedding bot replies…")
    bot_embs = embed_texts(model, bot_replies)

    # Compute per-instance similarity between bot reply and corresponding canonical:
    # both arrays are shape (total, D)
    if canonical_embs.shape[0] != bot_embs.shape[0]:
        # Fallback: try to broadcast if canonical was empty strings handled differently
        # We'll compute pairwise dot only for the minimum length
        n = min(canonical_embs.shape[0], bot_embs.shape[0])
        sims = np.sum(bot_embs[:n] * canonical_embs[:n], axis=1)
        # pad sims with zeros for any remainder
        if n < total:
            sims = np.concatenate([sims, np.zeros(total - n, dtype="float32")])
    else:
        sims = np.sum(bot_embs * canonical_embs, axis=1)

    passed = 0
    failed = 0

    fail_csv = os.path.join(os.path.dirname(__file__), "fast_full_failures.csv")
    with open(fail_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["query_idx", "expected_kb", "query", "canonical", "matched_kb",
                         "confidence", "similarity", "status", "bot_reply"])

        print("Evaluating…")
        for idx, sim in enumerate(sims):
            (_, expected_kb, q_text, canonical, matched_kb, conf) = bot_meta[idx]
            bot = bot_replies[idx]
            # PASS if KB ID match or semantic similarity high
            if (matched_kb is not None and str(matched_kb) == str(expected_kb)) or (sim >= SIM_THRESHOLD):
                passed += 1
                continue

            failed += 1
            writer.writerow([idx, expected_kb, q_text, canonical, matched_kb, conf, f"{sim:.3f}", "FAIL", bot[:400]])

    print(f"\n=== SUMMARY ===")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {passed/total*100:.2f}%")
    print("Failures saved to:", fail_csv)


if __name__ == "__main__":
    main()
