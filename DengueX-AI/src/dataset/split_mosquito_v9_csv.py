import os
import csv
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# 🔴 THIS IS THE CRITICAL LINE
RAW_DATA = os.path.join(PROJECT_ROOT, "data", "raw", "mosquitov9")

OUT_BASE = os.path.join(PROJECT_ROOT, "data", "processed", "mosquitov9")

DENGUE_DIR = os.path.join(OUT_BASE, "dengue_mosquito")
NON_DENGUE_DIR = os.path.join(OUT_BASE, "non_dengue_mosquito")
NON_MOSQUITO_DIR = os.path.join(OUT_BASE, "non_mosquito")

for d in [DENGUE_DIR, NON_DENGUE_DIR, NON_MOSQUITO_DIR]:
    os.makedirs(d, exist_ok=True)

DENGUE_CLASSES = {
    "aedes",
    "aedes aegypti",
    "aedes_aegypti",
    "aedes albopictus",
    "aedes-albopictus"
}

NON_DENGUE_CLASSES = {
    "culex",
    "anopheles"
}

def find_csv(split_dir):
    for f in os.listdir(split_dir):
        if f.lower().endswith(".csv"):
            return os.path.join(split_dir, f)
    return None

def process_split(split):
    split_dir = os.path.join(RAW_DATA, split)

    if not os.path.isdir(split_dir):
        raise RuntimeError(f"Missing split folder: {split_dir}")

    csv_path = find_csv(split_dir)
    if csv_path is None:
        raise RuntimeError(f"No CSV found in {split_dir}")

    print(f"[INFO] Using CSV: {csv_path}")

    image_labels = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row["filename"]
            label = row["class"].strip().lower()
            image_labels.setdefault(fname, set()).add(label)

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

for split in ["train", "valid", "test"]:
    process_split(split)

print("mosquitov9 dataset separated successfully.")

