# Feature1 Chatbot (DengueX)
Location: src/feature1_chatbot/

## What is included
- `dengue_kb_seed_50.jsonl` : initial knowledge base (50 entries)
- `chatbot_engine.py` : simple chatbot module (load_kb, get_reply, etc.)
- `example_run.py` : interactive demo to run locally
- `tests/` : basic unit tests
- `requirements.txt` : minimal dependencies

## How to run locally
1. Create a Python virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\\Scripts\\activate on Windows
   pip install -r src/feature1_chatbot/requirements.txt
   ```
2. Run the interactive demo:
   ```bash
   python src/feature1_chatbot/example_run.py
   ```
3. Run tests (from repo root):
   ```bash
   pip install pytest
   pytest -q
   ```

## Next steps (recommended)
- Review and edit KB entries as needed.
- Tune vectorizer and thresholds for higher accuracy.
- Optionally replace TF-IDF with sentence-transformer embeddings for better semantic matching.
