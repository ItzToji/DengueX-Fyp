import os
import shutil

# ✅ CORRECT PATHS (based on your screenshot)
anopheles_dir = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_raw\Mosquito_dataset\ANOPHELES"
culex_dir = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_raw\Mosquito_dataset\CULEX"
aedes_dir = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_raw\Mosquito_dataset\AEDES"

output_non_dengue = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_final\non_dengue"
output_dengue = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_final\dengue"

os.makedirs(output_non_dengue, exist_ok=True)
os.makedirs(output_dengue, exist_ok=True)

def copy_and_rename(source_dir, prefix, output_dir):
    count = 1
    for file in os.listdir(source_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            new_name = f"{prefix}_{count:04d}.jpg"
            shutil.copy(
                os.path.join(source_dir, file),
                os.path.join(output_dir, new_name)
            )
            count += 1

# Non-dengue
copy_and_rename(anopheles_dir, "anopheles", output_non_dengue)
copy_and_rename(culex_dir, "culex", output_non_dengue)

# Dengue
copy_and_rename(aedes_dir, "aedes", output_dengue)

print("✅ Dataset copied and renamed successfully.")
