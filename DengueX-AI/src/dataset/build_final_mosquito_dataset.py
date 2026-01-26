import os
import csv
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_ROOT = os.path.join(PROJECT_ROOT, "data", "raw")
OUT_ROOT = os.path.join(PROJECT_ROOT, "data", "processed")

DENGUE_DIR = os.path.join(OUT_ROOT, "dengue_mosquito")
NON_DENGUE_DIR = os.path.join(OUT_ROOT, "non_dengue_mosquito")

os.makedirs(DENGUE_DIR, exist_ok=True)
os.makedirs(NON_DENGUE_DIR, exist_ok=True)

# --------------------------------------------------
# CLASS DEFINITIONS (GROUND TRUTH)
# --------------------------------------------------

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

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def find_csv_files(base_dir):
    csvs = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".csv"):
                csvs.append(os.path.join(root, f))
    return csvs


def collect_labels(csv_file):
    image_labels = {}
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row["filename"]
            label = row["class"].strip().lower()
            image_labels.setdefault(fname, set()).add(label)
    return image_labels


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

seen_images = set()

print("[INFO] Scanning datasets in data/raw/...")

csv_files = find_csv_files(RAW_ROOT)

if not csv_files:
    raise RuntimeError("No CSV annotation files found.")

for csv_path in csv_files:
    dataset_dir = os.path.dirname(csv_path)
    print(f"[INFO] Using annotations: {csv_path}")

    labels_map = collect_labels(csv_path)

    for fname, labels in labels_map.items():
        if fname in seen_images:
            continue

        image_path = os.path.join(dataset_dir, fname)
        if not os.path.exists(image_path):
            continue

        if labels & DENGUE_CLASSES:
            shutil.copy(image_path, DENGUE_DIR)
            seen_images.add(fname)

        elif labels & NON_DENGUE_CLASSES:
            shutil.copy(image_path, NON_DENGUE_DIR)
            seen_images.add(fname)

print("==========================================")
print("FINAL DATASET BUILD COMPLETE")
print(f"Dengue images     : {len(os.listdir(DENGUE_DIR))}")
print(f"Non-dengue images : {len(os.listdir(NON_DENGUE_DIR))}")
print("==========================================")
