import re

# ==========================
# 1. DOMAIN GUARDRAIL (DENGUE ONLY)
# ==========================
DENGUE_KEYWORDS = [
    "dengue",
    "aedes",
    "mosquito",
    "aegypti",
    "albopictus",
    "fever",
    "viral fever",
    "stagnant water",
    "larvae",
    "outbreak",
    "vector",
]

# ==========================
# 2. MEDICAL SAFETY GUARDRAIL
# ==========================
MEDICAL_BLOCK_PATTERNS = [
    r"\bdiagnos",
    r"\btreat",
    r"\bmedicine",
    r"\bmedication",
    r"\btablet",
    r"\bdrug",
    r"\bprescrib",
    r"\btest result",
    r"\bcbc",
    r"\bplatelet",
    r"\bmg\b",
    r"\bam i infected",
    r"\bdo i have dengue",
    r"\bconfirm dengue",
    r"\bhow to cure",
    r"\bwhat should i take",
]

# ==========================
# 3. REFUSAL MESSAGES
# ==========================
DOMAIN_REFUSAL_MESSAGE = (
    "I can only answer questions related to dengue fever, "
    "its causes, symptoms, prevention, and public health awareness."
)

MEDICAL_REFUSAL_MESSAGE = (
    "I cannot provide medical diagnosis, treatment, or medication advice. "
    "Please consult a qualified healthcare professional or visit a government health facility."
)

# ==========================
# 4. GUARDRAIL FUNCTIONS
# ==========================
def is_dengue_related(text: str) -> bool:
    """
    Returns True if the query is related to dengue.
    """
    text = text.lower()
    return any(keyword in text for keyword in DENGUE_KEYWORDS)


def is_medically_unsafe(text: str) -> bool:
    """
    Returns True if the query asks for diagnosis or treatment.
    """
    text = text.lower()
    return any(re.search(pattern, text) for pattern in MEDICAL_BLOCK_PATTERNS)


def guardrail_check(text: str):
    """
    Returns (allowed: bool, message: str | None)
    """
    if not is_dengue_related(text):
        return False, DOMAIN_REFUSAL_MESSAGE

    if is_medically_unsafe(text):
        return False, MEDICAL_REFUSAL_MESSAGE

    return True, None
