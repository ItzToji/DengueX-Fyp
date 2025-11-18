# feature1_chatbot/tests/test_full_kb_and_extra.py
"""
Run exhaustive tests:
 - all KB items, using ALL question_variants for each item
 - optional extra file of unique queries (one per line)
Outputs:
 - prints summary
 - creates failures CSV: feature1_chatbot/tests/full_test_failures.csv

Usage:
  (1) Build index first:
     python feature1_chatbot/scripts/build_embeddings_variants.py --kb feature1_chatbot/dengue_kb_seed_1500.jsonl --index-dir feature1_chatbot/index

  (2) Run:
     python feature1_chatbot/tests/test_full_kb_and_extra.py --kb feature1_chatbot/dengue_kb_seed_1500.jsonl --index-dir feature1_chatbot/index --extra extra_queries.txt
"""
import os, sys, json, csv, random, argparse
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from feature1_chatbot.chatbot_engine import init_index, load_kb, get_reply, EMBEDDINGS, META
# Note: get_reply returns canonical answer and kb_id when index initialized.

# semantic model for evaluation (fallback if needed)
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except Exception:
    SentenceTransformer = None
    np = None

# thresholds
SEMANTIC_SIM_THRESHOLD = 0.70
KEYWORD_OVERLAP_REQUIRED = 1

def get_eval_model():
    if SentenceTransformer is None:
        return None
    return SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(model, text):
    emb = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return emb[0]

def load_all_variant_questions(kb_path):
    pairs = []  # list of (kb_id, variant_text, canonical_answer)
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            it = json.loads(line.strip())
            kb_id = str(it.get("id") or it.get("kb_id") or it.get("uid"))
            canonical = it.get("canonical_answer","")
            variants = it.get("question_variants") or []
            if not variants:
                # fallback use title
                variants = [it.get("title","")]
            for v in variants:
                if v and v.strip():
                    pairs.append((kb_id, v.strip(), canonical))
    return pairs

def significant_words(text, min_len=4):
    words = []
    for w in (text or "").lower().split():
        w_clean = "".join([c for c in w if c.isalnum()])
        if len(w_clean) >= min_len:
            words.append(w_clean)
    return words

def evaluate_one(model, kb_id_expected, query, canonical_expected, result):
    """
    Returns (is_correct:bool, reason:str, sim:float)
    """
    bot_reply = (result.get("reply") or "").strip()
    matched_kb = result.get("kb_id")
    # 1) kb_id match
    if matched_kb is not None and str(matched_kb) == str(kb_id_expected):
        return True, "matched_kb_id", 1.0
    # 2) semantic similarity between canonical and bot reply
    sim = 0.0
    if model is not None and bot_reply:
        try:
            a_emb = embed_text(model, canonical_expected)
            b_emb = embed_text(model, bot_reply)
            sim = float(np.dot(a_emb, b_emb))
        except Exception:
            sim = 0.0
    if sim >= SEMANTIC_SIM_THRESHOLD:
        return True, f"semantic_sim:{sim:.3f}", sim
    # 3) keyword overlap fallback
    sig = significant_words(canonical_expected, min_len=4)
    overlap = 0
    br = bot_reply.lower()
    for w in sig[:8]:
        if w in br:
            overlap += 1
    if overlap >= KEYWORD_OVERLAP_REQUIRED and len(sig)>0:
        return True, f"keyword_overlap:{overlap}", sim
    return False, f"fail(sim={sim:.3f}, overlap={overlap})", sim

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", default="feature1_chatbot/dengue_kb_seed_1500.jsonl")
    parser.add_argument("--index-dir", default="feature1_chatbot/index")
    parser.add_argument("--extra", default=None, help="Optional file with extra queries, one per line")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle test order")
    args = parser.parse_args()

    kb_path = args.kb
    index_dir = args.index_dir
    extra_file = args.extra

    # init index (preferred) - will raise if missing files
    try:
        init_index(index_dir)
        index_loaded = True
        print("Index loaded from", index_dir)
    except Exception as e:
        print("Index init failed or missing; falling back to load_kb() in-memory:", e)
        load_kb(kb_path)
        index_loaded = False

    # load all variant questions
    pairs = load_all_variant_questions(kb_path)
    print(f"Loaded {len(pairs)} query variants from KB")

    extra_queries = []
    if extra_file and os.path.exists(extra_file):
        with open(extra_file, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t:
                    extra_queries.append(("__extra__", t, ""))  # no canonical
        print(f"Loaded {len(extra_queries)} extra queries")

    # combine
    all_tests = pairs + extra_queries
    if args.shuffle:
        random.shuffle(all_tests)

    # evaluation model
    eval_model = None
    if SentenceTransformer is not None:
        print("Loading evaluation model (for semantic matching)...")
        eval_model = get_eval_model()

    # run tests
    total = len(all_tests)
    passed = 0
    failed = 0
    failures_csv = os.path.join(os.path.dirname(__file__), "full_test_failures.csv")
    with open(failures_csv, "w", encoding="utf-8", newline="") as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(["kb_id_expected","query","canonical_expected","matched_kb","bot_reply","reason","sim","confidence"])
        for kb_id, qtext, canonical in all_tests:
            res = get_reply(qtext)
            is_correct, reason, sim = evaluate_one(eval_model, kb_id, qtext, canonical, res)
            if is_correct:
                passed += 1
            else:
                failed += 1
                writer.writerow([kb_id, qtext, canonical, res.get("kb_id"), (res.get("reply") or "")[:500], reason, f"{sim:.3f}", res.get("confidence")])
    print("Done. Failures written to", failures_csv)
    print("Summary:")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {passed/total*100:.2f}%")

if __name__ == "__main__":
    main()
