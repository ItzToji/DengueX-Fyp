import os
import csv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

DENGUE_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "dengue_mosquito")
NON_DENGUE_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "non_dengue_mosquito")

OUT_DIR = os.path.join(PROJECT_ROOT, "data", "annotations")
os.makedirs(OUT_DIR, exist_ok=True)

CSV_PATH = os.path.join(OUT_DIR, "classification_labels.csv")

rows = []

for file in os.listdir(DENGUE_DIR):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        rows.append([file, "dengue"])

for file in os.listdir(NON_DENGUE_DIR):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        rows.append([file, "non_dengue"])

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "label"])
    writer.writerows(rows)

print("====================================")
print("CLASSIFICATION LABELS CREATED")
print(f"Total images labeled: {len(rows)}")
print(f"Saved to: {CSV_PATH}")
print("====================================")
