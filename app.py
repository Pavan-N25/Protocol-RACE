"""Minimal FastAPI app exposing Protocol-RACE endpoints."""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from protocol_race.detectors import detect_prompt_injection, detect_jailbreak, detect_social_engineering
from protocol_race.redactor import redact_sensitive
from protocol_race.policy import PolicyEngine
from protocol_race.auditor import Auditor
from protocol_race.protector import Protector
from protocol_race.config import get_config
from fastapi.responses import PlainTextResponse

logging.basicConfig(level=logging.INFO)
cfg = get_config()

app = FastAPI(title="Protocol-RACE")
auditor = Auditor()
policy = PolicyEngine()
protector = Protector(policy=policy, auditor=auditor)


class InspectRequest(BaseModel):
    text: str
    action: str | None = None


@app.post("/inspect")
def inspect(req: InspectRequest):
    return protector.protect(req.text, action=req.action)


@app.get("/audit")
def get_audit():
    return {"events": auditor.get_events()}


@app.get("/metrics")
def metrics():
    # prefer returning Prometheus exposition text when available
    m = auditor.get_metrics()
    prom = m.get("prometheus")
    if prom:
        return PlainTextResponse(prom)
    lines = []
    lines.append(f"protocol_race_events_total {m.get('events_total',0)}")
    lines.append(f"protocol_race_events_blocked {m.get('blocked',0)}")
    return PlainTextResponse("\n".join(lines))
