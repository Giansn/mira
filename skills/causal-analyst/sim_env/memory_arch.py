#!/usr/bin/env python3
"""Memory Architecture — stream, reflection, planning stubs."""
import json, hashlib, os

AUDIT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'audit_trail.jsonl')
MEMORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'memory_log.jsonl')
INSIGHTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'insights.jsonl')

def _ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def append_audit(run):
    """Append a Run to the audit trail (memory stream)."""
    _ensure_dir(AUDIT_PATH)
    with open(AUDIT_PATH, 'a') as f:
        f.write(json.dumps(run, sort_keys=True) + '\n')

def append_memory(run):
    """Append a redacted record to the memory log."""
    _ensure_dir(MEMORY_PATH)
    redacted = {
        "schema_version": run.get("schema_version", "v1.0"),
        "run_id": run.get("run_id"),
        "timestamp": run.get("timestamp"),
        "seed_hash": hashlib.sha256(str(run.get("seed", "")).encode()).hexdigest(),
        "command_hash": hashlib.sha256(run.get("command", "").encode()).hexdigest(),
        "command_preview": run["command"][:32] if run.get("tier") == "SAFE" else None,
        "tier": run.get("tier"),
        "decision": run.get("decision"),
        "status": run.get("status"),
        "mirror": {
            "risk_flags": run.get("mirror_trace", {}).get("risk_flags", []),
            "confidence": run.get("mirror_trace", {}).get("confidence", 0),
            "reasoning_trunc": run.get("mirror_trace", {}).get("reasoning", "")[:200]
        },
        "audit_hash": run.get("hash")
    }
    with open(MEMORY_PATH, 'a') as f:
        f.write(json.dumps(redacted, sort_keys=True) + '\n')

def reflect(runs, window=50):
    """Batch reflection over recent runs. Returns Insight objects."""
    recent = runs[-window:]
    if not recent:
        return []
    # Simple heuristic reflection
    total = len(recent)
    blocked = sum(1 for r in recent if r.get("status") == "blocked")
    denied = sum(1 for r in recent if r.get("status") == "denied")
    low_conf = sum(1 for r in recent if r.get("mirror_trace", {}).get("confidence", 1) < 0.5)
    insights = []
    if blocked / max(total, 1) > 0.4:
        insights.append({"type": "observation", "summary": f"High block rate ({blocked}/{total}). Tier map may be too aggressive.", "recommendation": "Review BLOCKED tier entries."})
    if denied / max(total, 1) > 0.3:
        insights.append({"type": "observation", "summary": f"High deny rate ({denied}/{total}). Policy rules may be too strict.", "recommendation": "Review SENSITIVE policy rules."})
    if low_conf > 0:
        insights.append({"type": "warning", "summary": f"{low_conf} runs with mirror confidence < 0.5.", "recommendation": "Flag for human review."})
    return insights

def save_insights(insights):
    """Persist insights to insights.jsonl."""
    _ensure_dir(INSIGHTS_PATH)
    with open(INSIGHTS_PATH, 'a') as f:
        for ins in insights:
            f.write(json.dumps(ins, sort_keys=True) + '\n')
