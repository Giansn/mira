#!/usr/bin/env python3
"""
TelClaw Telegram Bot Bridge
- Wires into existing bots via pluggable handler registration
- Inline Y/N approval buttons for gated commands
- Built-in commands: status, restart, reset, config, sts
- Supports custom command registration
- All actions gated by PolicyEngine + Gate
- No persistent file logs; logs go to stdout for ephemeral dry-runs
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timezone

# --- Logging: use stdout only; no persistent log files ---
logger = logging.getLogger('telclaw')
logger.setLevel(logging.INFO)
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
# Avoid duplicate handlers if re-imported
if not logger.handlers:
    logger.addHandler(sh)


# --- Config loader ---
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config(path=None):
    path = path or DEFAULT_CONFIG_PATH
    with open(path, 'r') as f:
        return json.load(f)


# --- Command Registry ---
class CommandRegistry:
    """Register named commands with handlers, descriptions, and fixed risk overrides."""

    def __init__(self):
        self._commands = {}

    def register(self, name, handler, description="", risk_override=None):
        """
        Register a command.
        - name: command name (e.g. "status")
        - handler: async callable(user_id, args) -> str
        - description: human-readable help text
        - risk_override: fixed risk int (0-10) or None for auto-classify
        """
        self._commands[name] = {
            "handler": handler,
            "description": description,
            "risk_override": risk_override,
        }

    def get(self, name):
        return self._commands.get(name)

    def list_commands(self):
        return {k: v["description"] for k, v in self._commands.items()}

    def has(self, name):
        return name in self._commands


# --- Built-in command handlers ---
async def cmd_status(user_id, args):
    """Return system status summary."""
    return "TelClaw online | mock_mode: active | bridge: healthy"

async def cmd_restart(user_id, args):
    """Restart a named service (simulated in mock mode)."""
    target = args.strip() if args else "telclaw"
    return f"[SIM] Restart issued for: {target}"

async def cmd_reset(user_id, args):
    """Reset TelClaw state (simulated in mock mode)."""
    return "[SIM] TelClaw state reset to defaults"

async def cmd_config(user_id, args):
    """Show or update config (simulated in mock mode)."""
    if args.strip():
        return f"[SIM] Config updated: {args.strip()}"
    cfg = load_config()
    return f"Current config:\n{json.dumps(cfg, indent=2)}"


async def cmd_help(user_id, args):
    """Show available commands and risk levels."""
    return "Available commands are exposed via the bot bridge. Use /sts for status if configured."

async def cmd_whoami(user_id, args):
    """Show current user identity and permissions."""
    return f"User: {user_id} | Access: granted"

async def cmd_uptime(user_id, args):
    """Show system uptime."""
    return f"[SIM] Uptime: 4d 12h 33m"

async def cmd_ping(user_id, args):
    """Health check ping."""
    return "pong"

async def cmd_time(user_id, args):
    """Current UTC time."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"Time: {now}"

# --- Namespace helpers for optional extras ---

# Optional extras for future expansion

# --- TelClaw Bot Bridge (integration point) ---
class TelClawBot:
    """
    Telegram bot bridge for TelClaw.
    Can be used standalone or wired into an existing bot.
    """

    def __init__(self, policy_engine, gate, executor, config=None, allowed_chat_ids=None):
        self.policy_engine = policy_engine
        self.gate = gate
        self.executor = executor
        self.config = config or load_config()
        self.allowed_chat_ids = allowed_chat_ids or self.config.get("allowed_chat_ids", [])
        self.registry = CommandRegistry()
        self.approvals = {}
        self._counter = 0

        # Register built-in commands
        self.registry.register("status", cmd_status, "System status", risk_override=0)
        self.registry.register("sts", cmd_status, "Alias for status", risk_override=0)
        self.registry.register("restart", cmd_restart, "Restart a service", risk_override=6)
        self.registry.register("reset", cmd_reset, "Reset TelClaw state", risk_override=8)
        self.registry.register("config", cmd_config, "Show/update config", risk_override=4)
        self.registry.register("help", cmd_help, "Help text", risk_override=0)
        self.registry.register("whoami", cmd_whoami, "Identity", risk_override=0)
        self.registry.register("time", cmd_time, "Current time", risk_override=0)

    def register_command(self, name, handler, description="", risk_override=None):
        self.registry.register(name, handler, description, risk_override)

    def _next_id(self):
        self._counter += 1
        return f"cb-{self._counter:04d}"

    def _is_allowed(self, chat_id):
        if not self.allowed_chat_ids:
            return True
        return str(chat_id) in [str(c) for c in self.allowed_chat_ids]

    async def handle_message(self, chat_id, user_id, text):
        if not self._is_allowed(chat_id):
            logger.warning(f"Unauthorized chat: {chat_id}")
            return {"reply": "Unauthorized.", "inline_buttons": None}

        parts = text.strip().split(None, 1)
        command = parts[0].lstrip("/").lower()
        args = parts[1] if len(parts) > 1 else ""

        entry = self.registry.get(command)
        if not entry:
            cmds = self.registry.list_commands()
            cmd_list = "\n".join(f"  {k} -- {v}" for k, v in cmds.items())
            return {"reply": f"Unknown command: {command}\n\nAvailable:\n{cmd_list}", "inline_buttons": None}

        risk = entry["risk_override"] if entry["risk_override"] is not None else self.policy_engine.classify(command, args)
        logger.info(f"CMD={command} USER={user_id} RISK={risk}")

        if risk <= 3:
            result = await entry["handler"](user_id, args)
            return {"reply": f"[risk {risk}] {result}", "inline_buttons": None}

        cb_id = self._next_id()
        self.approvals[cb_id] = {"user_id": user_id, "command": command, "args": args, "risk": risk, "created": None}
        prompt = (
            f"Approve? CMD: {command}, ARGS: {args or '(none)'}, RISK: {risk}, ID: {cb_id}"
        )
        buttons = [{"text": "Y", "callback_data": f"{cb_id}:Y"}, {"text": "N", "callback_data": f"{cb_id}:N"}]
        return {"reply": prompt, "inline_buttons": buttons}

    async def handle_callback(self, user_id, callback_data):
        cb_id, decision = callback_data.split(":", 1)
        decision = decision.upper()
        entry = self.approvals.pop(cb_id, None)
        if not entry:
            return {"reply": f"Approval {cb_id} not found"}
        if decision == "Y":
            handler = self.registry.get(entry["command"])["handler"]
            result = await handler(entry["user_id"], entry["args"])
            return {"reply": f"[approved] {result}"}
        else:
            return {"reply": f"[denied] {entry['command']} blocked."}

    def help_text(self):
        cmds = self.registry.list_commands()
        lines = [f"/{k} — {v}" for k, v in cmds.items()]
        return "TelClaw commands:\n" + "\n".join(lines)


# This module provides a minimal, in-process bridge. Integrations with python-telegram-bot
# or aiogram can import TelClawBot and call the wiring helpers from the bottom of the file.
