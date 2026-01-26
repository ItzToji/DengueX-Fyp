import os
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# OUTPUT (DO NOT TOUCH NON-DENGUE)
DENGUE_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "dengue_mosquito")
os.makedirs(DENGUE_DIR, exist_ok=True)

# --------------------------------------------------
# INPUT PATHS
# --------------------------------------------------

AMID_ROOT = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "aedes_kaggle",
    "aedes_only",
    "AMID V1"
)

CNN_ROOT = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "aedes_kaggle",
    "mosquito_cnn",
    "Mosquito_dataset"
)

# --------------------------------------------------
# AEDES SOURCES (LOCKED)
# --------------------------------------------------

AMID_AEDES_FOLDERS = [
    "Aedes_aegypti",
    "Aedes_albopictus",
    "Aedes_japonicus",
    "Aedes_koreicus"
]

CNN_AEDES_FOLDER = "AEDES"

# --------------------------------------------------
# COPY LOGIC
# --------------------------------------------------

seen = set()
count = 0

def copy_images(src_dir):
    global count
    for file in os.listdir(src_dir):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        if file in seen:
            continue

        src = os.path.join(src_dir, file)
        dst = os.path.join(DENGUE_DIR, file)

        shutil.copy(src, dst)
        seen.add(file)
        count += 1

# AMID V1
for folder in AMID_AEDES_FOLDERS:
    path = os.path.join(AMID_ROOT, folder)
    if os.path.isdir(path):
        copy_images(path)

# Mosquito CNN
cnn_aedes_path = os.path.join(CNN_ROOT, CNN_AEDES_FOLDER)
if os.path.isdir(cnn_aedes_path):
    copy_images(cnn_aedes_path)

print("====================================")
print("AEDES INTEGRATION COMPLETE")
print(f"Total Aedes images added: {count}")
print("====================================")
