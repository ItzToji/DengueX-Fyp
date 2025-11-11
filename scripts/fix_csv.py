import sys, os, re

src = "data/raw/Dengue_chatbot_data.csv"
dst = "data/processed/Dengue_chatbot_data_clean.csv"
os.makedirs("data/processed", exist_ok=True)

EXPECTED_FIELDS = 8

def split_outside_quotes(line):
    # split on commas not inside double quotes
    parts = []
    cur = []
    q = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"':
            q = not q
            cur.append(c)
        elif c == ',' and not q:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    parts.append(''.join(cur))
    return parts

fixed = []
bad = []
with open(src, encoding="utf-8") as f:
    lines = f.read().splitlines()

# keep header as-is
fixed.append(lines[0])
buf = ""
lineno = 1

for raw in lines[1:]:
    lineno += 1
    if not buf:
        buf = raw
    else:
        buf = buf + " " + raw  # join broken rows

    fields = split_outside_quotes(buf)
    if len(fields) == EXPECTED_FIELDS:
        fixed.append(buf)
        buf = ""
    elif len(fields) > EXPECTED_FIELDS:
        # if extra commas inside unquoted text -> quote the text column heuristically (q_en/q_ru/answers)
        # last try: compress multiple spaces; keep buffering in case it resolves on next line
        pass
    else:
        # need more lines -> continue accumulating
        pass

# if anything left in buffer, mark bad
if buf:
    bad.append(("EOF-buffer", buf))

# write
with open(dst, "w", encoding="utf-8", newline="") as out:
    out.write("\n".join(fixed) + "\n")

print("✅ Wrote:", dst)
print("Bad leftovers:", len(bad))
for tag, row in bad[:10]:
    print("[BAD]", tag, "->", row[:200])
