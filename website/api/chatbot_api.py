# website/api/chatbot_api.py
import os
import logging
import csv
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from feature1_chatbot.chatbot_engine import init_index, get_reply

# Config
LOG_DIR = os.environ.get("CHATBOT_LOG_DIR", "logs")
REVIEW_FILE = os.environ.get("CHATBOT_REVIEW_FILE", "feature1_chatbot/review_queue.csv")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(REVIEW_FILE), exist_ok=True)

# Logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "queries.log"),
    level=logging.INFO,
    format="%(asctime)s\t%(levelname)s\t%(message)s",
)

app = FastAPI(title="DengueX Chatbot API", version="1.1")

# Load index at startup
INDEX_DIR = os.environ.get("CHATBOT_INDEX_DIR", "feature1_chatbot/index")
try:
    init_index(INDEX_DIR)
    logging.info(f"Loaded index from {INDEX_DIR}")
except Exception as e:
    logging.exception(f"Index load failed: {e}")

# Threshold to record to review queue
REVIEW_CONF_THRESHOLD = float(os.environ.get("CHATBOT_REVIEW_THRESHOLD", 0.45))

class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok"}

def append_review_row(session_id, query, kb_id, confidence, urgency, reply):
    header = ["timestamp","session_id","query","kb_id","confidence","urgency","reply","notes","reviewed_by","reviewed_at"]
    new_row = [datetime.utcnow().isoformat(), session_id or "-", query[:2000], kb_id or "-", f"{confidence:.3f}", urgency or "-", reply[:2000], "", "", ""]
    write_header = not os.path.exists(REVIEW_FILE)
    with open(REVIEW_FILE, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(new_row)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty query text")

    try:
        result = get_reply(req.text)
    except Exception:
        logging.exception("Error in get_reply")
        raise HTTPException(status_code=500, detail="Internal error")

    # Log query to queries.log
    logging.info(
        f"session={req.session_id or '-'}\tquery={req.text[:300]}\tkb_id={result.get('kb_id')}\tconfidence={result.get('confidence'):.3f}\turgency={result.get('urgency')}"
    )

    # Append to review queue if confidence is low or out_of_scope
    confidence = float(result.get("confidence", 0.0))
    tags = result.get("tags", []) if isinstance(result, dict) else []
    # If low confidence OR explicitly out_of_scope tag OR matched no KB
    if confidence < REVIEW_CONF_THRESHOLD or result.get("kb_id") is None or ("out_of_scope" in tags):
        try:
            append_review_row(req.session_id, req.text, result.get("kb_id"), confidence, result.get("urgency"), result.get("reply"))
        except Exception:
            logging.exception("Failed to append to review queue")

    # Return only the reply to client
    return {"reply": result.get("reply", "")}
