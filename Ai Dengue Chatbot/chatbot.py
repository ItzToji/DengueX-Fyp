import torch
import json
import time
import sys
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch.nn.functional as F

# --------------------
# Load intent label map
# --------------------
with open("intent_label_map.json", "r") as f:
    label_map = json.load(f)

id2intent = {v: k for k, v in label_map.items()}

# --------------------
# Load model & tokenizer
# --------------------
sys.stdout.write("Loading model...\n")
sys.stdout.flush()

tokenizer = DistilBertTokenizerFast.from_pretrained("dengue_intent_bert")
model = DistilBertForSequenceClassification.from_pretrained("dengue_intent_bert")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

sys.stdout.write("Model loaded successfully.\n")
sys.stdout.flush()

# --------------------
# Thresholds & keywords
# --------------------
CONFIDENCE_THRESHOLD = 0.60

EMERGENCY_KEYWORDS = [
    "severe", "bleeding", "blood", "hospital",
    "life threatening", "danger", "critical", "shock"
]

TESTING_KEYWORDS = [
    "test", "testing", "diagnose", "diagnosis", "ns1", "igm", "igg", "blood test"
]

PREVENTION_KEYWORDS = [
    "prevent", "prevention", "avoid", "protect", "control", "stop"
]

# --------------------
# Intent → Response mapping
# --------------------
RESPONSES = {
    "dengue_definition":
        "Dengue is a viral infection transmitted by Aedes mosquitoes. It commonly causes fever, headache, muscle and joint pain, and sometimes a rash.",

    "dengue_symptoms_common":
        "Common dengue symptoms include high fever, severe headache, pain behind the eyes, joint and muscle pain, nausea, vomiting, and skin rash.",

    "dengue_emergency":
        "WARNING: Severe dengue symptoms detected. Please seek immediate medical attention or visit the nearest hospital.",

    "dengue_prevention":
        "Dengue prevention includes eliminating standing water, using mosquito repellents, wearing long sleeves, and using mosquito nets.",

    "dengue_testing":
        "Dengue can be diagnosed through blood tests such as NS1 antigen tests and IgM/IgG antibody tests.",

    "dengue_treatment":
        "There is no specific antiviral treatment for dengue. Management includes adequate hydration, rest, and medical supervision.",

    "out_of_scope":
        "WARNING: Please ask dengue-related questions only. This chatbot is designed to provide dengue information."
}

# --------------------
# Inference function (PATCHED)
# --------------------
def chatbot_reply(user_input: str):
    text = user_input.lower()

    encoding = tokenizer(
        user_input,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=48
    )

    with torch.no_grad():
        outputs = model(
            input_ids=encoding["input_ids"].to(device),
            attention_mask=encoding["attention_mask"].to(device)
        )

    probs = F.softmax(outputs.logits, dim=1)
    confidence, pred = torch.max(probs, dim=1)

    confidence = confidence.item()
    intent = id2intent[pred.item()]

    # --------------------
    # Rule-based overrides (SAFE GUARDS)
    # --------------------
    if any(k in text for k in TESTING_KEYWORDS):
        intent = "dengue_testing"

    elif any(k in text for k in PREVENTION_KEYWORDS):
        intent = "dengue_prevention"

    elif intent == "dengue_emergency":
        # Emergency only if danger keywords exist
        if not any(k in text for k in EMERGENCY_KEYWORDS):
            intent = "dengue_definition"

    # --------------------
    # Confidence fallback
    # --------------------
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "intent": "fallback",
            "confidence": round(confidence, 3),
            "response": "WARNING: I am not confident in understanding your question. Please ask a clear dengue-related question."
        }

    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "response": RESPONSES.get(
            intent,
            "WARNING: Please ask dengue-related questions only."
        )
    }

# --------------------
# Warm-up (prevents first-call delay)
# --------------------
sys.stdout.write("Warming up model...\n")
sys.stdout.flush()
_ = chatbot_reply("what is dengue")
sys.stdout.write("Warm-up complete.\n\n")
sys.stdout.flush()

# --------------------
# CLI Chat Loop
# --------------------
sys.stdout.write("Dengue Chatbot (type 'exit' to quit)\n\n")
sys.stdout.flush()

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        sys.stdout.write("Exiting chatbot.\n")
        sys.stdout.flush()
        break

    sys.stdout.write("Processing...\n")
    sys.stdout.flush()

    start =  time.time()
    result = chatbot_reply(user_input)
    end = time.time()

    sys.stdout.write(f"Bot: {result['response']}\n")
    sys.stdout.write(f"Confidence: {result['confidence']}\n")
    sys.stdout.write(f"Response time: {round(end - start, 2)} seconds\n\n")
    sys.stdout.flush()
