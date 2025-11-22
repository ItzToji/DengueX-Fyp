#!/usr/bin/env python3
# feature1_chatbot/scripts/apply_review_fixes.py
import os, json, argparse, shutil

def load_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            items.append(json.loads(line))
    return items

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kb", required=True, help="Path to KB jsonl")
    p.add_argument("--patch", required=True, help="Patch JSONL (list of items to replace/add, id field required)")
    p.add_argument("--out", default=None, help="If provided, write patched KB to this file (else overwrite with .patched.jsonl)")
    p.add_argument("--backup", action="store_true", help="Backup original KB")
    args = p.parse_args()

    kb_path = args.kb
    patch_path = args.patch
    out_path = args.out

    if not os.path.exists(kb_path):
        raise FileNotFoundError(kb_path)
    if not os.path.exists(patch_path):
        raise FileNotFoundError(patch_path)

    if args.backup:
        bak = kb_path + ".bak"
        shutil.copy2(kb_path, bak)
        print("Backup saved to:", bak)

    kb_items = load_jsonl(kb_path)
    patch_items = load_jsonl(patch_path)

    # build map by id
    kb_map = { (it.get("id") or it.get("kb_id") or str(idx)): it for idx,it in enumerate(kb_items) }

    replaced = 0
    added = 0
    for p_it in patch_items:
        pid = p_it.get("id") or p_it.get("kb_id")
        if pid is None:
            continue
        pid = str(pid)
        if pid in kb_map:
            # replace in place by id
            # find index
            for i, it in enumerate(kb_items):
                ik = (it.get("id") or it.get("kb_id") or str(i))
                if str(ik) == pid:
                    kb_items[i] = p_it
                    replaced += 1
                    break
        else:
            kb_items.append(p_it)
            added += 1

    print(f"Replaced: {replaced}, Added: {added}")

    if out_path:
        target = out_path
    else:
        target = kb_path.replace(".jsonl", ".patched.jsonl")

    with open(target, "w", encoding="utf-8") as out:
        for it in kb_items:
            out.write(json.dumps(it, ensure_ascii=False) + "\n")
    print("Wrote patched KB ->", target)

if __name__ == "__main__":
    main()
