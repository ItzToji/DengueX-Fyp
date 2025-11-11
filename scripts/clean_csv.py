import sys, re, csv, pathlib

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
log = dst.with_suffix(".log")

EXPECTED = 8
HEADER = ["id","question_en","question_ru","answer_en","answer_ru","tags","sources","safety_level"]

def is_header(line):
    s = line.strip().lower()
    return s.replace(" ", "") == ",".join(HEADER).replace(" ", "")

def fix_records(lines):
    buf = []
    recs = []
    for raw in lines:
        if not raw.strip():
            continue
        # drop stray repeated headers
        if is_header(raw):
            continue
        buf.append(raw.rstrip("\n"))
        # balance quotes: join next line(s) until quotes (not escaped) are even
        joined = "\n".join(buf)
        # count unescaped "
        q = len(re.findall(r'(?<!\\)"', joined))
        if q % 2 == 0:
            recs.append(joined)
            buf = []
    if buf:  # leftover (unbalanced) -> log it
        recs.append("\n".join(buf))
    return recs

with src.open(encoding="utf-8", errors="replace") as f:
    raw_lines = f.read().splitlines()

records = fix_records(raw_lines)

bad = []
rows = []
# Use csv.reader to respect quotes/commas-in-quotes
for i, rec in enumerate(records, start=1):
    try:
        for row in csv.reader([rec], quotechar='"', escapechar='\\', skipinitialspace=True):
            if len(row) != EXPECTED:
                bad.append((i, len(row), rec))
                # try last-ditch: collapse extras at the end into last column
                if len(row) > EXPECTED:
                    merged = row[:EXPECTED-1] + [",".join(row[EXPECTED-1:])]
                    row = merged
                elif len(row) < EXPECTED:
                    # pad short rows
                    row = row + [""]*(EXPECTED-len(row))
            rows.append(row)
    except Exception as e:
        bad.append((i, -1, rec))

# enforce header
if rows and [c.strip().lower() for c in rows[0]] != HEADER:
    rows.insert(0, HEADER)

# remove any accidental header duplicates within body
clean_rows = [rows[0]]
for r in rows[1:]:
    if [c.strip().lower() for c in r] == HEADER:
        continue
    clean_rows.append(r)

# normalize, drop duplicates by id (keep first)
out = []
seen = set()
for r in clean_rows[1:]:
    # coerce id
    try:
        rid = int(str(r[0]).strip())
    except:
        # skip rows with non-numeric id
        bad.append(("nonint_id", r[0], ",".join(r)))
        continue
    if rid in seen:
        bad.append(("dup_id_drop", rid, r[1]))
        continue
    seen.add(rid)
    # normalize tags/safety
    tags = (r[5] or "").strip()
    safety = (r[7] or "").strip().lower()
    if safety not in {"general","urgent-care","emergency"}:
        safety = "general"
    out.append([rid, r[1].strip(), r[2].strip(), r[3].strip(), r[4].strip(), tags, (r[6] or "").strip(), safety])

# write cleaned csv
dst.parent.mkdir(parents=True, exist_ok=True)
with dst.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(HEADER)
    w.writerows(out)

# write log
with log.open("w", encoding="utf-8") as f:
    for item in bad:
        f.write(f"{item}\n")

print(f"✅ CLEAN FILE SAVED -> {dst}")
print(f"ℹ️  Log -> {log}  (bad/adjusted rows listed here)")
print(f"Rows kept: {len(out)}  | Unique IDs: {len(set(r[0] for r in out))}")
