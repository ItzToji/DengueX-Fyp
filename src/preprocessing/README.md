# 🧩 DengueX – Preprocessing Module

This directory contains all data-preparation logic for **DengueX**, ensuring clean, consistent, and model-ready datasets for TF-IDF + SVM training.

---

## 📄 Scripts Overview

### 🧠 `process_text.py`
- Handles text normalization and cleaning.  
- Converts text to lowercase.  
- Removes punctuation and redundant spaces.  
- Designed for bilingual text (English + Roman Urdu).  
- Keeps medical terms intact (no stemming or lemmatization).

### 🧰 `prepare_dataset.py`
- Loads the cleaned CSV.  
- Combines English and Roman Urdu questions into one unified field.  
- Applies preprocessing using `process_text.py`.  
- Outputs model-ready data for training.

### 🔀 `train_test_split.py`
- Splits the model-ready dataset into **train** and **test** sets (80/20).  
- Ensures reproducibility via `random_state`.  
- Supports future stratified splits if needed.

### 🧭 `merge_label_map.py`
- Maps fine-grained `tags` to consolidated **intent labels** (e.g., `labs` → `laboratory`).  
- Collapses rare labels into `other` to improve model balance.  
- Outputs:
  - `Dengue_chatbot_data_merged_labels.csv`
  - `label_map.json`

---

## 🎯 Purpose
All scripts here ensure the **dataset is standardized, balanced, and merged into consistent intent labels**, ready for feature extraction and model training (Step 4).

---
