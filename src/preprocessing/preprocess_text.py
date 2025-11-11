import re
import string

PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def normalize_text(text: str) -> str:
    """
    Simple, medically-safe preprocessing for dengue questions.
    - Lowercase
    - Remove punctuation
    - Remove extra spaces
    - Keep stopwords (important for intent)
    - Do NOT stem/lemmatize
    """

    if not isinstance(text, str):
        return ""

    # lowercase
    text = text.lower()

    # remove punctuation
    text = text.translate(PUNCT_TABLE)

    # remove multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
