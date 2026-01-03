import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# Paths
# =========================
RESULTS_FILE = "results/prediction_results.csv"
OUTPUT_DIR = "results/graphs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# Load data
# =========================
df = pd.read_csv(RESULTS_FILE)

# =========================
# Global plot settings
# =========================
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.size"] = 12

# =========================
# 1. Class Distribution
# =========================
plt.figure(figsize=(7, 5))
df["predicted_class"].value_counts().plot(kind="bar")
plt.title("Distribution of Predicted Mosquito Classes", fontsize=14)
plt.xlabel("Mosquito Class")
plt.ylabel("Number of Images")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/class_distribution.png")
plt.close()

# =========================
# 2. Confidence Score Histogram
# =========================
plt.figure(figsize=(7, 5))
plt.hist(df["confidence"], bins=10)
plt.title("Confidence Score Distribution", fontsize=14)
plt.xlabel("Confidence (%)")
plt.ylabel("Number of Images")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/confidence_distribution.png")
plt.close()

# =========================
# 3. Warning Level Distribution
# =========================
plt.figure(figsize=(7, 5))
df["warning_level"].value_counts().plot(kind="bar")
plt.title("Prediction Warning Level Distribution", fontsize=14)
plt.xlabel("Warning Level")
plt.ylabel("Number of Images")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/warning_distribution.png")
plt.close()

# =========================
# 4. Image-wise Confidence Scores
# =========================
plt.figure(figsize=(10, 5))
plt.bar(df["image_name"], df["confidence"])
plt.title("Confidence Score per Image", fontsize=14)
plt.xlabel("Image Name")
plt.ylabel("Confidence (%)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/confidence_per_image.png")
plt.close()

print("✅ All graphs generated successfully.")
print(f"📁 Saved in: {OUTPUT_DIR}")
