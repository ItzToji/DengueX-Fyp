import pandas as pd
from preprocess_text import normalize_text
import os

RAW_FILE = "data/processed/Dengue_chatbot_data_clean.csv"
OUT_DIR = "data/processed/model_ready"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Loading dataset: {RAW_FILE}")
    df = pd.read_csv(RAW_FILE)

    # Apply preprocessing to English + Roman Urdu questions
    df["question_en_clean"] = df["question_en"].apply(normalize_text)
    df["question_ru_clean"] = df["question_ru"].apply(normalize_text)

    # Combine English + Roman Urdu into a single field for training
    df["combined_question"] = (
        df["question_en_clean"].astype(str) + " " +
        df["question_ru_clean"].astype(str)
    ).str.strip()

    # Export cleaned dataset for ML pipeline
    out_file = f"{OUT_DIR}/dengue_questions_clean.csv"
    df.to_csv(out_file, index=False)

    print(f"✅ Preprocessed dataset saved to: {out_file}")
    print(f"Total rows: {len(df)}")
    print(df[["combined_question"]].head())


if __name__ == "__main__":
    main()
