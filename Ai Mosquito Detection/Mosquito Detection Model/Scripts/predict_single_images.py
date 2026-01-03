import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing import image

# Paths
MODEL_PATH = "Model/dengue_mosquito_model.h5"
IMAGE_FOLDER = "test_images"

IMAGE_SIZE = (224, 224)

# Confidence thresholds
STRONG_WARNING_THRESHOLD = 70.0   # below this → strong warning
LIGHT_WARNING_THRESHOLD = 80.0    # 70–79 → light warning

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels (same order as training)
class_labels = {
    0: "Dengue Mosquito (Aedes)",
    1: "Non-Dengue Mosquito"
}

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

        # Output
        print(f"Image: {img_name}")
        print(f"Prediction: {class_labels[class_index]}")
        print(f"Confidence: {confidence:.2f}%")

        # 🟡 Light warning (70–79%)
        if STRONG_WARNING_THRESHOLD <= confidence < LIGHT_WARNING_THRESHOLD:
            print("🟡 Caution: Model confidence is moderate.")
            print("🟡 Result may not be fully reliable. Consider verifying the image.")

        # 🔴 Strong warning (< 70%)
        elif confidence < STRONG_WARNING_THRESHOLD:
            print("🔴 Warning: Model confidence is low.")
            print("🔴 Prediction is uncertain. Please use a clearer image or manual verification.")

        print("-" * 40)
