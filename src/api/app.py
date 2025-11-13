import os
import joblib
import traceback
from flask import Flask, request, jsonify
from src.denguex.utils.text_cleaning import basic_clean


# Initialize Flask
app = Flask(__name__)

# Load models
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MODEL_DIR = os.path.join(ROOT, "models")

word_vec = joblib.load(os.path.join(MODEL_DIR, "tfidf_word_v2.pkl"))
char_vec = joblib.load(os.path.join(MODEL_DIR, "tfidf_char_v2.pkl"))
model = joblib.load(os.path.join(MODEL_DIR, "svm_intent_v2.pkl"))

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        text = data.get("query", "")
        if not text:
            return jsonify({"error": "No query provided"}), 400

        clean_text = basic_clean(text)
        # Combine vectorizer outputs
        X_word = word_vec.transform([clean_text])
        X_char = char_vec.transform([clean_text])
        from scipy.sparse import hstack
        X = hstack([X_word, X_char])
        pred = model.predict(X)[0]
        return jsonify({"intent": pred})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DengueX API is running 🚀"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
