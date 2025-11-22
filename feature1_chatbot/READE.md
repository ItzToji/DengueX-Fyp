🦠 DengueX — Feature 1
AI-Powered Dengue Medical Chatbot (FAISS + Embeddings + API)

This project contains the full implementation of Feature 1 of DengueX:
A medical-safe, high-accuracy dengue chatbot powered by:

Sentence-Transformers embeddings

FAISS vector search

Typo correction + semantic fallback

15,000-entry dengue knowledge base (KB)

FastAPI backend with review logging & auto-fix pipeline

This README explains how to run, test, and deploy the chatbot from any machine.

📁 Project Structure
DengueX/
│
├── feature1_chatbot/
│   ├── chatbot_engine.py               # Main RAG engine
│   ├── dengue_kb_seed_15000_extended.jsonl   # Final KB (15k items)
│   ├── index/                          # FAISS index + embeddings
│   │     ├── embeddings.npy
│   │     ├── index.faiss
│   │     ├── meta.jsonl
│   │     └── model_name.txt
│   └── scripts/
│         ├── build_embeddings_variants.py
│         ├── apply_review_fixes.py
│         └── view_review.py
│
└── requirements.txt

⚙️ Installation
1. Create virtual environment
python -m venv venv

2. Activate it

Windows

venv\Scripts\activate


Mac/Linux

source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

🚀 Running the Chatbot API

From project root (DengueX/):

python -m uvicorn website.api.main:app --reload --port 8000


API will run at:

👉 http://127.0.0.1:8000/chat

💬 How to query the chatbot (test)

Send a POST request:

curl -X POST "http://127.0.0.1:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"what are dengue symptoms?\", \"session_id\":\"test123\"}"


The bot will reply:

Dengue-related answer → high-accuracy canonical answer

Non-dengue question →
“Please ask dengue-related questions only…”

🧠 About the AI Engine

The chatbot engine includes:

✔ FAISS vector search

1 vector per question variant

Aggregation across all variants

Typo-correction & hybrid search

✔ Strict dengue-only enforcement

All off-topic questions receive safe declines

AI never hallucinates medical info

✔ Urgency detection

Recognizes WHO warning signs such as:
“persistent vomiting”, “abdominal pain”, “vomit blood”, etc.

Returns emergency instructions immediately.

✔ 99%+ accuracy on curated tests

After KB cleaning + semantic fallback + typo correction.

🧪 Testing (Full & Fast Modes)
Full 15,000-query test
python feature1_chatbot/tests/test_full_kb.py \
  --kb feature1_chatbot/dengue_kb_seed_15000_extended.jsonl \
  --index-dir feature1_chatbot/index \
  --out full_failures_15000.csv

Output includes:

Total passed

Total failed

Accuracy

Failures CSV

🛠 Review System (Human-in-the-loop)

Every low-confidence or off-topic query is logged automatically in:

feature1_chatbot/review_queue.csv

View pending reviews:
python feature1_chatbot/scripts/view_review.py

Apply approved fixes into the KB:
python feature1_chatbot/scripts/apply_review_fixes.py

🔁 Updating the KB

Whenever the KB file changes, regenerate the index:

python feature1_chatbot/scripts/build_embeddings_variants.py \
  --kb feature1_chatbot/dengue_kb_seed_15000_extended.jsonl \
  --index-dir feature1_chatbot/index \
  --model all-MiniLM-L6-v2