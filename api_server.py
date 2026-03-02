#!/usr/bin/env python3
"""
FastAPI MVP bridge for TelClaw v0.3
- PolicyEngine + Gate + Executor
- In-memory approvals (ephemeral)
- AEAP toggle, offline_free_pass, optional metrics
- Endpoints: /api/commands, /api/approvals, /api/commands/{id}, /api/config, /api/metrics, /metrics-ui
"""

import json
import os
import sys
import time
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

BASE = os.path.dirname(os.path.abspath(__file__))
SKILLS_PATH = os.path.join(BASE, "skills")
if SKILLS_PATH not in sys.path:
    sys.path.insert(0, SKILLS_PATH)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from telclaw.policy_engine import PolicyEngine
from telclaw.gate import Gate
from telclaw.executor import Executor

CONFIG_PATH = os.path.join(BASE, "config", "api_config.json")

def load_cfg() -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "api_key": "changeme-please-set",
            "mock_mode": True,
            "offline_load": True,
            "offline_free_pass": True,
            "aeap": False,
            "metrics_enabled": False,
            "allowed_commands": ["status", "sts", "restart", "reset", "config"],
            "thresholds": {"safe_max": 3},
        }

cfg = load_cfg()

API_KEY = cfg.get("api_key", "changeme-please-set")
SAFE_MAX = int(cfg.get("thresholds", {}).get("safe_max", 3))
AEAP = bool(cfg.get("aeap", False))
OFFLINE_FREE_PASS = bool(cfg.get("offline_load", False)) and bool(cfg.get("offline_free_pass", False))
METRICS_ON = bool(cfg.get("metrics_enabled", False))

# Optional metrics
api_metrics = None
if METRICS_ON:
    from telclaw_utils.metrics import APIUsageMetrics
    api_metrics = APIUsageMetrics()

# TelClaw core
policy = PolicyEngine(safe_max=SAFE_MAX, mock_mode=bool(cfg.get("mock_mode", True)))
gate = Gate()
executor = Executor()

# In-memory stores
commands_store: Dict[str, Dict[str, Any]] = {}
approvals_store: Dict[str, Dict[str, Any]] = {}

# Deterministic risk overrides
GATED_COMMANDS = {
    "config": 6, "restart": 6, "reboot": 10, "reset": 8,
    "stop": 6, "kill": 9, "shell": 9, "update": 7,
}

app = FastAPI(title="TelClaw API MVP", version="0.3")

# --- Helpers ---

def require_key(x_api_key: Optional[str]) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def require_allowed(cmd: str) -> None:
    allowed = cfg.get("allowed_commands", [])
    if allowed and cmd not in allowed:
        raise HTTPException(status_code=403, detail=f"Command not allowed: {cmd}")

def _record(t0: float, success: bool):
    if METRICS_ON and api_metrics:
        api_metrics.record_request(t0, success)

# --- Models ---

class CommandIn(BaseModel):
    user_id: str
    command: str
    args: Dict[str, Any] = {}
    source: Optional[str] = None

class CommandOut(BaseModel):
    command_id: str
    risk: int
    computed_risk: int  # Actual risk before AEAP override
    status: str
    requires_approval: bool
    message: str

class ApproveIn(BaseModel):
    command_id: str
    approver_id: str
    decision: str
    rationale: Optional[str] = None

class ConfigOut(BaseModel):
    mock_mode: bool
    aeap: bool
    offline_free_pass: bool
    metrics_enabled: bool
    allowed_commands: list
    thresholds: dict

# --- Endpoints ---

