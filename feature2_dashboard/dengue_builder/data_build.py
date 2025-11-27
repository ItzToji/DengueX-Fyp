#!/usr/bin/env python3
"""
data_build.py

Download and build a combined dengue dataset (Option A) for Islamabad & Rawalpindi (2020-2024),
including case data, weather, and administrative boundaries, then export a ZIP file with:
 - cases_2020_2024.csv
 - islamabad_sectors.geojson
 - rawalpindi_ucs.geojson
 - pakistan_districts.geojson
 - metadata.json
 - README.txt

USAGE:
  1. Install requirements: pip install -r requirements.txt
  2. Set up Kaggle credentials (if you want to download Kaggle datasets):
       - Create ~/.kaggle/kaggle.json with your API token
       - Alternatively, download datasets manually and place into data/raw/
  3. Run: python data_build.py
  4. Output ZIP will be created at ./output/dengue_data_2020_2024_pakistan.zip

NOTES:
 - This script tries multiple sources. If a source requires manual download (e.g. Kaggle),
   place the file under data/raw/ with the expected filename (see README.md).
 - Internet access must be available for the script to download public files.
"""

import os
import sys
import shutil
from pathlib import Path
import requests
import zipfile
import pandas as pd
import geopandas as gpd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

ROOT = Path.cwd()
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
OUT_DIR = ROOT / "output"

