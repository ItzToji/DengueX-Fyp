# feature1_chatbot/tests/diagnose_failures.py
import os, sys, json, csv, random
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from feature1_chatbot.chatbot_engine import load_kb, get_reply, _embed_text, EMBEDDINGS, META  # load_kb must exist
from feature1_chatbot.chatbot_engine import SIMILARITY_THRESHOLD, TOP_K

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "dengue_kb_seed_1500.jsonl")

def load_questions():
    qs = []
    with open(KB_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            e = json.loads(line.strip())
            q = (e.get("id"), e.get("question_variants", [e.get("title","")])[0], e.get("canonical_answer",""))
            qs.append(q)
    return qs

def main():
    print("Loading KB:", KB_PATH)
    total = load_kb(KB_PATH)
    print("Loaded:", total)
    questions = load_questions()
    random.shuffle(questions)

    out_csv = os.path.join(os.path.dirname(__file__), "diagnose_failures.csv")
    headers = [
        "kb_id","query","expected_canonical","is_pass","bot_reply","confidence",
        "matched_kb_id","matched_title","top1_score",
        "top2_kb_id","top2_score","top3_kb_id","top3_score"
    ]

    with open(out_csv, "w", encoding="utf-8", newline="") as outf:
        writer = csv.writer(outf)
        writer.writerow(headers)

        pass_count = 0
        fail_count = 0

        for kb_id, q_text, expected in questions:
            res = get_reply(q_text)
            bot_reply = (res.get("reply") or "").lower()
            expected_l = (expected or "").lower()

            # same heuristic as your test (first 20 chars)
            is_correct = False
            if expected_l and len(expected_l) >= 20:
                is_correct = expected_l[:20] in bot_reply
            else:
                exp_words = [w for w in expected_l.split() if len(w) > 3]
                if exp_words:
                    is_correct = any(w in bot_reply for w in exp_words[:3])

            # collect top3 candidates + scores if possible
            # We try to obtain top-3 from META+EMBEDDINGS if available; otherwise we will set blanks.
            top1_id = top1_score = top2_id = top2_score = top3_id = top3_score = ""
            # If engine exposes META and EMBEDDINGS, compute top candidates by cosine
            try:
                if EMBEDDINGS is not None and EMBEDDINGS.shape[0] > 0:
                    qemb = _embed_text(q_text)
                    sims = (EMBEDDINGS @ qemb).tolist()  # dot product since normalized
                    # descending sort
                    idxs = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:3]
                    def get_meta(i):
                        m = META[i]
                        return m.get("id"), float(sims[i]), m.get("title","")
                    if len(idxs) > 0:
                        top1_id, top1_score, top1_title = get_meta(idxs[0])
                    if len(idxs) > 1:
                        top2_id, top2_score, _ = get_meta(idxs[1])
                    if len(idxs) > 2:
                        top3_id, top3_score, _ = get_meta(idxs[2])
            except Exception:
                pass

            writer.writerow([
                kb_id, q_text, expected, "PASS" if is_correct else "FAIL",
                res.get("reply",""), res.get("confidence", ""),
                top1_id, top1_score,
                top2_id, top2_score,
                top3_id, top3_score
            ])

            if is_correct:
                pass_count += 1
            else:
                fail_count += 1

    print("Done. Written:", out_csv)
    print("Pass:", pass_count, "Fail:", fail_count, "Total:", pass_count+fail_count)
    print("Open the CSV and inspect top failures (sorted by confidence or frequent failed kb_id).")

if __name__ == "__main__":
    main()
