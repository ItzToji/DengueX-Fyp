import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix

# 🔴 PATHS
DATASET_PATH = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_split"
MODEL_PATH = r"dengue_mosquito_model.h5"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Test data generator (NO augmentation)
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    DATASET_PATH + r"\test",
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)

# Evaluate model
loss, accuracy = model.evaluate(test_generator)
print(f"\n✅ Test Accuracy: {accuracy * 100:.2f}%")

# Predictions
y_pred = model.predict(test_generator)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = test_generator.classes

# Confusion matrix
cm = confusion_matrix(y_true, y_pred_classes)
print("\nConfusion Matrix:\n", cm)

# Classification report
print("\nClassification Report:\n")
print(classification_report(
    y_true,
    y_pred_classes,
    target_names=test_generator.class_indices.keys()
))
