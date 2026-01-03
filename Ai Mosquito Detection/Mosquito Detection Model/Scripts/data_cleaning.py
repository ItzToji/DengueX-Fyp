import camelot
import pandas as pd
import re
import glob

# -------------------------------------------------
# Locate NIH PDFs (Downloads folder)
# -------------------------------------------------
pdf_files = glob.glob(r"C:/Users/pc/Downloads/Weekly_Report-*-*.pdf")
print("PDFs found:", pdf_files)

rows = []

for pdf in pdf_files:
    match = re.search(r"Weekly_Report-(\d+)-(\d{4})", pdf)
    if not match:
        print(f"Skipping filename: {pdf}")
        continue

    week = int(match.group(1))
    year = int(match.group(2))
    print(f"Processing {pdf} (Week {week}, {year})")

    try:
        tables = camelot.read_pdf(pdf, pages="all", flavor="stream")
    except Exception as e:
        print(f"Failed to read {pdf}: {e}")
        continue

    for table in tables:
        df = table.df

        if df.empty:
            continue

        # First row as header
        df.columns = df.iloc[0]
        df = df[1:]

        # Find dengue column
        dengue_cols = [c for c in df.columns if "dengue" in str(c).lower()]
        if not dengue_cols:
            continue

        dengue_col = dengue_cols[0]

        for _, r in df.iterrows():
            for region in ["Punjab", "Sindh", "KP", "Balochistan", "ICT", "AJK", "GB"]:
                if region not in r:
                    continue

                val = r[region]
                if pd.isna(val) or str(val).strip() in ["NR", "", "0"]:
                    continue

                try:
                    cases = int(str(val).replace(",", ""))
                except ValueError:
                    continue

                rows.append({
                    "cases": cases,
                    "region": region,
                    "week": week,
                    "year": year
                })

# -------------------------------------------------
# Build DataFrame
# -------------------------------------------------
df = pd.DataFrame(rows)

if df.empty:
    raise ValueError(
        "No dengue data extracted.\n"
        "Camelot ran correctly, but dengue tables were not detected.\n"
        "This is expected for some NIH weeks."
    )

# -------------------------------------------------
# Convert week → month
# -------------------------------------------------
df["date"] = (
    pd.to_datetime(df["year"].astype(str) + "-01-01")
    + pd.to_timedelta((df["week"] - 1) * 7, unit="D")
)
df["month"] = df["date"].dt.month_name()

df = df[["cases", "region", "month", "year"]]
df.to_csv("pakistan_dengue_nih_2020_2025.csv", index=False)

print("\nCSV created successfully: pakistan_dengue_nih_2020_2025.csv")
print(df.head())
