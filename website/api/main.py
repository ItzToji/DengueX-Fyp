# website/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback

app = FastAPI(title="DengueX Chatbot API")

class ChatRequest(BaseModel):
    text: str
    session_id: str = "anon"

# lazy init on first request to avoid startup delays
from feature1_chatbot.chatbot_engine import init_index, get_reply
INDEX_INITIALIZED = False

def ensure_index():
    global INDEX_INITIALIZED
    if not INDEX_INITIALIZED:
        try:
            init_index()  # will load feature1_chatbot/index by default
            INDEX_INITIALIZED = True
        except Exception as e:
            raise RuntimeError(f"Failed to load index: {e}")

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        ensure_index()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    try:
        res = get_reply(req.text)
        # Return a minimal safe payload for frontend
        return {
            "reply": res.get("reply", ""),
            "urgency": res.get("urgency","non-urgent"),
            "confidence": round(float(res.get("confidence",0.0)), 3)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status":"ok","note":"DengueX Chatbot API"}
