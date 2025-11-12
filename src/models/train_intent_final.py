"""
Train intent SVM (v2) with combined word n-grams + char n-grams, class balancing,
and quick GridSearch for C. Saves vectorizer(s) + model.

Run from project root:
    # (ensure src is discoverable)
    export PYTHONPATH="$PWD/src"      # on Windows Git Bash: export too; or run with -m
    python -m src.models.train_intent_merged_v2
"""
import os
import joblib
import pandas as pd
from collections import Counter
from denguex.utils.text_cleaning import basic_clean
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer
from scipy.sparse import hstack

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_PATH = os.path.join(ROOT, "data", "processed", "Dengue_chatbot_data_augmented.csv")
MODEL_DIR = os.path.join(ROOT, "models")
os.makedirs(MODEL_DIR, exist_ok=True)
EVAL_DIR = os.path.join(MODEL_DIR, "eval")
os.makedirs(EVAL_DIR, exist_ok=True)

def load_df():
    df = pd.read_csv(DATA_PATH)
    # build a single text field combining English + Roman-Urdu questions
    df["text"] = (df["question_en"].fillna("") + " ||| " + df["question_ru"].fillna("")).apply(basic_clean)
    df["label"] = df["merged_label"]
    return df[["text", "label"]]

def build_vectorizers():
    # word n-grams (1..3)
    word = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1,3),
        max_features=15000,
        token_pattern=r"(?u)\b\w+\b",
        sublinear_tf=True
    )
    # char n-grams (char_wb tends to be good for short text / misspellings)
    char = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3,6),
        max_features=5000,
        sublinear_tf=True
    )
    return word, char

def main():
    df = load_df()
    print("Loaded rows:", len(df))
    print("Label distribution:", Counter(df["label"]))

    X = df["text"]
    y = df["label"]

    # stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

    # vectorizers
    word_vec, char_vec = build_vectorizers()
    X_train_word = word_vec.fit_transform(X_train)
    X_train_char = char_vec.fit_transform(X_train)
    X_test_word = word_vec.transform(X_test)
    X_test_char = char_vec.transform(X_test)

    # combine feature matrices
    X_train_comb = hstack([X_train_word, X_train_char])
    X_test_comb = hstack([X_test_word, X_test_char])

    # classifier with class balancing
    svc = LinearSVC(class_weight="balanced", max_iter=10000)

    # small grid for C
    param_grid = {"C": [0.1, 1.0, 4.0]}

    # 3-fold stratified CV
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    gs = GridSearchCV(svc, param_grid, cv=cv, n_jobs=-1, scoring="f1_weighted", verbose=1)

    print("Fitting GridSearchCV ...")
    gs.fit(X_train_comb, y_train)

    print("Best params:", gs.best_params_)

    # eval on test set
    y_pred = gs.predict(X_test_comb)
    acc = accuracy_score(y_test, y_pred)
    print("\nAccuracy:", acc)
    print("\nClassification report (test set):\n")
    print(classification_report(y_test, y_pred, digits=3))

    # save vectorizers + model
    joblib.dump(word_vec, os.path.join(MODEL_DIR, "tfidf_word_v2.pkl"))
    joblib.dump(char_vec, os.path.join(MODEL_DIR, "tfidf_char_v2.pkl"))
    joblib.dump(gs.best_estimator_, os.path.join(MODEL_DIR, "svm_intent_v2.pkl"))

    # save simple eval artifacts
    # confusion matrix CSV
    import numpy as np
    from sklearn.metrics import confusion_matrix
    labels = sorted(list(set(y_test)))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    import pandas as pd
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_df.to_csv(os.path.join(EVAL_DIR, "confusion_matrix_v2.csv"))
    print(f"\nSaved model + vectorizers to {MODEL_DIR} and eval to {EVAL_DIR}")

if __name__ == "__main__":
    main()
