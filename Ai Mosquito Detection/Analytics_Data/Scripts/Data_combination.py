import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Paths (Windows-safe)
# --------------------------------------------------
BASE = Path.home() / "Downloads"

CITY_FILE = BASE / "dengue_pakistan_clean.csv"
PROV_FILE = BASE / "dengue_pakistan_clean_FIXED_v2.csv"
OUTPUT_FILE = BASE / "dengue_pakistan_MASTER_ANALYTICS.csv"

# --------------------------------------------------
# Load datasets
# --------------------------------------------------
df_city = pd.read_csv(CITY_FILE)
df_prov = pd.read_csv(PROV_FILE)

print("City data shape:", df_city.shape)
print("Province data shape:", df_prov.shape)

# --------------------------------------------------
# STANDARDIZE CITY-LEVEL DATA
# --------------------------------------------------
df_city = df_city.rename(columns={"city": "location"})
df_city["location_level"] = "city"
df_city["source"] = "OpenDengue_city"

df_city = df_city[[
    "year",
    "month",
    "location",
    "location_level",
    "cases",
    "source"
]]

# --------------------------------------------------
# STANDARDIZE PROVINCE-LEVEL DATA
# --------------------------------------------------
df_prov["source"] = "OpenDengue_province"

df_prov = df_prov[[
    "year",
    "month",
    "location",
    "location_level",
    "cases",
    "source"
]]

# --------------------------------------------------
# COMBINE DATASETS
# --------------------------------------------------
combined = pd.concat([df_city, df_prov], ignore_index=True)

# --------------------------------------------------
# FINAL SAFETY CLEANING
# --------------------------------------------------
combined = combined.dropna()
combined = combined[combined["cases"] > 0]

combined["year"] = combined["year"].astype(int)
combined["month"] = combined["month"].astype(int)
combined["cases"] = combined["cases"].astype(int)

# --------------------------------------------------
# Save master analytics file
# --------------------------------------------------
combined.to_csv(OUTPUT_FILE, index=False)

print("✅ Combined analytics dataset saved to:")
print(OUTPUT_FILE)

# --------------------------------------------------
# Quick sanity checks
# --------------------------------------------------
print("\nLocation level counts:")
print(combined["location_level"].value_counts())

print("\nYear coverage:")
print(combined["year"].min(), "→", combined["year"].max())
