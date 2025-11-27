# feature_2_dashboard/scripts/clean_all_raw.py
import pandas as pd
import numpy as np
from pathlib import Path
import glob

ROOT = Path(__file__).parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def list_csv_files(folder: Path):
    return sorted([Path(p) for p in glob.glob(str(folder / "*.csv"))])

def read_csv_safe(path: Path):
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        try:
            return pd.read_csv(path, encoding="latin1", low_memory=False)
        except Exception as e:
            print(f"Failed to read {path}: {e}")
            return None

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    rename = {}
    # common name variants -> standard
    variants = {
        "date": ["date", "report_date", "reported_on", "calendar_start_date", "reporting_date", "notification_date", "case_date", "date_reported"],
        "city": ["city", "city_name", "town", "municipality", "adm_1_name", "province", "admin1"],
        "district": ["district", "district_name", "adm_2_name", "admin2", "adm2", "adm_2", "districtname"],
        "cases": ["cases", "dengue_total", "case_count", "count", "new_cases", "total_cases", "cases_reported", "suspected", "confirmed", "value"],
        "lat": ["lat", "latitude", "y"],
        "lon": ["lon", "longitude", "long", "lng", "x"]
    }
    for std, keys in variants.items():
        for k in keys:
            if k in df.columns and std not in rename.values():
                rename[k] = std
                break
    df = df.rename(columns=rename)
    return df

def coerce_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # parse date with dayfirst True (handles many formats)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    # if date missing but year exists, create Jan 1st of year
    if ("date" not in df.columns or df["date"].isna().all()) and "year" in df.columns:
        try:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
            df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01", errors="coerce")
        except Exception:
            pass
    # numeric conversions
    if "cases" in df.columns:
        df["cases"] = pd.to_numeric(df["cases"], errors="coerce").fillna(0).astype(int)
    else:
        df["cases"] = 0
    if "lat" in df.columns:
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    else:
        df["lat"] = np.nan
    if "lon" in df.columns:
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    else:
        df["lon"] = np.nan
    # standardize text
    for col in ("city", "district"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'nan': None, 'none': None, 'na': None})
            df[col] = df[col].where(df[col].str.len() > 0, other=np.nan)
        else:
            df[col] = np.nan
    return df

def ensure_standard_cols(df: pd.DataFrame) -> pd.DataFrame:
    cols_keep = list(df.columns)
    for c in ["date", "city", "district", "cases", "lat", "lon"]:
        if c not in cols_keep:
            df[c] = np.nan
    # put standard cols first
    other = [c for c in df.columns if c not in ["date", "city", "district", "cases", "lat", "lon"]]
    return df[["date", "city", "district", "cases", "lat", "lon"] + other]

def build_dup_key(df: pd.DataFrame) -> pd.Series:
    s = df[["date", "city", "district", "cases", "lat", "lon"]].astype(str).fillna("").agg("|".join, axis=1)
    return s

def clean_all():
    files = list_csv_files(RAW_DIR)
    if not files:
        print("No CSV files found in", RAW_DIR)
        return
    cleaned_frames = []
    for p in files:
        df = read_csv_safe(p)
        if df is None:
            continue
        df = standardize_columns(df)
        df = coerce_and_clean(df)
        df = ensure_standard_cols(df)
        cleaned_frames.append(df)
        print(f"Read {p.name} -> rows {len(df)}")
    if not cleaned_frames:
        print("No data read.")
        return
    combined = pd.concat(cleaned_frames, ignore_index=True, sort=False)
    combined = combined[~(combined["date"].isna() & (combined["cases"]==0))].copy()
    combined["dup_key"] = build_dup_key(combined)
    before = len(combined)
    combined = combined.drop_duplicates(subset="dup_key").drop(columns=["dup_key"])
    after = len(combined)
    print(f"Combined rows: {before} -> deduped: {after}")
    combined["year"] = combined["date"].dt.year

    combined_out = OUT_DIR / "Dengue_data_raw.csv"
    filtered_out = OUT_DIR / "pakistan_dengue_kaggle.csv"

    combined.to_csv(combined_out, index=False)
    mask_year = combined["year"].between(2020, 2024)
    mask_city = combined["city"].str.contains("Islamabad", case=False, na=False) | combined["city"].str.contains("Rawalpindi", case=False, na=False) | combined["district"].str.contains("Islamabad", case=False, na=False) | combined["district"].str.contains("Rawalpindi", case=False, na=False)
    filtered = combined[mask_year & mask_city].copy()
    filtered.to_csv(filtered_out, index=False)

    print("Saved:", combined_out)
    print("Saved:", filtered_out)
    print("Combined total rows:", len(combined))
    print("Filtered rows (2020-2024, Islamabad & Rawalpindi):", len(filtered))

if __name__ == "__main__":
    clean_all()
