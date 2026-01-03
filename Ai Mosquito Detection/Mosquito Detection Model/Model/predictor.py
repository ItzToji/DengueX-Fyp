# mosquito_ai/predictor.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model/dengue_mosquito_model.h5")
IMAGE_SIZE = (224, 224)

CONFIDENCE_THRESHOLD_LOW = 70
CONFIDENCE_THRESHOLD_MED = 80

model = tf.keras.models.load_model(MODEL_PATH)

class_labels = {
    0: "Dengue Mosquito (Aedes)",
    1: "Non-Dengue Mosquito"
}

def predict_mosquito(img_path):
    img = image.load_img(img_path, target_size=IMAGE_SIZE)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    class_index = np.argmax(prediction)
    confidence = float(prediction[0][class_index] * 100)

    if confidence < CONFIDENCE_THRESHOLD_LOW:
        warning = "LOW_CONFIDENCE"
    elif confidence < CONFIDENCE_THRESHOLD_MED:
        warning = "MEDIUM_CONFIDENCE"
    else:
        warning = "HIGH_CONFIDENCE"

    return {
        "prediction": class_labels[class_index],
        "confidence": round(confidence, 2),
        "warning_level": warning
    }
