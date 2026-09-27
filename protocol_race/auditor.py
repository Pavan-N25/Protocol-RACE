"""Simple auditor to record events and decisions."""
import time
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)
try:
    from prometheus_client import Counter, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
    registry = CollectorRegistry()
    MET_EVENTS = Counter("protocol_race_events_total", "Total events", registry=registry)
    MET_BLOCKED = Counter("protocol_race_events_blocked", "Blocked events", registry=registry)
except Exception:
    PROMETHEUS_AVAILABLE = False
    MET_EVENTS = None
    MET_BLOCKED = None



class Auditor:
    def __init__(self):
        self.events: List[Dict] = []
        self.metrics: Dict[str, int] = {"events_total": 0, "blocked": 0}

    def record(self, event: Dict) -> None:
        event.setdefault("timestamp", time.time())
        self.events.append(event)
        self.metrics["events_total"] += 1
        decision = event.get("decision", {})
        if isinstance(decision, dict) and not decision.get("allowed", True):
            self.metrics["blocked"] += 1
        logger.info("Auditor recorded event: %s", {"summary": event.get("decision")})
        if PROMETHEUS_AVAILABLE:
            MET_EVENTS.inc()
            if isinstance(decision, dict) and not decision.get("allowed", True):
                MET_BLOCKED.inc()

    def get_events(self) -> List[Dict]:
        return list(self.events)

    def get_metrics(self) -> Dict[str, int]:
        out = dict(self.metrics)
        if PROMETHEUS_AVAILABLE:
            try:
                out["prometheus"] = generate_latest(registry).decode("utf-8")
            except Exception:
                out["prometheus"] = None
        return out
