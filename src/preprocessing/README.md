# src/preprocessing

This directory contains all data-preparation logic for DengueX.

## Scripts

### preprocess_text.py
- Normalizes text  
- Lowercasing  
- Removes punctuation  
- Removes extra spaces  
- Safe for medical text (no stemming/lemmatization)

### prepare_dataset.py
- Loads cleaned dataset  
- Applies preprocessing  
- Generates combined English+Roman Urdu field  
- Saves model-ready file

### train_test_split.py
- Splits dataset into train/test  
- 80/20 split  
- Shuffle enabled  
- No stratification (IDs are unique)

## Purpose
All scripts here ensure the dataset is standardized and ready for TF-IDF + SVM training.
