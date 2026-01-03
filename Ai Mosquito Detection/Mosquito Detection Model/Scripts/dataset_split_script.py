import os
import shutil
import random

base_dir = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_final"

output_dir = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_split"

classes = ["dengue", "non_dengue"]
split_ratio = {
    "train": 0.7,
    "val": 0.15,
    "test": 0.15
}

random.seed(42)

for cls in classes:
    images = os.listdir(os.path.join(base_dir, cls))
    random.shuffle(images)

    total = len(images)
    train_end = int(total * split_ratio["train"])
    val_end = train_end + int(total * split_ratio["val"])

    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:]
    }

    for split, files in splits.items():
        split_dir = os.path.join(output_dir, split, cls)
        os.makedirs(split_dir, exist_ok=True)

        for file in files:
            src = os.path.join(base_dir, cls, file)
            dst = os.path.join(split_dir, file)
            shutil.copy(src, dst)

print("✅ Dataset successfully split into train / val / test.")
