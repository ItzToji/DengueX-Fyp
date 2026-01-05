import os, sys, json, argparse, csv, time, math
from datetime import datetime

# Run a full KB regression over chatbot replies with resumable progress and CSV failure logging.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from feature1_chatbot.chatbot_engine_final import init_index, get_reply
except Exception as e:
    print("Failed to import chatbot_engine. Ensure venv is active and project root is on PYTHONPATH.", e)
    raise

def load_kb_entries(kb_path):
    entries = []
    with open(kb_path, 'r', encoding='utf-8') as f:
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
    if entry.get('question_variants'):
        q = entry['question_variants'][0]
    else:
        q = entry.get('title', '')
    return (q or "").strip()

def is_correct_reply(expected, reply, prefix_chars=40):
    if not expected:
        return False
    exp = expected.lower().strip()
    rep = (reply or "").lower()
    if len(exp) >= prefix_chars:
        return exp[:prefix_chars] in rep
    words = [w for w in exp.split() if len(w) > 4]
    return any(w in rep for w in words[:3])

def save_partial_progress(out_jsonl_path, processed_records):
    # Append partial evaluation records as JSONL for resume/debugging.
    with open(out_jsonl_path, 'a', encoding='utf-8') as f:
        for rec in processed_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kb', required=True, help='Path to KB jsonl file')
    parser.add_argument('--index-dir', default='feature1_chatbot/index', help='Index directory (for init_index)')
    parser.add_argument('--out', default='feature1_chatbot/tests/full_failures.csv', help='Failures CSV output')
    parser.add_argument('--resume', default=None, help='Optional JSONL partial progress file to resume into (appended)')
    parser.add_argument('--save-every', type=int, default=200, help='Save partial progress every N items (default 200)')
    parser.add_argument('--start', type=int, default=0, help='Start index (for manual resume)')
    parser.add_argument('--limit', type=int, default=0, help='Limit number to run (0 = run all)')
    parser.add_argument('--prefix-chars', type=int, default=40, help='How many prefix chars to check for correctness')
    args = parser.parse_args()

    kb_path = args.kb
    out_csv = args.out
    resume_jsonl = args.resume
    save_every = max(1, args.save_every)
    start_index = max(0, args.start)
    limit = args.limit

    if not os.path.exists(kb_path):
        print(f"KB file not found: {kb_path}")
        sys.exit(2)

    print(f"[{datetime.utcnow().isoformat()}] Initializing index (this loads model and index)...")
    try:
        init_index(args.index_dir)
    except Exception as e:
        print("Warning: init_index failed or index missing. Continuing if chatbot_engine can still answer via in-memory load.", e)

    print(f"[{datetime.utcnow().isoformat()}] Loading KB entries from: {kb_path}")
    entries = load_kb_entries(kb_path)
    total_entries = len(entries)
    print(f"[{datetime.utcnow().isoformat()}] Total KB entries: {total_entries}")

    if limit > 0:
        total_to_run = min(limit, total_entries - start_index)
    else:
        total_to_run = total_entries - start_index

    print(f"Running from index {start_index} for {total_to_run} items...")

    passed = 0
    failed = 0
    processed = 0
    failures = []
    partial_buffer = []

    if os.path.exists(out_csv):
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        backup = out_csv + f".bak.{timestamp}"
        print(f"Backing up existing failures CSV to: {backup}")
        os.replace(out_csv, backup)

    start_time = time.time()
    for idx in range(start_index, start_index + total_to_run):
        entry = entries[idx]
        q = choose_query_from_entry(entry)
        expected = entry.get('canonical_answer', '').strip()
        kb_id = entry.get('id', f"idx_{idx}")

        processed += 1
        if processed % 50 == 0:
            elapsed = time.time() - start_time
            per_item = elapsed / processed
            remaining = total_to_run - processed
            eta = remaining * per_item
            print(f"[{processed}/{total_to_run}] idx={idx} kb_id={kb_id} elapsed={int(elapsed)}s ETA≈{int(eta)}s")

        try:
            result = get_reply(q)
        except Exception as e:
            result = {"reply": "", "confidence": 0.0}
            print(f"Error calling get_reply at idx {idx}: {e}")

        reply = result.get('reply', '') if isinstance(result, dict) else str(result)
        confidence = float(result.get('confidence', 0.0)) if isinstance(result, dict) else 0.0

        correct = is_correct_reply(expected, reply, prefix_chars=args.prefix_chars)
        status = "PASS" if correct else "FAIL"
        if correct:
            passed += 1
        else:
            failed += 1
            failures.append({
                'index': idx,
                'kb_id': kb_id,
                'query': q,
                'expected_prefix': (expected[:200] if expected else ''),
                'reply': (reply[:1000] if reply else ''),
                'confidence': confidence
            })

        partial_buffer.append({
            'index': idx,
            'kb_id': kb_id,
            'query': q,
            'expected_prefix': (expected[:200] if expected else ''),
            'reply': (reply[:1000] if reply else ''),
            'confidence': confidence,
            'status': status
        })

        if (processed % save_every) == 0:
            if resume_jsonl:
                try:
                    save_partial_progress(resume_jsonl, partial_buffer)
                    print(f"Saved partial progress ({len(partial_buffer)}) to {resume_jsonl}")
                except Exception as e:
                    print("Failed to save partial progress:", e)
            partial_buffer = []

    if partial_buffer and resume_jsonl:
        save_partial_progress(resume_jsonl, partial_buffer)
        print(f"Saved final partial progress ({len(partial_buffer)}) to {resume_jsonl}")

    total_run = processed
    accuracy = (passed/total_run*100) if total_run > 0 else 0.0
    print("\n=== FULL RUN SUMMARY ===")
    print(f"Total run: {total_run}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Time elapsed: {int(time.time() - start_time)}s")

    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'kb_id', 'query', 'expected_prefix', 'reply', 'confidence'])
        writer.writeheader()
        for r in failures:
            writer.writerow(r)
    print(f"Wrote failures to: {out_csv}")

if __name__ == '__main__':
    main()
