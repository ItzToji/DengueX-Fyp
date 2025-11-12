# 🩸 DengueX – Source Code Overview

The `src/` directory contains all source code for the **DengueX AI Health System**, including preprocessing, model training, and evaluation.

---

## 📁 Directory Structure

src/
├── denguex/ # Core utilities (text cleaning, helpers)
├── models/ # Model training, tuning, and prediction
├── preprocessing/ # Dataset preparation and merging
└── README.md 

---

## ⚙️ Workflow Summary

| Step | Folder | Description |
|------|---------|-------------|
| Step 1–3 | `preprocessing/` | Clean and merge datasets |
| Step 4 | `models/` | Train TF-IDF + SVM intent classifier |
| Step 5 | `models/` | Save + evaluate model |
| Step 6 | Web integration (up next) |

---

## 🧾 Final Deliverables
- Dataset: `data/processed/Dengue_chatbot_data_merged_labels.csv`
- Model: `models/svm_intent_v2.pkl`
- Accuracy: **92.18%**
- Bilingual Support: ✅ English + Roman Urdu

---
