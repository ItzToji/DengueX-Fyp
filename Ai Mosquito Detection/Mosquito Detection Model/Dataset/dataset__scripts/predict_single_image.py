import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Paths
MODEL_PATH = "Model/dengue_mosquito_model.h5"
IMAGE_PATH = "test_image/mosquito1.jpg"

IMAGE_SIZE = (224, 224)

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Load & preprocess image
img = image.load_img(IMAGE_PATH, target_size=IMAGE_SIZE)
img_array = image.img_to_array(img)
img_array = img_array / 255.0
img_array = np.expand_dims(img_array, axis=0)

# Predict
prediction = model.predict(img_array)
class_index = np.argmax(prediction)
confidence = np.max(prediction)

# Class labels (IMPORTANT – same order as training)
class_labels = {0: "Dengue Mosquito (Aedes)", 1: "Non-Dengue Mosquito"}

print("🦟 Prediction Result")
print("-------------------")
print("Class:", class_labels[class_index])
print("Confidence:", f"{confidence * 100:.2f}%")
