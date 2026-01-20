import os
import re
import pdfplumber
import nltk
import pytesseract
from pdf2image import convert_from_path
from nltk.tokenize import sent_tokenize, word_tokenize

# =========================
# NLTK SETUP
# =========================
nltk.download("punkt")

# =========================
# CONFIG
# =========================
RAW_DIR = "chatbot_dataset/raw_sources"
CLEAN_DIR = "chatbot_dataset/processed/cleaned_text"
CHUNK_DIR = "chatbot_dataset/processed/chunks"

MIN_WORDS = 80
MAX_WORDS = 200

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

# =========================
# SAFETY FILTERS (CORRECT)
# =========================
UNSAFE_PATTERNS = [
    r"\bparacetamol\b",
    r"\bacetaminophen\b",
    r"\bibuprofen\b",
    r"\bdisprin\b",
    r"\baspirin\b",
    r"\b\d+\s*mg\b",
    r"\bcbc\b",
    r"\bplatelet count\b",
    r"\bvaccine\b",
    r"\bvaccination\b",
]

def is_safe_sentence(sentence: str) -> bool:
    sentence = sentence.lower()
    return not any(re.search(p, sentence) for p in UNSAFE_PATTERNS)

# =========================
# PDF TEXT EXTRACTION (TEXT + OCR)
# =========================
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    # 1️⃣ Try normal text extraction
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass

    # 2️⃣ OCR fallback for image-based PDFs
    if len(text.strip()) < 50:
        try:
            images = convert_from_path(pdf_path, dpi=300)
            for img in images:
                text += pytesseract.image_to_string(img)
        except Exception:
            pass

    return text

# =========================
# CLEAN TEXT
# =========================
def clean_text(raw_text: str) -> str:
    sentences = sent_tokenize(raw_text)
    safe_sentences = [s for s in sentences if is_safe_sentence(s)]
    cleaned = " ".join(safe_sentences)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

# =========================
# CHUNKING (FIXED)
# =========================
def chunk_text(text: str):
    words = word_tokenize(text)
    chunks = []
    start = 0

    while start < len(words):
        end = start + MAX_WORDS
        chunk_words = words[start:end]

        if len(chunk_words) < MIN_WORDS:
            break

        chunks.append(" ".join(chunk_words))
        start = end

    return chunks

# =========================
# MAIN PIPELINE (FIXED)
# =========================
def process_all_pdfs():
    merged_text = ""

    for root, _, files in os.walk(RAW_DIR):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, file)
            print(f"Processing: {pdf_path}")

            raw_text = extract_text_from_pdf(pdf_path)
            cleaned = clean_text(raw_text)

            if len(cleaned) < 50:
                continue  # skip junk OCR

            # Save cleaned text per file (debugging)
            clean_path = os.path.join(
                CLEAN_DIR, file.replace(".pdf", "_cleaned.txt")
            )
            with open(clean_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            merged_text += " " + cleaned

    # 🔥 CHUNK AFTER MERGING ALL TEXT
    chunks = chunk_text(merged_text)

    for i, chunk in enumerate(chunks):
        with open(os.path.join(CHUNK_DIR, f"chunk_{i}.txt"), "w", encoding="utf-8") as f:
            f.write(chunk)

    print("\nDONE")
    print(f"Total chunks created: {len(chunks)}")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    process_all_pdfs()
