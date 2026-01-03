import tensorflow as tf
import numpy as np
import os
import csv
from tensorflow.keras.preprocessing import image

# Paths
MODEL_PATH = "Model/dengue_mosquito_model.h5"
IMAGE_FOLDER = "test_images"
RESULTS_DIR = "results"
RESULTS_FILE = os.path.join(RESULTS_DIR, "prediction_results.csv")

IMAGE_SIZE = (224, 224)

# Confidence thresholds
STRONG_WARNING_THRESHOLD = 70.0   # below this → strong warning
LIGHT_WARNING_THRESHOLD = 80.0    # 70–79 → light warning

# Create results directory if not exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels
class_labels = {
    0: "Dengue Mosquito (Aedes)",
    1: "Non-Dengue Mosquito"
}

# Open CSV file and write header
with open(RESULTS_FILE, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([
        "image_name",
        "predicted_class",
        "confidence",
        "warning_level"
    ])

    print("\n🧪 Batch Prediction Results")
    print("-" * 40)

    for img_name in os.listdir(IMAGE_FOLDER):

        # Only process image files
        if img_name.lower().endswith((".jpg", ".jpeg", ".png", ".jfif")):
            img_path = os.path.join(IMAGE_FOLDER, img_name)

            # Load & preprocess image
            img = image.load_img(img_path, target_size=IMAGE_SIZE)
            img_array = image.img_to_array(img)
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Predict
            prediction = model.predict(img_array)
            class_index = np.argmax(prediction)
            confidence = prediction[0][class_index] * 100

            # Determine warning level
            if confidence < STRONG_WARNING_THRESHOLD:
                warning_level = "HIGH"
            elif confidence < LIGHT_WARNING_THRESHOLD:
                warning_level = "MEDIUM"
            else:
                warning_level = "LOW"

            # Console output
            print(f"Image: {img_name}")
            print(f"Prediction: {class_labels[class_index]}")
            print(f"Confidence: {confidence:.2f}%")

            if warning_level == "MEDIUM":
                print("🟡 Caution: Model confidence is moderate.")
            elif warning_level == "HIGH":
                print("🔴 Warning: Model confidence is low.")

            print("-" * 40)

            # Save to CSV
            writer.writerow([
                img_name,
                class_labels[class_index],
                round(confidence, 2),
                warning_level
            ])

print(f"\n✅ Results saved to: {RESULTS_FILE}")
