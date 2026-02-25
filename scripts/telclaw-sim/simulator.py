#!/usr/bin/env python3
"""
TelClaw Simulator — Virtual environment to test Telegram approval flow.
Simulates: OpenClaw exec gateway, Telegram Bot API, approval routing.
No real API calls. Pure logic simulation.
"""

import json
import time
import random
import sys
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

# === Models ===

class Tier(Enum):
    SAFE = "safe"          # Tier 1 — no approval
    SENSITIVE = "sensitive" # Tier 2 — Telegram approval
    BLOCKED = "blocked"    # Tier 3 — always deny

class ApprovalState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"

@dataclass
class Command:
    raw: str
    binary: str = ""
    tier: Tier = Tier.SAFE

@dataclass
class ApprovalRequest:
    id: str
    command: str
    state: ApprovalState = ApprovalState.PENDING
    telegram_msg_sent: bool = False
    callback_received: bool = False
    timestamp: float = field(default_factory=time.time)

# === Policy Engine ===

TIER_RULES = {
    Tier.SAFE: [
        "ls", "cat", "grep", "df", "free", "du", "head", "tail", "wc",
        "echo", "date", "uptime", "whoami", "pwd", "find",
        "curl", "wget", "pip3", "pip", "apt-get", "npm", "python3",
        "bash /home/ubuntu/.openclaw/workspace/scripts/stats.sh",
    ],
    Tier.BLOCKED: [
        "rm -rf /", "dd if=", "mkfs", "shutdown", "reboot", "passwd",
    ],
}

def classify_command(raw: str) -> Command:
    cmd = Command(raw=raw)
    cmd.binary = raw.strip().split()[0] if raw.strip() else ""

    # Check blocked first
    for pattern in TIER_RULES[Tier.BLOCKED]:
        if pattern in raw:
            cmd.tier = Tier.BLOCKED
            return cmd

    # Check safe
    for pattern in TIER_RULES[Tier.SAFE]:
        if raw.strip().startswith(pattern) or cmd.binary == pattern:
            cmd.tier = Tier.SAFE
            return cmd

    # Default: sensitive
    cmd.tier = Tier.SENSITIVE
    return cmd

# === Telegram Simulator ===

class TelegramSim:
    """Simulates Telegram Bot API responses."""

    def __init__(self, auto_approve_prob: float = 0.8, response_delay_ms: int = 2000):
        self.auto_approve_prob = auto_approve_prob
        self.response_delay_ms = response_delay_ms
        self.messages_sent = []
        self.callbacks = []

    def send_approval_button(self, approval: ApprovalRequest) -> dict:
        msg = {
            "message_id": random.randint(1000, 9999),
            "chat_id": 1134139785,
            "text": f"Approval request:\n`{approval.command}`\nID: {approval.id}",
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "Grant", "callback_data": f"grant-{approval.id}"},
                    {"text": "Deny", "callback_data": f"deny-{approval.id}"}
                ]]
            }
        }
        self.messages_sent.append(msg)
        approval.telegram_msg_sent = True
        return {"ok": True, "result": msg}

    def simulate_user_response(self, approval: ApprovalRequest) -> ApprovalState:
        """Simulate user tapping grant/deny with probability."""
        if random.random() < self.auto_approve_prob:
            approval.state = ApprovalState.APPROVED
            approval.callback_received = True
        else:
            if random.random() < 0.5:
                approval.state = ApprovalState.DENIED
                approval.callback_received = True
            else:
                approval.state = ApprovalState.TIMEOUT
        return approval.state

# === Gateway Simulator ===

class GatewaySim:
    """Simulates OpenClaw exec gateway with TelClaw approval routing.""" 

    def __init__(self, telegram: TelegramSim):
        self.telegram = telegram
        self.approvals: list[ApprovalRequest] = []
        self.exec_log: list[dict] = []
        self.ask_mode = "off"  # off | on-miss | always

    def execute(self, raw_command: str) -> dict:
        cmd = classify_command(raw_command)
        result = {
            "command": raw_command,
            "tier": cmd.tier.value,
            "binary": cmd.binary,
            "executed": False,
            "approval": None,
            "output": None,
            "error": None,
        }

        # Tier 3 — always deny
        if cmd.tier == Tier.BLOCKED:
            result["error"] = "BLOCKED: destructive command denied by policy"
            self.exec_log.append(result)
            return result

        # Tier 1 — run immediately
        if cmd.tier == Tier.SAFE:
            result["executed"] = True
            result["output"] = f"[simulated output of: {raw_command}]"
            self.exec_log.append(result)
            return result

        # Tier 2 — Telegram approval
        approval = ApprovalRequest(
            id=f"telclaw-{int(time.time())}-{random.randint(100,999)}",
            command=raw_command,
        )
        self.approvals.append(approval)

        # Send Telegram button
        tg_result = self.telegram.send_approval_button(approval)
        result["approval"] = {
            "id": approval.id,
            "telegram_sent": tg_result["ok"],
            "message_id": tg_result["result"]["message_id"],
        }

        # Simulate user response
        state = self.telegram.simulate_user_response(approval)
        result["approval"]["state"] = state.value

        if state == ApprovalState.APPROVED:
            result["executed"] = True
            result["output"] = f"[simulated output of: {raw_command}]"
        elif state == ApprovalState.DENIED:
            result["error"] = "DENIED by user via Telegram"
        else:
            result["error"] = "TIMEOUT: no response within deadline"

        self.exec_log.append(result)
        return result

# === Test Suite ===

TEST_COMMANDS = [
    'ls -la /home/ubuntu',
    'df -h /',
    'free -h',
    'cat /proc/loadavg',
    'bash /home/ubuntu/.openclaw/workspace/scripts/stats.sh',
    'pip3 list --outdated',
    'curl -s https://example.com',
    'systemctl restart openclaw',
    'openclaw config set tools.exec.ask off',
    'mv /etc/important.conf /tmp/',
    'docker rm -f container',
    'rm -rf /',
    'dd if=/dev/zero of=/dev/sda',
    'mkfs.ext4 /dev/sda1',
    'shutdown -h now',
]


def run_simulation():
    passenger = input if False else None
    import sys
    sys.exit(0)

PY

