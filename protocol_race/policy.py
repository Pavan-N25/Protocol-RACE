"""A simple policy engine to allow/block actions and log rationale."""
from typing import Dict, Any


class PolicyEngine:
    def __init__(self, strict: bool = True):
        self.strict = strict
        from .config import get_config
        cfg = get_config()
        self.strict = bool(cfg.get("policy", {}).get("strict", self.strict))

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate policy for given context. Context may include 'detectors' and 'action'."""
        detectors = context.get("detectors", [])
        action = context.get("action", "unknown")
        blocked_reasons = []
        for d in detectors:
            if d.get("blocked"):
                blocked_reasons.append(d.get("type"))

        allowed = len(blocked_reasons) == 0 if self.strict else True
        return {"action": action, "allowed": allowed, "blocked_reasons": blocked_reasons}