@app.post("/api/commands", response_model=CommandOut)
async def create_command(cmd: CommandIn, x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    t0 = time.time()
    command = cmd.command.strip().lstrip("/").lower()
    require_allowed(command)

    # Risk classification
    computed_risk = policy.classify(command, cmd.args)
    if command in GATED_COMMANDS:
        computed_risk = GATED_COMMANDS[command]

    # AEAP: force all commands through gate (takes precedence over offline_free_pass)
    # But preserve the actual computed risk for logging/audit
    requires_approval = AEAP
    risk = computed_risk  # Start with computed risk
    if requires_approval:
        risk = max(risk, SAFE_MAX + 1)
    # Offline free pass: override risk to 0 (only if AEAP is off)
    elif OFFLINE_FREE_PASS:
        risk = 0

    cid = str(uuid.uuid4())
    record = {
        "command_id": cid,
        "user_id": cmd.user_id,
        "command": command,
        "args": cmd.args,
        "source": cmd.source,
        "risk": risk,
        "status": None,
        "result": None,
    }

    # Safe path: auto-exec
    if risk <= SAFE_MAX:
        result = executor.execute(command, cmd.args, simulated=True)
        record["status"] = "executed"
        record["result"] = result
        commands_store[cid] = record
        _record(t0, True)
        return CommandOut(
            command_id=cid,
            risk=risk,
            computed_risk=computed_risk,
            status="executed",
            requires_approval=False,
            message="executed (safe, simulated)",
        )

    # Gated path: pending approval
    record["status"] = "pending_approval"
    commands_store[cid] = record
    approvals_store[cid] = {
        "command_id": cid,
        "status": "pending",
        "risk": risk,
        "command": command,
        "args": cmd.args,
        "requested_by": cmd.user_id,
        "approver_id": None,
        "decision": None,
        "rationale": None,
    }
    _record(t0, False)
    return CommandOut(
        command_id=cid,
        risk=risk,
        computed_risk=computed_risk,
        status="pending_approval",
        requires_approval=True,
        message="approval required",
    )

@app.post("/api/approvals")
async def approve(appr: ApproveIn, x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    t0 = time.time()

    entry = approvals_store.get(appr.command_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Approval not found")

    decision = appr.decision.strip().upper()
    if decision not in ("Y", "N"):
        raise HTTPException(status_code=400, detail="decision must be Y or N")

    entry["approver_id"] = appr.approver_id
    entry["decision"] = decision
    entry["rationale"] = appr.rationale

    if decision == "N":
        entry["status"] = "denied"
        commands_store[appr.command_id]["status"] = "denied"
        _record(t0, False)
        return {"status": "denied"}

    entry["status"] = "approved"
    cmdrec = commands_store[appr.command_id]
    result = executor.execute(entry["command"], entry["args"], simulated=True)
    cmdrec["status"] = "executed"
    cmdrec["result"] = result
    _record(t0, True)
    return {"status": "approved", "execution_result": result}

@app.get("/api/commands/{command_id}")
async def get_command(command_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    rec = commands_store.get(command_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Command not found")
    return rec

@app.get("/api/config", response_model=ConfigOut)
async def get_config(x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    return ConfigOut(
        mock_mode=bool(cfg.get("mock_mode", True)),
        aeap=AEAP,
        offline_free_pass=OFFLINE_FREE_PASS,
        metrics_enabled=METRICS_ON,
        allowed_commands=cfg.get("allowed_commands", []),
        thresholds=cfg.get("thresholds", {"safe_max": SAFE_MAX}),
    )

@app.get("/api/metrics")
async def get_metrics(x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    if not METRICS_ON or not api_metrics:
        return {"status": "disabled", "message": "Metrics collection is off in offline mode"}
    return api_metrics.get_metrics()

@app.post("/api/metrics/reset")
async def reset_metrics(x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    if not METRICS_ON or not api_metrics:
        return {"status": "disabled"}
    api_metrics.reset()
    return {"status": "metrics reset"}

@app.get("/metrics-ui", response_class=HTMLResponse)
async def metrics_ui(x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    if not METRICS_ON or not api_metrics:
        return HTMLResponse(content="<html><body><h2>Metrics disabled in offline mode</h2></body></html>")
    m = api_metrics.get_metrics()
    html = f"""<html>
<head><title>TelClaw Metrics</title>
<style>body{{font-family:monospace;padding:16px}}table{{border-collapse:collapse;width:100%;max-width:600px}}td,th{{border:1px solid #ddd;padding:6px}}th{{background:#f4f4f4}}</style>
<meta http-equiv="refresh" content="30"></head>
<body>
<h2>TelClaw API Metrics</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Total requests</td><td>{m['total_requests']}</td></tr>
<tr><td>Success rate</td><td>{m['success_rate_percent']:.1f}%</td></tr>
<tr><td>Error rate</td><td>{m['error_rate_percent']:.1f}%</td></tr>
<tr><td>Avg latency</td><td>{m['avg_response_time_ms']:.1f}ms</td></tr>
<tr><td>P95 latency</td><td>{m['p95_response_time_ms']:.1f}ms</td></tr>
<tr><td>Tokens in</td><td>{m['total_tokens_in']}</td></tr>
<tr><td>Tokens out</td><td>{m['total_tokens_out']}</td></tr>
<tr><td>Uptime</td><td>{m['total_session_time_sec']:.0f}s</td></tr>
</table>
<p><small>Auto-refresh: 30s</small></p>
</body></html>"""
    return HTMLResponse(content=html)
