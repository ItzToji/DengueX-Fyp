# DengueX Chatbot AI Module – Backend Integration Guide

This document explains **what the AI chatbot does**, **what it does NOT do**, and **how to integrate it into the backend**. This README is written for the **web/backend developer** responsible for Django integration.

---

## 1. What This Chatbot Is

The DengueX chatbot is a **controlled, AI-powered dengue awareness assistant** built using a **fine-tuned FLAN-T5 transformer model** combined with **rule-based safety and factual guardrails**.

It is **NOT** a generic chatbot and **NOT** a medical diagnostic system.

### Core Characteristics

* AI-powered (Transformer-based language model)
* Domain-restricted (answers dengue-related questions only)
* Safety-guarded (blocks diagnosis, treatment, medication)
* Public-health focused (awareness, causes, transmission, prevention)
* Short, clear answers (1–3 sentences)

This hybrid design ensures **accuracy, safety, and academic defensibility**.

---

## 2. What the Chatbot Can Answer

The chatbot is designed to answer **ONLY** the following categories:

* What is dengue fever
* How dengue spreads
* Which mosquito spreads dengue
* Mosquito breeding sites
* Environmental risk factors
* Seasonal patterns (monsoon, summer)
* Urban vs rural risk
* Community-level prevention and awareness
* Why dengue is a public health issue

All answers are **non-medical**, **non-diagnostic**, and **public-safe**.

---

## 3. What the Chatbot Will NOT Answer (By Design)

The chatbot will **politely refuse** to answer:

* Medical diagnosis ("Do I have dengue?")
* Treatment or cure
* Medicines or dosages
* Test interpretation (platelets, CBC, reports)
* Any non-dengue topic (e.g., malaria, diabetes, AI, politics)

Instead, it returns **user-friendly warning messages**.

---

## 4. AI Architecture (Important for Understanding)

The chatbot uses a **Hybrid AI Architecture**:

1. **Rule-based Guardrails**

   * Detect non-dengue questions
   * Detect medical/unsafe queries

2. **Canonical Knowledge Base (Hard Truths)**

   * Verified dengue facts (spread, mosquito, breeding, prevention)
   * These answers override the AI model to prevent hallucination

3. **Transformer Model (FLAN-T5)**

   * Used ONLY for safe, general awareness questions
   * Controlled decoding to avoid repetition and nonsense

This is **industry-standard for healthcare chatbots**.

---

## 5. Project Folder Structure (AI Side)

The backend developer needs **ONLY these files/folders**:

```
chatbot_ml/
│
├── chatbot_engine.py        # MAIN ENTRY POINT (call this)
│
├── model/
│   └── denguex_flan_t5_final/   # Trained transformer model
│
├── knowledge_base/
│   ├── canonical_answers.py     # Verified dengue facts
│   └── question_classifier.py   # Question routing logic
│
└── (test files - optional, not required for deployment)
```

⚠️ **Do NOT modify model files or retrain** during backend integration.

---

## 6. How to Integrate into Django Backend

### 6.1 Required Python Imports

In your Django app (e.g. `chatbot/views.py`):

```python
from chatbot_ml.chatbot_engine import chatbot_answer
```

Make sure `chatbot_ml` is in the Python path (same project root or added to `PYTHONPATH`).

---

### 6.2 Function to Call

The chatbot exposes **ONE function**:

```python
chatbot_answer(question: str) -> dict
```

### Returned JSON Format

```json
{
  "allowed": true,
  "answer": "Dengue spreads through the bite of an infected Aedes mosquito."
}
```

or (blocked case):

```json
{
  "allowed": false,
  "answer": "I cannot help with medical diagnosis or treatment..."
}
```

---

### 6.3 Example Django View

```python
def chatbot_api(request):
    user_question = request.POST.get("question")
    result = chatbot_answer(user_question)

    return JsonResponse({
        "response": result["answer"],
        "allowed": result["allowed"]
    })
```

Frontend should simply display `response` text.

---

## 7. Performance Notes

* Runs on **CPU** (GPU optional)
* First request may take ~2–3 seconds (model load)
* Subsequent responses are fast
* Safe for VPS deployment

---

## 8. Testing Status

The chatbot has been tested using:

* Controlled 14-question test
* Controlled 50-question test

Testing confirms:

* Correct handling of dengue facts
* Zero unsafe medical answers
* Correct blocking of non-dengue questions

---

## 9. Limitations (Intentional)

* Not a doctor
* Not a diagnostic tool
* Not a treatment advisor
* Knowledge limited to dengue awareness

These limitations are **intentional and required** for public deployment and academic ethics.

---

## 10. Summary for Integration

**Backend developer only needs to:**

1. Copy `chatbot_ml/` folder
2. Import `chatbot_answer()`
3. Expose an API endpoint
4. Display returned text

No ML knowledge required on backend side.

---

## 11. Contact / Notes

Any change to chatbot logic **must be discussed with AI module owner**.

The chatbot is **feature-complete and frozen** for FYP submission.
