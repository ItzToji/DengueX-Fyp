import os
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# OUTPUT
NON_DENGUE_DIR = os.path.join(
    PROJECT_ROOT, "data", "processed", "non_dengue_mosquito"
)
os.makedirs(NON_DENGUE_DIR, exist_ok=True)

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
# NON-DENGUE SOURCES (LOCKED)
# --------------------------------------------------

AMID_NON_DENGUE_FOLDERS = [
    "Culex_pipiens",
    "Culex_quinquefasciatus",
    "Armigeres_subalbatus",
    "Other_species"
]

CNN_NON_DENGUE_FOLDERS = [
    "CULEX",
    "ANOPHELES"
]

# --------------------------------------------------
# COPY LOGIC
# --------------------------------------------------

seen = set(os.listdir(NON_DENGUE_DIR))
count = 0

def copy_images(src_dir):
    global count
    for file in os.listdir(src_dir):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        if file in seen:
            continue

        src = os.path.join(src_dir, file)
        dst = os.path.join(NON_DENGUE_DIR, file)

        shutil.copy(src, dst)
        seen.add(file)
        count += 1

# AMID V1 non-dengue
for folder in AMID_NON_DENGUE_FOLDERS:
    path = os.path.join(AMID_ROOT, folder)
    if os.path.isdir(path):
        copy_images(path)

# Mosquito CNN non-dengue
for folder in CNN_NON_DENGUE_FOLDERS:
    path = os.path.join(CNN_ROOT, folder)
    if os.path.isdir(path):
        copy_images(path)

print("====================================")
print("NON-DENGUE INTEGRATION COMPLETE")
print(f"New non-dengue images added: {count}")
print("====================================")
