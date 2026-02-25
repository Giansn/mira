#!/usr/bin/env python3
"""Mirror Agent — single-pass critique producing MirrorTrace."""

RISK_VOCAB = ["ESCALATE", "REVIEW", "SAFE_OVERRIDE", "DATA_RISK", "UNKNOWN_CMD"]

HEURISTICS = {
    "BLOCKED": {"reasoning": "Blocked unconditionally. No execution path.", "risk_flags": [], "confidence": 1.0, "alternative_action": None},
    "SAFE": {"reasoning": "Read-only or benign command. No side effects detected.", "risk_flags": [], "confidence": 0.95, "alternative_action": None},
}

def evaluate(run, persona=None):
    """Produce a MirrorTrace for a completed Run object.
    Single pass. No recursion. No external calls."""
    tier = run.get("tier", "SAFE")
    status = run.get("status", "ran")
    command = run.get("command", "")

    if tier in HEURISTICS:
        trace = dict(HEURISTICS[tier])
    else:
        # SENSITIVE tier — nuanced critique
        trace = {
            "reasoning": f"SENSITIVE command '{command[:32]}' evaluated by policy engine.",
            "risk_flags": [],
            "confidence": 0.7,
            "alternative_action": None
        }
        if status == "denied":
            trace["reasoning"] += " Denied — no explicit grant rule."
            trace["risk_flags"].append("REVIEW")
        elif status == "timeout":
            trace["reasoning"] += " Timed out waiting for approval."
            trace["risk_flags"].append("ESCALATE")
            trace["confidence"] = 0.4
        elif status == "ran":
            trace["reasoning"] += " Granted and executed."
            trace["confidence"] = 0.8

    # Persona anchor override
    if persona and persona.get("confidence_bias") == "pessimistic":
        trace["confidence"] = max(0.0, trace["confidence"] - 0.15)
    if persona and persona.get("confidence_bias") == "optimistic":
        trace["confidence"] = min(1.0, trace["confidence"] + 0.1)

    # Auto-flag low confidence
    if trace["confidence"] < 0.5 and "REVIEW" not in trace["risk_flags"]:
        trace["risk_flags"].append("REVIEW")

    return trace
