# feature1_chatbot/tests/test_100_queries.py
import os, sys, json, random, argparse
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from feature1_chatbot.chatbot_engine import init_index, get_reply, load_kb

def load_kb_queries(kb_path, limit=100):
    qs = []
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            it = json.loads(line)
            q = ""
            if it.get("question_variants"):
                q = it["question_variants"][0]
            else:
                q = it.get("title","")
            qs.append((it.get("id"), q, it.get("canonical_answer","")))
    return qs[:limit]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", default="feature1_chatbot/dengue_kb_seed_15000_extended.jsonl")
    parser.add_argument("--index-dir", default="feature1_chatbot/index")
    parser.add_argument("--n", type=int, default=100)
    args = parser.parse_args()

    print("Init index...")
    init_index(args.index_dir)

    queries = load_kb_queries(args.kb, limit=args.n)
    random.shuffle(queries)
    passed = 0
    failed = 0
    for kb_id, q, expected in queries:
        r = get_reply(q)
        rep = (r.get("reply") or "").lower()
        exp = (expected or "").lower()
        ok = False
        if exp and len(exp) > 20:
            ok = exp[:20] in rep
        else:
            ok = any(w in rep for w in exp.split() if len(w)>4)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(kb_id, status, "conf:", round(r.get("confidence",0),3))
    print("Summary:", passed, "passed;", failed, "failed; accuracy:", passed/(passed+failed)*100 if (passed+failed)>0 else 0)

if __name__ == "__main__":
    main()
