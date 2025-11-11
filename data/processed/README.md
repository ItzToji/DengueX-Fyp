
# data/processed

Contains cleaned, validated, and model-ready datasets.

## Files

### 1. Dengue_chatbot_data_clean.csv
- Cleaned version of raw dataset  
- Fixed malformed rows  
- Correct 8-column structure  
- 899 total Q&A pairs  
- Unique IDs only  

### 2. model_ready/dengue_questions_clean.csv
- Preprocessed questions  
- Contains `combined_question` used for TF-IDF training  

### 3. model_ready/train.csv / test.csv
- Train–test split (80/20)
- Used for model training & evaluation

## Notes
These files should be used for ML steps 4–6.