for p in [DATA_RAW, DATA_PROC, OUT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# ---------- CONFIG: URLs & filenames (editable) ------------
# NOTE: some sources (Kaggle) require auth or manual download. The script will check local files first.
SOURCES = {
    "gadm_pak_districts": {
        "url": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_PAK_2.json",
        "local": DATA_RAW / "gadm41_PAK_2.json"
    },
    "islamabad_sectors": {
        "url": "https://raw.githubusercontent.com/codeforpakistan/Open-Islamabad/master/GeoJSON/islamabad-sectors.geojson",
        "local": DATA_RAW / "islamabad-sectors.geojson"
    },
    "rawalpindi_ucs": {
        "url": "https://raw.githubusercontent.com/codeforpakistan/Open-Rawalpindi/master/geojson/rawalpindi-ucs.geojson",
        "local": DATA_RAW / "rawalpindi-ucs.geojson"
    },
    "nih_weekly_example_pdf": {
        "url": "https://nih.org.pk/wp-content/uploads/2024/10/Weekly_Report-38-2024.pdf",
        "local": DATA_RAW / "nih_weekly_38_2024.pdf"
    },
    # Kaggle datasets (expected local filenames if downloaded manually or by kaggle API)
    "kaggle_pakistan_dengue": {
        "url": None,
        "local": DATA_RAW / "pakistan_dengue_kaggle.csv",  # expected filename if manually placed
        "note": "Place the Kaggle CSV here if you downloaded it (kaggle requires auth)"
    },
    "kaggle_punjab": {
        "url": None,
        "local": DATA_RAW / "punjab_dengue_kaggle.csv",
        "note": "Place Punjab dataset here if available"
    }
}

# ---------- helper functions ----------
def download_file(url, target_path, chunk_size=1024*64):
    if target_path.exists():
        logging.info(f"Already present: {target_path.name}")
        return target_path
    logging.info(f"Downloading {url} -> {target_path.name}")
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(target_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    logging.info("Downloaded OK")
    return target_path

def load_kaggle_csv(local_path):
    if local_path.exists():
        logging.info(f"Found local Kaggle CSV: {local_path.name}")
        return pd.read_csv(local_path)
    logging.warning(f"Kaggle file not found: {local_path}. If you want to auto-download from Kaggle, configure kaggle API and modify this script.")
    return None

# ---------- Step 1: download public files where possible ----------
for key, info in SOURCES.items():
    url = info.get("url")
    local = info.get("local")
    if url:
        try:
            download_file(url, local)
        except Exception as e:
            logging.warning(f"Could not download {key}: {e} - you can place the file manually at {local}")
    else:
        logging.info(f"No URL for {key}; expecting local file: {local}")

# ---------- Step 2: Read & inspect shapefiles ----------
logging.info("Loading Pakistan districts GeoJSON")
pak_gdf = None
try:
    pak_gdf = gpd.read_file(SOURCES["gadm_pak_districts"]["local"])
    logging.info("Loaded Pakistan districts geometry")
except Exception as e:
    logging.warning(f"Could not read Pakistan districts GeoJSON: {e} - ensure the file exists in data/raw/")

# Load Islamabad sectors & Rawalpindi UCs if available
try:
    islamabad_gdf = gpd.read_file(SOURCES["islamabad_sectors"]["local"])
    logging.info("Loaded Islamabad sectors")
except Exception as e:
    islamabad_gdf = None
    logging.warning(f"Islamabad sectors not found: {e}")

try:
    rawalpindi_gdf = gpd.read_file(SOURCES["rawalpindi_ucs"]["local"])
    logging.info("Loaded Rawalpindi UCs")
except Exception as e:
    rawalpindi_gdf = None
    logging.warning(f"Rawalpindi UCs not found: {e}")

# ---------- Step 3: Obtain case data ----------
# Strategy:
# - Prefer local Kaggle CSVs if present.
# - Otherwise try to parse NIH PDF(s) in data/raw/ using tabula or camelot (requires Java for tabula).
# - Fallback: user should place official CSVs into data/raw/

cases_df = None
# Try Kaggle Pakistan CSV
cases_df = load_kaggle_csv(SOURCES["kaggle_pakistan_dengue"]["local"])
if cases_df is None:
    cases_df = load_kaggle_csv(SOURCES["kaggle_punjab"]["local"])

# If still None, attempt to parse NIH PDF weekly reports (simple heuristic)
if cases_df is None:
    pdf_path = SOURCES["nih_weekly_example_pdf"]["local"]
    if pdf_path.exists():
        logging.info("Attempting to extract tables from NIH PDF (requires camelot or tabula installed and Java).")
        try:
            import camelot
            tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')
            logging.info(f"Found {len(tables)} tables in the PDF. Trying to concatenate.")
            df_list = []
            for t in tables:
                df_list.append(t.df)
            if df_list:
                combined = pd.concat(df_list, ignore_index=True)
                combined.to_csv(DATA_RAW / "nih_extracted.csv", index=False)
                cases_df = combined
                logging.info("Saved NIH extracted CSV")
        except Exception as e:
            logging.warning(f"PDF extraction failed: {e}. Place case CSVs manually into data/raw/.")
    else:
        logging.warning("No case data found automatically. Please place your CSV files in data/raw/ with filenames: pakistani kaggle csvs or punjab csv.")

if cases_df is None:
    logging.error("No case data available. Exiting with instruction to add data to data/raw/")
    sys.exit(1)

# ---------- Step 4: basic cleaning & filter 2020-2024, Islamabad & Rawalpindi ----------
logging.info("Cleaning case data (best-effort)")
# attempting common column names
cols = [c.lower() for c in cases_df.columns]
# heuristics to find date, city/district, cases columns
date_col = None
loc_col = None
cases_col = None
for c in cases_df.columns:
    lc = c.lower()
    if 'date' in lc:
        date_col = c
    if any(x in lc for x in ['district','city','area','location','region']):
        loc_col = c
    if any(x in lc for x in ['cases','case','count','no.']):
        cases_col = c

logging.info(f"Detected columns -> date: {date_col}, location: {loc_col}, cases: {cases_col}")

# normalize and filter
if date_col is None:
    logging.error("No date column detected. Please ensure your case CSV has a date column. Stopping.")
    sys.exit(1)

cases_df[date_col] = pd.to_datetime(cases_df[date_col], errors='coerce')
cases_df = cases_df.dropna(subset=[date_col])
cases_df = cases_df[(cases_df[date_col].dt.year >= 2020) & (cases_df[date_col].dt.year <= 2024)]

# normalize location strings for matching Islamabad/Rawalpindi
def norm(s):
    try:
        return str(s).strip().lower()
    except:
        return ''

if loc_col:
    cases_df['loc_norm'] = cases_df[loc_col].apply(norm)
    mask = cases_df['loc_norm'].str.contains('islamabad') | cases_df['loc_norm'].str.contains('rawalpindi') | cases_df['loc_norm'].str.contains('isl.') 
    filtered = cases_df[mask].copy()
else:
    logging.warning("No location column found; attempting to spatial-join by lat/lon if available")
    filtered = cases_df

if filtered.empty:
    logging.warning("No records explicitly matching Islamabad/Rawalpindi found. You may need to supply a case CSV that includes city/district columns or lat/lon.")
    # still continue and write an empty cleaned file for the user to inspect

# keep essential columns & write cleaned CSV
out_cases = DATA_PROC / "cases_2020_2024_isb_rawalpindi.csv"
filtered.to_csv(out_cases, index=False)
logging.info(f"Wrote cleaned cases CSV -> {out_cases} (rows: {len(filtered)})")

# ---------- Step 5: Prepare geojson outputs (subset relevant features) ----------
# Subset Pakistan districts to Rawalpindi & Islamabad if pak_gdf is available
if pak_gdf is not None:
    # try common name fields
    name_cols = [c for c in pak_gdf.columns if 'NAME' in str(c).upper() or 'name'==str(c).lower() or 'NAME_1' in str(c)]
    # fallback to 'GID_2' or 'GID_1'
    try:
        # find column with district name heuristically
        district_name_col = None
        for c in pak_gdf.columns:
            if 'NAME_2' in str(c).upper() or 'NAME_1' in str(c).upper() or c.lower()=='name':
                district_name_col = c
                break
        if district_name_col is None:
            district_name_col = pak_gdf.columns[0]
        pak_gdf['nm_norm'] = pak_gdf[district_name_col].astype(str).str.lower()
        sel = pak_gdf[pak_gdf['nm_norm'].str.contains('rawalpindi') | pak_gdf['nm_norm'].str.contains('islamabad')]
        if not sel.empty:
            sel.to_file(DATA_PROC / "pakistan_districts_subset_isb_rawalpindi.geojson", driver="GeoJSON")
            logging.info("Wrote pakistan_districts_subset_isb_rawalpindi.geojson")
        else:
            logging.warning("Could not find matching district names in GADM file; saving full districts file instead.")
            pak_gdf.to_file(DATA_PROC / "pakistan_districts_all.geojson", driver="GeoJSON")
    except Exception as e:
        logging.warning(f"Error processing pak_gdf: {e}")

# copy islamabad & rawalpindi finer geodata if present
if islamabad_gdf is not None:
    islamabad_gdf.to_file(DATA_PROC / "islamabad_sectors.geojson", driver="GeoJSON")
    logging.info("Saved islamabad_sectors.geojson to processed folder")
if rawalpindi_gdf is not None:
    rawalpindi_gdf.to_file(DATA_PROC / "rawalpindi_ucs.geojson", driver="GeoJSON")
    logging.info("Saved rawalpindi_ucs.geojson to processed folder")

# ---------- Step 6: create metadata.json ----------
meta = {
    "created_at": datetime.utcnow().isoformat() + "Z",
    "sources": {
        k: (str(v.get('url')) if v.get('url') else "local file expected") for k,v in SOURCES.items()
    },
    "notes": "Built using available public sources. Filtered to years 2020-2024 and locations Islamabad/Rawalpindi where possible."
}
with open(DATA_PROC / "metadata.json", "w") as f:
    import json
    json.dump(meta, f, indent=2)
logging.info("Wrote metadata.json")

# ---------- Step 7: package outputs into zip ----------
zip_path = OUT_DIR / "dengue_data_2020_2024_pakistan.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    # include processed CSV if it exists
    for p in DATA_PROC.glob("*"):
        z.write(p, arcname=p.name)
    # include any raw files that may be useful (small PDFs / geojson)
    for p in DATA_RAW.glob("*"):
        if p.suffix.lower() in ['.json', '.geojson', '.csv', '.pdf']:
            # avoid huge files by skipping >200MB
            try:
                if p.stat().st_size < 200*1024*1024:
                    z.write(p, arcname=f"raw/{p.name}")
            except Exception:
                pass
logging.info(f"Created ZIP -> {zip_path}")

print("DONE. Output zip:", zip_path)
