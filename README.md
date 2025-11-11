# DengueX – AI-Powered Dengue Information & Forecasting System

DengueX is a Final Year Project (FYP) that provides three core modules:

## 1. Dengue Chatbot (English + Roman Urdu)
A medical-grade Q&A chatbot using:
- Custom dataset (900+ curated Q&A)
- TF-IDF Vectorizer + SVM baseline
- Spell handling and irrelevant query rejection
- Bilingual response engine (English & Roman Urdu)

## 2. Dengue Forecast Dashboard
Data visualization & trends for Pakistan-based dengue cases.

## 3. Mosquito Breeding Report System
User-submitted reports, images, and geolocation mapping.

---

# Project Structure

data/raw → Raw collected datasets
data/processed → Clean, validated, model-ready data
src/preprocessing → Preprocessing scripts
src/model → Training scripts & saved models


# Current Progress (Milestones)
✅ Step 1: Dataset creation (900 Q&A)  
✅ Step 2: Text preprocessing pipeline  
✅ Step 3: Train/Test split  
⬜ Step 4: TF-IDF + SVM model  
⬜ Step 5: Save .pkl model + inference script  
⬜ Step 6: Web chatbot UI  
⬜ Step 7: Backend API  
⬜ Step 8: Testing & deployment

---

# How to Run Preprocessing
python src/preprocessing/prepare_dataset.py
python src/preprocessing/train_test_split.py


---

# Tech Stack
- Python
- Scikit-learn (TF-IDF, SVM)
- Pandas
- Matplotlib / Plotly (forecast dashboard)
- Flask / FastAPI (backend)
- React or Streamlit (frontend)

---

# Author
Final Year Project – DengueX (2025)

