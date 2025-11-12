# 🧠 DengueX – Model Training and Evaluation

This directory contains all ML logic for training, tuning, and evaluating the **Dengue intent classifier**.

---

## 📂 Key Scripts

### ⚡ `train_intent_final.py`
- Final and best-performing model (Accuracy ≈ 92%).  
- Combines **word** (1–3 grams) + **character** (3–6 grams) TF-IDF.  
- Uses `LinearSVC` with class balancing and grid search (`C=[0.1, 1.0, 4.0]`).  
- Trained on `Dengue_chatbot_data_merged_labels.csv`.

### 💬 `predict_intent.py`
- Loads saved model + vectorizers.  
- Predicts the dengue intent for user queries in English or Roman Urdu.  
- Used for chatbot backend and testing.

### 📊 `eval_compare.py` / `eval_errors.py`
- Evaluate and compare model variants.  
- Generate confusion matrices and reports.

---

## 🧾 Outputs

### Saved Models
models/
├── svm_intent_v2.pkl
├── tfidf_word_v2.pkl
├── tfidf_char_v2.pkl

### Evaluation

---

## 🧠 Final Model Summary
| Component | Description |
|------------|-------------|
| Algorithm | Linear SVM (class_weight="balanced") |
| Features | Word + Char TF-IDF |
| Accuracy | **92.18%** |
| Language Support | English + Roman Urdu |
| Use Case | Dengue chatbot intent detection |

---
