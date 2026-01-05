import os, json, argparse, shutil

def load_jsonl(path):
    """Load a JSONL file into a list of dicts."""
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", required=True, help="KB .jsonl file")
    parser.add_argument("--patch", required=True, help="Patch JSONL with updated items (requires id/kb_id)")
    parser.add_argument("--out", default=None, help="Output file (default = kb.patched.jsonl)")
    parser.add_argument("--backup", action="store_true", help="Backup original KB before patching")
    args = parser.parse_args()

    kb_path = args.kb
    patch_path = args.patch
    out_path = args.out

    if not os.path.exists(kb_path):
        raise FileNotFoundError(kb_path)
    if not os.path.exists(patch_path):
        raise FileNotFoundError(patch_path)

    # Optional backup
    if args.backup:
        bak = kb_path + ".bak"
        shutil.copy2(kb_path, bak)
        print("Backup saved ->", bak)

    # Load KB + patch file
    kb_items = load_jsonl(kb_path)
    patch_items = load_jsonl(patch_path)

    # Build map for quick replacement
    kb_map = { str(it.get("id") or it.get("kb_id") or idx): it
               for idx, it in enumerate(kb_items) }

    replaced = 0
    added = 0

    for p_it in patch_items:
        pid = p_it.get("id") or p_it.get("kb_id")
        if pid is None:
            continue

        pid = str(pid)

        if pid in kb_map:
            # Replace item with the same ID
            for i, it in enumerate(kb_items):
                key = str(it.get("id") or it.get("kb_id") or i)
                if key == pid:
                    kb_items[i] = p_it
                    replaced += 1
                    break
        else:
            # Add new KB item
            kb_items.append(p_it)
            added += 1

    print(f"Replaced: {replaced} | Added: {added}")

    # Determine output file
    if out_path:
        target = out_path
    else:
        target = kb_path.replace(".jsonl", ".patched.jsonl")

    # Write final patched KB
    with open(target, "w", encoding="utf-8") as out:
        for it in kb_items:
            out.write(json.dumps(it, ensure_ascii=False) + "\n")

    print("Wrote patched KB ->", target)

if __name__ == "__main__":
    main()
