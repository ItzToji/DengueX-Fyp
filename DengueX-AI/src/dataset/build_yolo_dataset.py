import os
import random
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

SRC = {
    0: os.path.join(PROJECT_ROOT, "data", "processed", "dengue_mosquito"),
    1: os.path.join(PROJECT_ROOT, "data", "processed", "non_dengue_mosquito"),
    2: os.path.join(PROJECT_ROOT, "data", "processed", "non_mosquito_object"),
}

YOLO_BASE = os.path.join(PROJECT_ROOT, "data", "yolo")
YOLO_IMG = os.path.join(YOLO_BASE, "images")
YOLO_LBL = os.path.join(YOLO_BASE, "labels")

# 🔒 ENSURE ALL REQUIRED DIRECTORIES EXIST
for split in ["train", "val", "test"]:
    os.makedirs(os.path.join(YOLO_IMG, split), exist_ok=True)
    os.makedirs(os.path.join(YOLO_LBL, split), exist_ok=True)

random.seed(42)

def split_files(files):
    random.shuffle(files)
    n = len(files)
    return {
        "train": files[:int(0.7*n)],
        "val": files[int(0.7*n):int(0.9*n)],
        "test": files[int(0.9*n):]
    }

total_copied = 0

for class_id, src_dir in SRC.items():
    files = [
        f for f in os.listdir(src_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    splits = split_files(files)

    for split, split_files_list in splits.items():
        for f in split_files_list:
            src_img = os.path.join(src_dir, f)
            dst_img = os.path.join(YOLO_IMG, split, f)
            dst_lbl = os.path.join(YOLO_LBL, split, os.path.splitext(f)[0] + ".txt")

            shutil.copy2(src_img, dst_img)

            with open(dst_lbl, "w") as out:
                out.write(f"{class_id} 0.5 0.5 1.0 1.0\n")

            total_copied += 1
            if total_copied % 500 == 0:
                print(f"[INFO] Copied {total_copied} images...")

print("===================================")
print("YOLOv8 DATASET BUILD COMPLETE")
print(f"Total images processed: {total_copied}")
print("===================================")
