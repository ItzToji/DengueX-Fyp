import os

# Absolute import ensures Django can load it correctly
from chatbot.feature1_chatbot import chatbot_engine_final as engine


# Initialize index once
_initialized = False


def _ensure_initialized():
    global _initialized
    if not _initialized:
        index_dir = os.path.join(os.path.dirname(__file__), "index")

        try:
            engine.init_index(index_dir=index_dir)
            _initialized = True
        except Exception as e:
            print("ERROR initializing chatbot engine:", e)
            raise e


def chatbot_reply(question: str):
    _ensure_initialized()

    # engine.get_reply returns a dictionary
    response = engine.get_reply(question)

    # Ensure Django API always returns clean JSON
    return {
        "reply": response.get("reply", ""),
        "kb_id": response.get("kb_id"),
        "sources": response.get("sources", []),
        "urgency": response.get("urgency", "non-urgent"),
        "confidence": float(response.get("confidence", 0)),
        "matched_warning_signs": response.get("matched_warning_signs", [])
    }
