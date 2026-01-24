import re

# Hard medical blocks (intent-level, rule-enforced)
BLOCK_PATTERNS = [
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
]

REFUSAL_MESSAGE = (
    "I cannot provide medical diagnosis or treatment. "
    "For health-related concerns, please consult a qualified healthcare professional "
    "or visit a government health facility."
)

def is_blocked_query(text: str) -> bool:
    """
    Returns True if the query is medically unsafe.
    """
    text = text.lower()
    return any(re.search(pattern, text) for pattern in BLOCK_PATTERNS)
