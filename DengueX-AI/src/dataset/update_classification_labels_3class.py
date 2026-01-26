import os
import csv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

DENGUE_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "dengue_mosquito")
NON_DENGUE_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "non_dengue_mosquito")
NON_MOSQ_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "non_mosquito_object")

OUT_DIR = os.path.join(PROJECT_ROOT, "data", "annotations")
os.makedirs(OUT_DIR, exist_ok=True)

CSV_PATH = os.path.join(OUT_DIR, "classification_labels_3class.csv")

rows = []

for f in os.listdir(DENGUE_DIR):
    if f.lower().endswith((".jpg", ".jpeg", ".png")):
        rows.append([f, "dengue"])

for f in os.listdir(NON_DENGUE_DIR):
    if f.lower().endswith((".jpg", ".jpeg", ".png")):
        rows.append([f, "non_dengue"])

for f in os.listdir(NON_MOSQ_DIR):
    if f.lower().endswith((".jpg", ".jpeg", ".png")):
        rows.append([f, "non_mosquito"])

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "label"])
    writer.writerows(rows)

print("====================================")
print("3-CLASS LABELS CREATED")
print(f"Total images labeled: {len(rows)}")
print(f"Saved to: {CSV_PATH}")
print("====================================")
