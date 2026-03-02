#!/usr/bin/env python3
"""
Self-Simulation Framework
- Log decision rationale before acting
- Branch alternative reasoning paths
- Compare outcomes and learn
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

SIM_DIR = Path("/home/ubuntu/.openclaw/workspace/simulations")
DECISION_LOG = SIM_DIR / "decisions.jsonl"
BRANCHES_DIR = SIM_DIR / "branches"

# Ensure directories exist
SIM_DIR.mkdir(exist_ok=True)
BRANCHES_DIR.mkdir(exist_ok=True)

def log_decision(
    context: str,
    choice: str,
    rationale: str,
    alternatives: list = None,
    confidence: float = 0.5
):
    """Log a decision before executing it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context[:500],  # Truncate long contexts
        "choice": choice,
        "rationale": rationale,
        "alternatives": alternatives or [],
        "confidence": confidence,
    }
    with open(DECISION_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def branch(
    branch_id: str,
    context: str,
    prompt: str,
    strategy: str = "default"
):
    """
    Create an alternative reasoning branch.
    Strategies: default, devil_advocate, conservative, creative
    """
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    entry = {
        "branch_id": branch_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "context": context[:500],
        "prompt": prompt,
        "strategy": strategy,
        "status": "pending",
    }
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    return entry

def resolve_branch(branch_id: str, outcome: str, learnings: str = ""):
    """Mark a branch as resolved with outcome and learnings."""
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    if branch_file.exists():
        with open(branch_file, "r") as f:
            entry = json.load(f)
        entry["status"] = "resolved"
        entry["outcome"] = outcome
        entry["learnings"] = learnings
        entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
        with open(branch_file, "w") as f:
            json.dump(entry, f, indent=2)
    return entry

def get_recent_decisions(limit: int = 10):
    """Get recent decision log entries."""
    if not DECISION_LOG.exists():
        return []
    with open(DECISION_LOG, "r") as f:
        lines = f.readlines()
    entries = [json.loads(line) for line in reversed(lines[-limit:])]
    return list(reversed(entries))

def get_pending_branches():
    """Get all pending branches."""
    pending = []
    for f in BRANCHES_DIR.glob("*.json"):
        with open(f) as fp:
            entry = json.load(fp)
        if entry.get("status") == "pending":
            pending.append(entry)
    return pending

# Quick CLI for testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "log":
            print(log_decision(
                context=sys.argv[2] if len(sys.argv) > 2 else "",
                choice=sys.argv[3] if len(sys.argv) > 3 else "",
                rationale=sys.argv[4] if len(sys.argv) > 4 else ""
            ))
        elif cmd == "branches":
            print(json.dumps(get_pending_branches(), indent=2))
        elif cmd == "recent":
            print(json.dumps(get_recent_decisions(), indent=2))
