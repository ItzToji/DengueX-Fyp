import os
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

SRC_ROOT = os.path.join(PROJECT_ROOT, "data", "raw", "non_mosquito_kaggle")
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "non_mosquito_object")

os.makedirs(OUT_DIR, exist_ok=True)

VALID_EXTS = (".jpg", ".jpeg", ".png")

seen = set(os.listdir(OUT_DIR))
count = 0

def copy_from_tree(root_dir):
    global count
    for root, _, files in os.walk(root_dir):
        for f in files:
            if not f.lower().endswith(VALID_EXTS):
                continue
            if f in seen:
                continue
            src = os.path.join(root, f)
            dst = os.path.join(OUT_DIR, f)
            shutil.copy(src, dst)
            seen.add(f)
            count += 1

if not os.path.isdir(SRC_ROOT):
    raise RuntimeError(f"Source folder not found: {SRC_ROOT}")

copy_from_tree(SRC_ROOT)

print("====================================")
print("NON-MOSQUITO OBJECT INTEGRATION DONE")
print(f"Images added: {count}")
print(f"Total now in non_mosquito_object: {len(os.listdir(OUT_DIR))}")
print("====================================")
