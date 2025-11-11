import pandas as pd
from sklearn.model_selection import train_test_split
import os

IN_FILE = "data/processed/model_ready/dengue_questions_clean.csv"
OUT_DIR = "data/processed/model_ready"


def main():
    print("Loading:", IN_FILE)
    df = pd.read_csv(IN_FILE)

    # Ensure required column exists
    if "combined_question" not in df.columns:
        raise ValueError("combined_question column missing. Run preprocessing first.")

    # The classifier will map questions → best-matching id
    X = df["combined_question"]
    y = df["id"]

    # 80/20 split (recommended for small medical datasets)
    X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    shuffle=True
)


    # Save splits
    os.makedirs(OUT_DIR, exist_ok=True)

    train_df = pd.DataFrame({"question": X_train, "id": y_train})
    test_df = pd.DataFrame({"question": X_test, "id": y_test})

    train_df.to_csv(f"{OUT_DIR}/train.csv", index=False)
    test_df.to_csv(f"{OUT_DIR}/test.csv", index=False)

    print("✅ Train/Test split completed")
    print("Training samples:", len(train_df))
    print("Test samples:", len(test_df))
    print("Saved to:")
    print(" -", OUT_DIR + "/train.csv")
    print(" -", OUT_DIR + "/test.csv")


if __name__ == "__main__":
    main()
