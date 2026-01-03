import torch
import json
import random
import time
import pandas as pd
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch.nn.functional as F
from tqdm import tqdm

# --------------------
# Load model & tokenizer
# --------------------
with open("intent_label_map.json") as f:
    label_map = json.load(f)

id2intent = {v: k for k, v in label_map.items()}

tokenizer = DistilBertTokenizerFast.from_pretrained("dengue_intent_bert")
model = DistilBertForSequenceClassification.from_pretrained("dengue_intent_bert")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

CONFIDENCE_THRESHOLD = 0.60

# --------------------
# Question pools
# --------------------
DENGUE_QUESTIONS = [
    "what is dengue",
    "what are dengue symptoms",
    "early signs of dengue",
    "is dengue dangerous",
    "how dengue spreads",
    "how to prevent dengue",
    "dengue treatment",
    "dengue testing methods",
    "dengue fever recovery time",
    "severe dengue symptoms"
]

NON_DENGUE_QUESTIONS = [
    "what is diabetes",
    "how to treat malaria",
    "what is covid",
    "who is the prime minister",
    "how to cook rice",
    "best programming language",
    "what is cancer",
    "how to lose weight",
    "what is football",
    "tell me a joke"
]

MISSPELLINGS = ["dengu", "denge", "dangue", "denguee"]

# --------------------
# Question generator (20K)
# --------------------
def generate_questions(n=20000):
    questions = []

    for _ in range(n):
        r = random.random()

        if r < 0.6:
            q = random.choice(DENGUE_QUESTIONS)
            q_type = "dengue"

        elif r < 0.8:
            q = random.choice(DENGUE_QUESTIONS)
            q = q.replace("dengue", random.choice(MISSPELLINGS))
            q_type = "misspelling"

        else:
            q = random.choice(NON_DENGUE_QUESTIONS)
            q_type = "non_dengue"

        questions.append((q, q_type))

    return questions

# --------------------
# Inference function
# --------------------
def predict_intent(text):
    encoding = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=48
    )

    start = time.time()

    with torch.no_grad():
        outputs = model(
            input_ids=encoding["input_ids"].to(device),
            attention_mask=encoding["attention_mask"].to(device)
        )

    probs = F.softmax(outputs.logits, dim=1)
    confidence, pred = torch.max(probs, dim=1)

    latency = time.time() - start

    intent = id2intent[pred.item()]
    confidence = confidence.item()

    if confidence < CONFIDENCE_THRESHOLD:
        return "fallback", confidence, latency

    return intent, confidence, latency

# --------------------
# Run 20K stress test
# --------------------
def run_test():
    questions = generate_questions(20000)
    results = []

    print("Running 20,000-question automated stress test...\n")

    for q, q_type in tqdm(questions):
        intent, confidence, latency = predict_intent(q)

        results.append({
            "question": q,
            "question_type": q_type,
            "predicted_intent": intent,
            "confidence": round(confidence, 3),
            "response_time_sec": round(latency, 3)
        })

    df = pd.DataFrame(results)

    # ✅ FINAL REQUIRED FILENAME
    df.to_csv("chatbot_20k_stress_test_results.csv", index=False)

    print("\nStress test completed.")
    print("Total questions:", len(df))
    print("\nIntent distribution:\n")
    print(df["predicted_intent"].value_counts())

    print("\nQuestion type distribution:\n")
    print(df["question_type"].value_counts())

    print("\nAverage response time:",
          round(df["response_time_sec"].mean(), 3), "seconds")

if __name__ == "__main__":
    run_test()
