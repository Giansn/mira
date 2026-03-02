#!/usr/bin/env python3
"""Risk Assessment for offline AEAP (Atlas) — audit-only, offline-deterministic with compact mode by default."""
import json
from typing import Optional, Dict

# Default thresholds (private, adjustable)
DEFAULT_THRESHOLDS = {
    "low": 0.0,
    "medium": 0.25,
    "high": 0.5,
    "critical": 0.75,
}

WEIGHTS = {
    "ESCALATE": 0.3,
    "REVIEW": 0.2,
    "SAFE_OVERRIDE": 0.1,
    "DATA_RISK": 0.25,
    "UNKNOWN_CMD": 0.2,
}


def _score_from_flags(flags: list) -> float:
    s = 0.0
    for f in flags:
        s += WEIGHTS.get(f, 0.0)
    return s


def assess_run(run: dict, thresholds: Optional[dict] = None, compact_level: float = 0.0, context_budget: float = 1.0) -> dict:
    """Assess a Run. compact_level 0.0..1.0 controls verbosity; context_budget 0.0..1.0 controls context in summaries."""
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    status = run.get("status", "unknown")
    tier = run.get("tier", "SAFE")
    mirror = run.get("mirror_trace", {})
    risk_flags = mirror.get("risk_flags", [])
    confidence = mirror.get("confidence", 1.0)

    base = 0.0
    if status == "BLOCKED":
        base += 0.6
    if status == "DENIED":
        base += 0.4
    if status == "TIMEOUT":
        base += 0.5
    if tier == "SENSITIVE":
        base += 0.2

    base += _score_from_flags(risk_flags)
    risk_score = min(1.0, base)

    # determine category
    if risk_score < thresholds["medium"]:
        category = "Low"
    elif risk_score < thresholds["high"]:
        category = "Medium"
    elif risk_score < thresholds["critical"]:
        category = "High"
    else:
        category = "Critical"

    # Build risk_notes with compact level control
    if compact_level <= 0.25:
        risk_notes = (
            f"Deterministic offline risk: score={risk_score:.3f}, category={category}, "
            f"flags={risk_flags}, conf={confidence:.2f}"
        )
    elif compact_level <= 0.5:
        risk_notes = (
            f"Risk {risk_score:.3f} ({category}) with {confidence:.2f} confidence"
        )
    else:
        risk_notes = None  # most compact

    # Summary line respects context budget
    if context_budget >= 0.5:
        summary = f"Run {run.get('run_id','?')} | seed {run.get('seed')} | cmd {run.get('command','')} | risk {risk_score:.3f} ({category})"
    else:
        summary = f"Run {run.get('run_id','?')} | risk {risk_score:.3f} ({category})"

    risk_action = "PROCEED"

    return {
        "risk_score": round(risk_score, 3),
        "risk_category": category,
        "risk_notes": risk_notes,
        "risk_action": risk_action,
        "summary": summary,
        "adjustment_meta": {
            "adaptive": False,
            "thresholds": thresholds,
            "compact_level": round(compact_level, 2),
            "context_budget": round(context_budget, 2)
        }
    }
