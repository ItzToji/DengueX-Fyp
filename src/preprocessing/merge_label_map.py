#!/usr/bin/env python3
"""
Merge / remap intent labels into a smaller, cleaner set and write a new CSV.

Usage (from project root):
    python -m src.preprocessing.merge_label_map
or
    python src/preprocessing/merge_label_map.py

Input:
    data/processed/Dengue_chatbot_data_clean.csv

Output:
    data/processed/Dengue_chatbot_data_merged_labels.csv
    data/processed/label_map.json   (the mapping used)
"""
import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
IN_CSV = ROOT / "data" / "processed" / "Dengue_chatbot_data_clean.csv"
OUT_CSV = ROOT / "data" / "processed" / "Dengue_chatbot_data_merged_labels.csv"
MAP_OUT = ROOT / "data" / "processed" / "label_map.json"

# --- Configure your target label set and mapping rules here ---
# Keys are source tags (possible values from 'tags' column).
# Values are the consolidated target label you want for training.
LABEL_MAP = {
    # core high-volume intents (keep)
    "symptoms": "symptoms",
    "warning_signs": "warning_signs",
    "hydration": "hydration",
    "diagnosis": "diagnosis",
    "medications": "medications",
    "laboratory": "laboratory",
    "labs": "laboratory",
    "nutrition": "nutrition",
    "pediatrics": "pediatrics",
    "timeline": "timeline",
    "transmission": "transmission",
    "prevention": "prevention",
    "treatment": "treatment",
    "immunity": "immunity",
    "severe_dengue": "severe_dengue",
    "severe": "severe_dengue",
    "mosquito_control": "mosquito_control",
    "vector": "mosquito_control",
    "vector_control": "mosquito_control",
    "pregnancy": "pregnancy",
    "recovery": "recovery",
    "breastfeeding": "breastfeeding",
    "travel": "travel",
    "community": "community",
    # medium / low volume -> keep but may be collapsed to 'other' later
    "bleeding": "bleeding",
    "complications": "complications",
    "breeding": "breeding",
    "myths": "myths",
    "platelets": "platelets",
    "fatigue": "fatigue",
    "risks": "risks",
    "body_pain": "symptoms",
    "muscle": "symptoms",
    "eye": "symptoms",
    "skin": "symptoms",
    "gastro": "symptoms",
    "cardio": "symptoms",
    "sleep": "symptoms",
    "assessment": "assessment",
    "mosquito_behavior": "mosquito_control",
    "geriatrics": "geriatrics",
    "virology": "virology",
    "monitoring": "laboratory",
    "household": "mosquito_control",
    "repellents": "prevention",
}

# Any source tag not in LABEL_MAP will be mapped to this:
DEFAULT_LABEL = "other"

MIN_SUPPORT = 5  # later you can collapse labels with support < MIN_SUPPORT into 'other'

def pick_primary_tag(tags_field: str) -> str:
    """Return the primary tag (first) from the tags field."""
    if not isinstance(tags_field, str) or tags_field.strip() == "":
        return ""
    # tags are expected like "symptoms;hydration"
    return tags_field.split(";")[0].strip()

def apply_map(tag: str, mapping: dict) -> str:
    return mapping.get(tag, DEFAULT_LABEL)

def collapse_rare_labels(series: pd.Series, min_support: int):
    counts = series.value_counts()
    rare = counts[counts < min_support].index.tolist()
    if not rare:
        return series, []
    series = series.apply(lambda t: "other" if t in rare else t)
    return series, rare

def main():
    assert IN_CSV.exists(), f"Input not found: {IN_CSV}"
    df = pd.read_csv(IN_CSV)
    print(f"Loaded {len(df)} rows from {IN_CSV.name}")

    # 1) derive primary_tag from 'tags' column
    df["primary_tag"] = df["tags"].fillna("").apply(pick_primary_tag)

    # 2) map primary_tag -> target label using LABEL_MAP (or DEFAULT_LABEL)
    df["merged_label"] = df["primary_tag"].apply(lambda t: apply_map(t, LABEL_MAP))

    # 3) show counts and collapse rare labels into 'other' if needed
    counts_before = df["merged_label"].value_counts()
    print("\nCounts before collapse:")
    print(counts_before.head(40))

    df["merged_label"], rare = collapse_rare_labels(df["merged_label"], MIN_SUPPORT)
    if rare:
        print(f"\nCollapsed {len(rare)} rare labels into 'other':")
        print(rare)

    counts_after = df["merged_label"].value_counts()
    print("\nCounts after collapse:")
    print(counts_after.head(60))

    # 4) write out new csv (keeps all original columns + merged_label)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"\nWrote merged CSV -> {OUT_CSV}")

   # 5) save the label map used (for reproducibility)
MAP_OUT.parent.mkdir(parents=True, exist_ok=True)
with open(MAP_OUT, "w", encoding="utf-8") as f:
    json.dump(
        {
            "label_map": LABEL_MAP,
            "default_label": DEFAULT_LABEL,
            "min_support": MIN_SUPPORT,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )
print(f"Saved label map -> {MAP_OUT}")

if __name__ == "__main__":
    main()

