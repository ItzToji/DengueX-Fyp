import pandas as pd
from pathlib import Path

# --------------------------------------------------
# BASE PATH (Windows-safe)
# --------------------------------------------------
BASE = Path.home() / "Downloads"

# --------------------------------------------------
# Load files
# --------------------------------------------------
df_city = pd.read_csv(BASE / "dengue_pakistan_clean.csv")
df_prov = pd.read_csv(BASE / "dengue_pakistan_clean_FIXED_v2.csv")
df_xls = pd.read_excel(BASE / "dengue_data.xlsx", engine="openpyxl")

print("Files loaded successfully")

# --------------------------------------------------
# STANDARDIZE FILE 1 (City-level)
# --------------------------------------------------
df_city = df_city.rename(columns={"city": "location"})
df_city["location_level"] = "city"
df_city["source"] = "OpenDengue_EMRO_city"

df_city = df_city[["year", "month", "location", "location_level", "cases", "source"]]

# --------------------------------------------------
# STANDARDIZE FILE 2 (Province-level)
# --------------------------------------------------
df_prov["source"] = "OpenDengue_EMRO_province"

df_prov = df_prov[["year", "month", "location", "location_level", "cases", "source"]]

# --------------------------------------------------
# STANDARDIZE FILE 3 (Excel dataset)
# --------------------------------------------------
print("Excel columns:", df_xls.columns.tolist())

# ⚠️ Adjust names ONLY if needed
df_xls = df_xls.rename(columns={
    "city": "location",
    "dengue_cases": "cases"
})

df_xls["location_level"] = "city"
df_xls["source"] = "External_dataset_xls"

df_xls = df_xls[["year", "month", "location", "location_level", "cases", "source"]]

# --------------------------------------------------
# Combine ALL datasets
# --------------------------------------------------
final = pd.concat([df_city, df_prov, df_xls], ignore_index=True)

# --------------------------------------------------
# Final cleaning
# --------------------------------------------------
final = final.dropna()
final = final[final["cases"] > 0]

final["year"] = final["year"].astype(int)
final["month"] = final["month"].astype(int)
final["cases"] = final["cases"].astype(int)

# --------------------------------------------------
# Save MASTER dataset
# --------------------------------------------------
OUTPUT_FILE = BASE / "dengue_pakistan_MASTER_ANALYTICS.csv"
final.to_csv(OUTPUT_FILE, index=False)

print("✅ Master analytics dataset saved to:")
print(OUTPUT_FILE)
