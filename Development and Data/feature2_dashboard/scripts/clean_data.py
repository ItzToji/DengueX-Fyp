import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

TXT_FILE = RAW / "884881269-dengue-data-2019-2024.txt"
PDF_FILE = RAW / "Weekly_Report-21-2025.pdf"

# TXT -> monthly CSV
def clean_txt():
    if not TXT_FILE.exists():
        print("[WARN] TXT file not found:", TXT_FILE)
        return
    try:
        df = pd.read_csv(TXT_FILE, sep=r"\s+", header=None, names=["date","time","cases"], engine="python", comment="#")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
        df = df.loc[df["date"].notna(), ["date","cases"]].sort_values("date").reset_index(drop=True)
        out = PROC / "monthly_dengue_2019_2024.csv"
        df.to_csv(out, index=False)
        print("[OK] TXT cleaned ->", out)
    except Exception as e:
        print("[ERROR] TXT cleaning failed:", e)

# Try Camelot extraction and safe concat
def try_camelot_extract(path, out):
    try:
        import camelot
    except Exception:
        print("[WARN] camelot not available")
        return False
    try:
        tables = camelot.read_pdf(str(path), pages="all", flavor="stream")
        if not tables or len(tables) == 0:
            print("[WARN] camelot found no tables")
            return False
        frames = []
        for t in tables:
            df = t.df.copy()
            # if first row looks like header use it
            first = df.iloc[0].astype(str).str.lower().tolist()
            if any("province" in s for s in first) or any("week" in s for s in first):
                df.columns = [c.strip().lower() for c in df.iloc[0]]
                df = df.iloc[1:].reset_index(drop=True)
            else:
                df.columns = [f"col_{i}" for i in range(df.shape[1])]
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            frames.append(df)
        # unify columns (safe concat)
        all_cols = []
        for f in frames:
            for c in f.columns:
                if c not in all_cols:
                    all_cols.append(c)
        norm = []
        for f in frames:
            norm.append(f.reindex(columns=all_cols))
        final = pd.concat(norm, ignore_index=True, sort=False)
        final = final.replace({"": None}).reset_index(drop=True)
        final.to_csv(out, index=False)
        print("[OK] Camelot extraction saved ->", out)
        return True
    except Exception as e:
        print("[WARN] Camelot extraction failed:", str(e))
        return False

# Fallback: pdfplumber -> text -> regex parse
def pdfplumber_fallback(path, out):
    try:
        import pdfplumber
    except Exception:
        print("[ERROR] pdfplumber not installed (pip install pdfplumber). Fallback unavailable.")
        return False
    try:
        text_pages = []
        with pdfplumber.open(str(path)) as pdf:
            for p in pdf.pages:
                txt = p.extract_text()
                if txt:
                    text_pages.append(txt)
        if not text_pages:
            print("[WARN] No text extracted with pdfplumber")
            return False
        all_text = "\n".join(text_pages)
        # Normalize common separators
        all_text = all_text.replace("\xa0", " ")
        # Known province names (common in Pakistan reports). Expand if needed.
        provinces = ["punjab","sindh","khyber pakhtunkhwa","kpk","balochistan","ajk","gilgit baltistan","ict","islamabad","rawalpindi","punjab province","sindh province"]
        # Build regex: capture lines that contain a province name and a series of numbers
        # Example matches: "Punjab  123  0  456"
        num = r"[-+]?\d{1,3}(?:[,]\d{3})*|\d+"
        province_pattern = r"(?P<prov>(" + "|".join(re.escape(p) for p in provinces) + r"))"
        line_re = re.compile(rf"^{province_pattern}.*?((?:{num}[\s,]*){{1,10}})", re.IGNORECASE | re.MULTILINE)
        rows = []
        for m in line_re.finditer(all_text):
            prov = m.group("prov").strip()
            tail = m.group(0)[m.group(0).lower().find(prov.lower()) + len(prov):].strip()
            # extract numbers from tail
            nums = re.findall(r"\d{1,3}(?:,\d{3})*|\d+", tail)
            nums = [int(n.replace(",","")) for n in nums]
            rows.append((prov.title(), nums))
        if not rows:
            # Secondary approach: find any line with province-like tokens followed by numbers
            generic_re = re.compile(r"^([A-Za-z \-]{2,40})\s+((?:\d{1,3}(?:,\d{3})*[\s,]*){1,10})", re.MULTILINE)
            for m in generic_re.finditer(all_text):
                name = m.group(1).strip()
                nums = re.findall(r"\d{1,3}(?:,\d{3})*|\d+", m.group(2))
                nums = [int(n.replace(",","")) for n in nums]
                rows.append((name.title(), nums))
        if not rows:
            print("[WARN] No province-number rows parsed from PDF text.")
            return False
        # Determine max numbers length -> create columns num_1..num_n
        maxlen = max(len(r[1]) for r in rows)
        out_rows = []
        for name, nums in rows:
            row = {"province": name}
            for i in range(maxlen):
                row[f"val_{i+1}"] = nums[i] if i < len(nums) else None
            out_rows.append(row)
        df = pd.DataFrame(out_rows)
        df.to_csv(out, index=False)
        print("[OK] pdfplumber fallback parsed and saved ->", out)
        return True
    except Exception as e:
        print("[ERROR] pdfplumber parsing failed:", e)
        return False

def main():
    clean_txt()
    out_pdf = PROC / "weekly_provincial_dengue_2025.csv"
    if not PDF_FILE.exists():
        print("[WARN] PDF file not found:", PDF_FILE)
        return
    print("[INFO] Attempting Camelot extraction...")
    ok = try_camelot_extract(PDF_FILE, out_pdf)
    if not ok:
        print("[INFO] Camelot failed or incomplete. Trying pdfplumber fallback...")
        ok2 = pdfplumber_fallback(PDF_FILE, out_pdf)
        if not ok2:
            print("[ERROR] All PDF extraction methods failed. Consider manually exporting tables or installing camelot + ghostscript.")
    print("[DONE]")

if __name__ == "__main__":
    main()
