"""Orchestration module that coordinates detection, redaction, policy, and auditing."""
from typing import Dict, Any
from .detectors import detect_prompt_injection, detect_jailbreak, detect_social_engineering
from .redactor import redact_sensitive
from .policy import PolicyEngine
from .auditor import Auditor
from .config import get_config


class Protector:
    def __init__(self, policy: PolicyEngine | None = None, auditor: Auditor | None = None):
        self.policy = policy or PolicyEngine()
        self.auditor = auditor or Auditor()
        from .detectors import scored_detection
        self.scored_detection = scored_detection
        self.config = get_config()
        self.scored_threshold = float(self.config.get("detector", {}).get("scored_threshold", 0.5))

    def protect(self, text: str, action: str | None = None) -> Dict[str, Any]:
        d_prompt = detect_prompt_injection(text)
        d_jail = detect_jailbreak(text)
        d_social = detect_social_engineering(text)
        scored = self.scored_detection(text)
        redacted_text, redacted_count = redact_sensitive(text)
        # incorporate scored detector into policy context
        context = {"detectors": [d_prompt, d_jail, d_social], "scored": scored, "action": action}
        # if scored exceeds threshold, mark as blocked in context for policy evaluation
        if isinstance(scored, dict) and scored.get("score", 0) >= self.scored_threshold:
            # attach a synthetic detector result indicating scored suspicion
            context["detectors"].append({"type": "scored", "matches": [], "blocked": True})

        decision = self.policy.evaluate(context)
        event = {
            "text": text,
            "detectors": [d_prompt, d_jail, d_social],
            "redacted_count": redacted_count,
            "scored": scored,
            "decision": decision,
        }
        self.auditor.record(event)
        return {"decision": decision, "redacted_text": redacted_text, "redacted_count": redacted_count}
