#!/usr/bin/env python3
"""
Causal Analyst v0.3 (Atlas / Ra) — Adaptive Risk + Overlay Gating
Phase 2/3: env-aware, seed-driven, non-destructive overlay for Telegram gating.
Never touches main OpenClaw config. Never restarts gateway.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time
from enum import Enum
from typing import List, Dict, Any, Tuple

class Tier(Enum):
    SAFE = "SAFE"
    SENSITIVE = "SENSITIVE"
    BLOCKED = "BLOCKED"

BLOCKED_PATTERNS = ["rm -rf /", "dd if=", "mkfs", "shutdown", "reboot", "passwd"]
SAFE_PATTERNS = [
    "ls", "cat", "grep", "df", "free", "du", "head", "tail", "wc",
    "echo", "date", "uptime", "whoami", "pwd", "find",
    "curl", "wget", "pip3", "pip", "apt-get", "npm", "python3",
    "bash",
]
RISK_KEYWORDS = {
    "rm": 50, "kill": 40, "systemctl": 35, "service": 30,
    "iptables": 45, "ufw": 40, "chmod": 25, "chown": 25,
    "mv /etc": 50, "cp /etc": 30, "docker": 30,
    "openclaw config": 25, "sudo": 15, "apt": 15,
}

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except: return {}

def load_env_profile(path: str = None) -> Dict[str, Any]:
    if path is None:
        path = "/home/ubuntu/.openclaw/workspace/skills/causal-analyst/env_profile.json"
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

# Safety: lightweight context hygiene helpers (Phase 2)
def _compile_context_digest(context_strings: List[str]) -> str:
    lines = ["# Atlas Context Digest", "", "Compiled memory digest for Phase 2 safety", ""]
    # show up to last 6 items for readability
    show = context_strings[-6:]
    for i, s in enumerate(show, 1):
        lines.append(f"- {i}: {s}")
    if len(context_strings) > 6:
        lines.append(f"... {len(context_strings) - 6} more items trimmed")
    return "\n".join(lines)


def maybe_cleanup_context(context_strings: List[str], threshold: float = 0.7, max_tokens: int = 200000) -> Dict[str, Any]:
    """If the context usage exceeds threshold, write a Markdown digest and return it."""
    # rough token proxy: assume ~4 chars per token
    est_tokens = sum(len(s) for s in context_strings)  # rough chars
    est_tokens = max(0, int(est_tokens / 4))
    ratio = est_tokens / max_tokens if max_tokens else 0.0
    if ratio < threshold:
        return {"digest": None, "written": False}
    digest = _compile_context_digest(context_strings)
    path = "/home/ubuntu/.openclaw/workspace/atlas_context_digest.md"
    with open(path, "w") as f:
        f.write(digest)
    return {"digest": digest, "written": True}

# === End patch placeholder for environment hooks ===

# --- rest of the original content will be appended below in actual run ---
