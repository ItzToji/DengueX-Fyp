import os
import csv
import shutil

# =====================================================
# PATH CONFIGURATION
# =====================================================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA = os.path.join(PROJECT_ROOT, "data", "raw")
OUTPUT_BASE = os.path.join(PROJECT_ROOT, "data", "processed")

DENGUE_DIR = os.path.join(OUTPUT_BASE, "dengue_mosquito")
NON_DENGUE_DIR = os.path.join(OUTPUT_BASE, "non_dengue_mosquito")
NON_MOSQUITO_DIR = os.path.join(OUTPUT_BASE, "non_mosquito")

for d in [DENGUE_DIR, NON_DENGUE_DIR, NON_MOSQUITO_DIR]:
    os.makedirs(d, exist_ok=True)

# =====================================================
# CLASS DEFINITIONS (STRING-BASED)
# =====================================================

DENGUE_CLASSES = {
    "aedes",
    "aedes_aegypti",
    "aedes-albopictus",
    "aedes albopictus"
}

NON_DENGUE_CLASSES = {
    "culex",
    "anopheles"
}

# =====================================================
# PROCESS EACH SPLIT
# =====================================================

def process_split(split):
    split_dir = os.path.join(RAW_DATA, split)
    csv_path = os.path.join(split_dir, "_annotations.csv")

    if not os.path.isfile(csv_path):
        print(f"[SKIP] No annotations for {split}")
        return

    # Build image → class mapping
    image_labels = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row["filename"]
            label = row["class"].strip().lower()
            image_labels.setdefault(filename, set()).add(label)

    # Process images
    for file in os.listdir(split_dir):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        src = os.path.join(split_dir, file)
        labels = image_labels.get(file, set())

        if labels & DENGUE_CLASSES:
            shutil.copy(src, DENGUE_DIR)
        elif labels & NON_DENGUE_CLASSES:
            shutil.copy(src, NON_DENGUE_DIR)
        else:
            shutil.copy(src, NON_MOSQUITO_DIR)

# =====================================================
# RUN
# =====================================================

for split in ["train", "valid", "test"]:
    process_split(split)

print("Dataset separation completed successfully.")
