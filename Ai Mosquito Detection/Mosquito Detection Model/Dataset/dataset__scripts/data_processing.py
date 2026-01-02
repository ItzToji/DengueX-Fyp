from tensorflow.keras.preprocessing.image import ImageDataGenerator

# 🔴 PATH TO SPLIT DATASET
DATASET_PATH = r"E:\DengueX\Development and Data\Mosquito Detection Model\Dataset\mosquito_dataset_split"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

# 🔹 TRAINING DATA (with augmentation)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True
)

# 🔹 VALIDATION & TEST DATA (NO augmentation)
val_test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH + r"\train",
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_generator = val_test_datagen.flow_from_directory(
    DATASET_PATH + r"\val",
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

test_generator = val_test_datagen.flow_from_directory(
    DATASET_PATH + r"\test",
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)

print("✅ Data generators created successfully.")
print("Class labels:", train_generator.class_indices)
