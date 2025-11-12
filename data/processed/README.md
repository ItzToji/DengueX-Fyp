# 🧩 DengueX – Processed Data

This folder contains all cleaned, validated, and model-ready datasets.

---

## 📄 Files Overview

### 🧼 `Dengue_chatbot_data_clean.csv`
- Cleaned version of raw data (fixed malformed lines).  
- 899 total Q&A pairs with unique IDs.  
- Used as base for label merging.

### 🧭 `Dengue_chatbot_data_merged_labels.csv`
- Final dataset used for model training.  
- Contains mapped and consolidated intent labels.  
- Used in `train_intent_final.py`.

### 🧾 `label_map.json`
- JSON dictionary of all tag → label mappings used during preprocessing.

---

## 📊 Notes
- All files use UTF-8 encoding.  
- Every row has 8 consistent columns.  
- No missing or duplicate IDs.  
- Directly consumable by TF-IDF + SVM models (Steps 4–6).

---
