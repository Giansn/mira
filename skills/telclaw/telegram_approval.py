#!/usr/bin/env python3
"""
TelClaw Telegram Approval Bot
- Connects to local FastAPI MVP bridge
- Sends commands, receives approval prompts, handles Y/N inline buttons
- Works in AEAP + offline_free_pass mode
- No external API calls; all local to 127.0.0.1:8000
"""

import json
import logging
import os
import urllib.request
import urllib.error
from typing import Optional

logger = logging.getLogger("telclaw.telegram_approval")

# --- Config ---

DEFAULT_API_BASE = "http://127.0.0.1:8000"
DEFAULT_API_KEY = "changeme-please-set"

def load_bot_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "telegram_bot.json")
    try:
        with open(cfg_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# --- API helpers (local only, no external calls) ---

def api_post(endpoint: str, payload: dict, api_base: str = DEFAULT_API_BASE, api_key: str = DEFAULT_API_KEY) -> dict:
    url = f"{api_base}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": e.code, "detail": body}
    except Exception as e:
        return {"error": str(e)}

def api_get(endpoint: str, api_base: str = DEFAULT_API_BASE, api_key: str = DEFAULT_API_KEY) -> dict:
    url = f"{api_base}{endpoint}"
    req = urllib.request.Request(url, headers={"X-API-Key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

# --- Command + Approval flow ---

def send_command(user_id: str, command: str, args: dict = None) -> dict:
    """Send a command to the API and return the result."""
    payload = {"user_id": user_id, "command": command, "args": args or {}}
    return api_post("/api/commands", payload)

def approve_command(command_id: str, approver_id: str, decision: str = "Y", rationale: str = "") -> dict:
    """Approve or deny a pending command."""
    payload = {
        "command_id": command_id,
        "approver_id": approver_id,
        "decision": decision,
        "rationale": rationale,
    }
    return api_post("/api/approvals", payload)

def get_config() -> dict:
    """Fetch current API config."""
    return api_get("/api/config")

def get_metrics() -> dict:
    """Fetch current metrics (if enabled)."""
    return api_get("/api/metrics")

# --- Telegram message formatting ---

def format_command_result(result: dict) -> str:
    """Format a command result for Telegram display."""
    if "error" in result:
        return f"Error: {result.get('detail', result.get('error', 'unknown'))}"

    status = result.get("status", "unknown")
    risk = result.get("risk", "?")
    cid = result.get("command_id", "?")
    msg = result.get("message", "")
    requires = result.get("requires_approval", False)

    lines = [f"CMD: {cid[:8]}...", f"Risk: {risk}", f"Status: {status}"]
    if requires:
        lines.append("Approval: REQUIRED")
    if msg:
        lines.append(f"Message: {msg}")
    return "\n".join(lines)

def format_approval_result(result: dict) -> str:
    """Format an approval result for Telegram display."""
    if "error" in result:
        return f"Error: {result.get('detail', result.get('error', 'unknown'))}"

    status = result.get("status", "unknown")
    exec_result = result.get("execution_result", "")
    lines = [f"Decision: {status}"]
    if exec_result:
        lines.append(f"Result: {exec_result}")
    return "\n".join(lines)

def format_config(cfg: dict) -> str:
    """Format config for Telegram display."""
    if "error" in cfg:
        return f"Error: {cfg.get('error', 'unknown')}"
    lines = [
        f"AEAP: {'ON' if cfg.get('aeap') else 'OFF'}",
        f"Offline free pass: {'ON' if cfg.get('offline_free_pass') else 'OFF'}",
        f"Metrics: {'ON' if cfg.get('metrics_enabled') else 'OFF'}",
        f"Mock mode: {'ON' if cfg.get('mock_mode') else 'OFF'}",
        f"Commands: {len(cfg.get('allowed_commands', []))} allowed",
    ]
    return "\n".join(lines)

def format_metrics(m: dict) -> str:
    """Format metrics for Telegram display."""
    if m.get("status") == "disabled":
        return "Metrics: disabled (offline mode)"
    if "error" in m:
        return f"Error: {m.get('error', 'unknown')}"
    lines = [
        f"Requests: {m.get('total_requests', 0)}",
        f"Success: {m.get('success_rate_percent', 0):.1f}%",
        f"Errors: {m.get('error_rate_percent', 0):.1f}%",
        f"Avg latency: {m.get('avg_response_time_ms', 0):.1f}ms",
        f"P95 latency: {m.get('p95_response_time_ms', 0):.1f}ms",
        f"Uptime: {m.get('total_session_time_sec', 0):.0f}s",
    ]
    return "\n".join(lines)

# --- Inline button helpers (for python-telegram-bot / aiogram) ---

def make_approval_buttons(command_id: str) -> list:
    """Return inline button data for Y/N approval."""
    return [
        {"text": "Y Approve", "callback_data": f"approve:{command_id}:Y"},
        {"text": "N Deny", "callback_data": f"approve:{command_id}:N"},
    ]

def parse_callback(callback_data: str) -> Optional[dict]:
    """Parse callback data from inline button press."""
    parts = callback_data.split(":")
    if len(parts) == 3 and parts[0] == "approve":
        return {"command_id": parts[1], "decision": parts[2]}
    return None


# --- Wire into python-telegram-bot (ptb) ---

def wire_approval_to_ptb(application, api_key: str = DEFAULT_API_KEY):
    """
    Wire TelClaw approval flow into an existing python-telegram-bot Application.

    Usage:
        from telegram.ext import ApplicationBuilder
        app = ApplicationBuilder().token(TOKEN).build()
        wire_approval_to_ptb(app, api_key="your-key")
        app.run_polling()
    """
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

    async def on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        parts = text.split(None, 1)
        cmd = parts[0].lstrip("/").lower()
        args_str = parts[1] if len(parts) > 1 else ""
        user_id = str(update.effective_user.id)

        # Special commands
        if cmd == "config":
            cfg = get_config()
            await update.message.reply_text(format_config(cfg))
            return
        if cmd == "metrics":
            m = get_metrics()
            await update.message.reply_text(format_metrics(m))
            return

        # Send command to API
        result = send_command(user_id, cmd, {"raw": args_str} if args_str else {})
        msg = format_command_result(result)

        # If approval required, show inline buttons
        if result.get("requires_approval"):
            cid = result.get("command_id", "")
            buttons = make_approval_buttons(cid)
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text=b["text"], callback_data=b["callback_data"])
                for b in buttons
            ]])
            await update.message.reply_text(msg, reply_markup=keyboard)
        else:
            await update.message.reply_text(msg)

    async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        parsed = parse_callback(query.data)
        if not parsed:
            await query.edit_message_text("Invalid callback.")
            return

        user_id = str(query.from_user.id)
        result = approve_command(
            parsed["command_id"],
            approver_id=user_id,
            decision=parsed["decision"],
            rationale="Telegram inline approval",
        )
        msg = format_approval_result(result)
        await query.edit_message_text(msg)

    async def on_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "TelClaw Commands:\n"
            "/status - System status\n"
            "/config - Show config\n"
            "/metrics - Show metrics\n"
            "/restart - Restart service\n"
            "/reboot - Reboot system\n"
            "/reset - Reset state\n"
            "/kill - Kill process\n"
            "/help - This message\n\n"
            "Any command triggers risk assessment.\n"
            "High-risk commands show Y/N approval buttons."
        )
        await update.message.reply_text(help_text)

    application.add_handler(CommandHandler("help", on_help))
    application.add_handler(MessageHandler(filters.COMMAND, on_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_command))
    application.add_handler(CallbackQueryHandler(on_callback))


