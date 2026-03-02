#!/usr/bin/env python3
"""
TelClaw extended command set.
Each command is an async callable(user_id, args) -> str.
Risk overrides: 0-3 safe (auto), 4-5 moderate (gate), 6-10 high/critical (gate).
"""

import json
import os
from datetime import datetime, timezone


# --- System commands ---

async def cmd_status(user_id, args):
    """System status overview."""
    return "TelClaw online | mock_mode: active | bridge: healthy"


async def cmd_restart(user_id, args):
    """Restart a named service."""
    target = args.strip() if args else "telclaw"
    return f"[SIM] Restart issued for: {target}"


async def cmd_reset(user_id, args):
    """Reset TelClaw state to defaults."""
    return "[SIM] TelClaw state reset to defaults"


async def cmd_config(user_id, args):
    """Show or update config."""
    cfg_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if args.strip():
        return f"[SIM] Config updated: {args.strip()}"
    with open(cfg_path, 'r') as f:
        cfg = json.load(f)
    return f"Config:\n{json.dumps(cfg, indent=2)}"


# --- Info commands ---

async def cmd_help(user_id, args):
    """Show available commands and risk levels."""
    # Populated dynamically by TelClawBot.help_text(); placeholder here
    return "Use /help via the bot bridge for a full command list."


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


# --- Workspace commands ---

async def cmd_ls(user_id, args):
    """List workspace files (simulated)."""
    target = args.strip() if args else "workspace root"
    return f"[SIM] Listing: {target}"


async def cmd_cat(user_id, args):
    """Show file contents (simulated)."""
    target = args.strip() if args else "(no file)"
    return f"[SIM] Contents of: {target}"


async def cmd_disk(user_id, args):
    """Show disk usage (simulated)."""
    return "[SIM] Disk: 12.4G used / 28.9G total (43%)"


async def cmd_mem(user_id, args):
    """Show memory usage (simulated)."""
    return "[SIM] RAM: 842M used / 1.9G total | Swap: 128M used / 2.0G total"


# --- Service management ---

async def cmd_logs(user_id, args):
    """Show recent log lines (simulated)."""
    target = args.strip() if args else "telclaw"
    return f"[SIM] Last 10 lines of {target} logs"


async def cmd_stop(user_id, args):
    """Stop a named service."""
    target = args.strip() if args else "telclaw"
    return f"[SIM] Stop issued for: {target}"


async def cmd_start(user_id, args):
    """Start a named service."""
    target = args.strip() if args else "telclaw"
    return f"[SIM] Start issued for: {target}"


# --- Dangerous commands ---

async def cmd_shell(user_id, args):
    """Execute a shell command (simulated, gated)."""
    cmd = args.strip() if args else "(empty)"
    return f"[SIM] Shell exec: {cmd}"


async def cmd_kill(user_id, args):
    """Kill a process (simulated, gated)."""
    target = args.strip() if args else "(no target)"
    return f"[SIM] Kill: {target}"


async def cmd_reboot(user_id, args):
    """Reboot the system (simulated, gated)."""
    return "[SIM] System reboot initiated"


async def cmd_update(user_id, args):
    """Run system updates (simulated, gated)."""
    return "[SIM] System update started"


# --- Command manifest ---
# name -> (handler, description, risk_override)
# risk_override: None = auto-classify, int = fixed risk

COMMANDS = {
    # Safe (0-3): auto-execute
    "status":   (cmd_status,   "System status overview",           0),
    "help":     (cmd_help,     "Show available commands",          0),
    "whoami":   (cmd_whoami,   "Show user identity",               0),
    "ping":     (cmd_ping,     "Health check",                     0),
    "time":     (cmd_time,     "Current UTC time",                 0),
    "uptime":   (cmd_uptime,   "System uptime",                    1),

    # Moderate (4-5): Y/N gate
    "config":   (cmd_config,   "Show/update config",               4),
    "ls":       (cmd_ls,       "List workspace files",             4),
    "cat":      (cmd_cat,      "Show file contents",               4),
    "disk":     (cmd_disk,     "Disk usage",                       3),
    "mem":      (cmd_mem,      "Memory usage",                     3),
    "logs":     (cmd_logs,     "Show recent log lines",            4),

    # High (6-8): Y/N gate, strict
    "restart":  (cmd_restart,  "Restart a service",                6),
    "stop":     (cmd_stop,     "Stop a service",                   6),
    "start":    (cmd_start,    "Start a service",                  5),
    "update":   (cmd_update,   "Run system updates",               7),

    # Critical (9-10): Y/N gate, critical
    "shell":    (cmd_shell,    "Execute shell command",            9),
    "kill":     (cmd_kill,     "Kill a process",                   9),
    "reboot":   (cmd_reboot,   "Reboot system",                  10),
    "reset":    (cmd_reset,    "Reset TelClaw state",              8),
}
