"""Redact sensitive information before passing data to models or tools."""
import re
from typing import Tuple

SENSITIVE_PATTERNS = [
    re.compile(r"\b(?:api[_\-\s]?key|secret|password|passwd)\b", re.I),
    re.compile(r"AKIA[0-9A-Z]{8,20}"),  # AWS-like (more flexible)
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b\d{13,19}\b"),  # credit card (very naive)
]


def redact_sensitive(text: str) -> Tuple[str, int]:
    """Redact matches and return (redacted_text, count)."""
    count = 0
    redacted = text
    for p in SENSITIVE_PATTERNS:
        redacted, n = p.subn("[REDACTED]", redacted)
        count += n
    return redacted, count
