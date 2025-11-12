import joblib
import os
from denguex.utils.text_cleaning import basic_clean

MODEL_DIR = "models"
VEC_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer_intent.pkl")
MODEL_PATH = os.path.join(MODEL_DIR, "svm_intent.pkl")

vectorizer = joblib.load(VEC_PATH)
model = joblib.load(MODEL_PATH)

def predict_intent(query: str):
    clean_q = basic_clean(query)
    X = vectorizer.transform([clean_q])
    pred = model.predict(X)[0]
    return pred

if __name__ == "__main__":
    test_queries = [
        "What are the symptoms of dengue?",
        "Kya dengue mein pani peena zaroori hai?",
        "Which medicine is safe for dengue?",
        "Can dengue affect pregnancy?",
        "How to prevent dengue at home?"
    ]
    for q in test_queries:
        print(f"{q} → {predict_intent(q)}")
