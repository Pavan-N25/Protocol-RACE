"""Simple detectors for prompt injection, jailbreaks, and social engineering."""
import re
from typing import List, Dict
from .detectors_ml import ScoredDetector

PROMPT_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(r"ignore (previous )?instructions", re.I),
    re.compile(r"disregard (previous )?instructions", re.I),
    re.compile(r"bypass (safety|filter)", re.I),
    re.compile(r"exfiltrate|steal|leak", re.I),
]

JAILBREAK_PATTERNS: List[re.Pattern] = [
    re.compile(r"jailbreak", re.I),
    re.compile(r"help me hack", re.I),
]

SOCIAL_ENGINEERING_PATTERNS: List[re.Pattern] = [
    re.compile(r"password|api[- ]?key|ssn|social security", re.I),
    re.compile(r"urgent|asap|right away", re.I),
]


def _match_any(text: str, patterns: List[re.Pattern]) -> List[str]:
    found = []
    for p in patterns:
        if p.search(text):
            found.append(p.pattern)
    return found


def detect_prompt_injection(text: str) -> Dict:
    matches = _match_any(text, PROMPT_INJECTION_PATTERNS)
    return {"type": "prompt_injection", "matches": matches, "blocked": bool(matches)}


def detect_jailbreak(text: str) -> Dict:
    matches = _match_any(text, JAILBREAK_PATTERNS)
    return {"type": "jailbreak", "matches": matches, "blocked": bool(matches)}


def detect_social_engineering(text: str) -> Dict:
    matches = _match_any(text, SOCIAL_ENGINEERING_PATTERNS)
    return {"type": "social_engineering", "matches": matches, "blocked": bool(matches)}


_scored = ScoredDetector()


def scored_detection(text: str) -> Dict:
    """Return scored detection result using ScoredDetector."""
    return _scored.evaluate(text)