# --- Wire into aiogram ---

def wire_approval_to_aiogram(dp, bot_instance, api_key: str = DEFAULT_API_KEY):
    """
    Wire TelClaw approval flow into an existing aiogram Dispatcher.

    Usage:
        from aiogram import Bot, Dispatcher
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
        wire_approval_to_aiogram(dp, bot, api_key="your-key")
        dp.run_polling(bot)
    """
    from aiogram import types
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    @dp.message()
    async def on_message(message: types.Message):
        text = message.text.strip()
        parts = text.split(None, 1)
        cmd = parts[0].lstrip("/").lower()
        args_str = parts[1] if len(parts) > 1 else ""
        user_id = str(message.from_user.id)

        if cmd == "config":
            cfg = get_config()
            await message.answer(format_config(cfg))
            return
        if cmd == "metrics":
            m = get_metrics()
            await message.answer(format_metrics(m))
            return

        result = send_command(user_id, cmd, {"raw": args_str} if args_str else {})
        msg = format_command_result(result)

        if result.get("requires_approval"):
            cid = result.get("command_id", "")
            buttons = make_approval_buttons(cid)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=b["text"], callback_data=b["callback_data"])
                for b in buttons
            ]])
            await message.answer(msg, reply_markup=keyboard)
        else:
            await message.answer(msg)

    @dp.callback_query()
    async def on_callback(callback: types.CallbackQuery):
        parsed = parse_callback(callback.data)
        if not parsed:
            await callback.message.edit_text("Invalid callback.")
            await callback.answer()
            return

        user_id = str(callback.from_user.id)
        result = approve_command(
            parsed["command_id"],
            approver_id=user_id,
            decision=parsed["decision"],
            rationale="Telegram inline approval",
        )
        msg = format_approval_result(result)
        await callback.message.edit_text(msg)
        await callback.answer()
