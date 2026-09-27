"""Basic file analyzer for suspicious code or commands."""
import re
from typing import Dict

SUSPICIOUS_COMMANDS = [
    re.compile(r"rm\s+-rf", re.I),
    re.compile(r"curl .*sh\s*\|\s*sh", re.I),
    re.compile(r"nc\s+-e|netcat", re.I),
]


def analyze_file(content: str) -> Dict:
    matches = []
    for p in SUSPICIOUS_COMMANDS:
        if p.search(content):
            matches.append(p.pattern)
    return {"suspicious": bool(matches), "matches": matches}
