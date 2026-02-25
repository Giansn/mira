"""
userbot.py — Telegram → OpenClaw relay
Features:
  - Forwards incoming Telegram messages to OpenClaw via WebSocket RPC
  - Routes agent replies back to the original sender
  - Access gate (gate.md rules) enforced before any API call
  - Global rate limiting (10 msg/min total)
  - Text first; media support stubbed for later
  - Dry-run mode: log-only, no real replies sent
"""

import asyncio
import json
import logging
import os
import time
from collections import deque

import websockets
from telethon import TelegramClient, events
from telethon.tl.types import User

# ── Config ────────────────────────────────────────────────────────────────────

API_ID       = int(os.environ["TG_API_ID"])
API_HASH     = os.environ["TG_API_HASH"]
SESSION_NAME = os.environ.get("TG_SESSION", "userbot")
WS_URL       = os.environ.get("OPENCLAW_WS", "ws://127.0.0.1:18789")
DRY_RUN      = os.environ.get("DRY_RUN", "0") == "1"

# Gate passwords
OWNER_ID       = 1134139785
FULL_PASSWORD  = "sierra nevada"
GUEST_PASSWORD = "yesui umaqui"
GUEST_LIMIT    = 4

# Global rate limit: max N messages per window (seconds)
RATE_LIMIT_MAX    = 10
RATE_LIMIT_WINDOW = 60  # seconds

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("userbot")

# ── State ─────────────────────────────────────────────────────────────────────

# Per-sender gate state
# { sender_id: { "access": "none"|"guest"|"full", "prompts_used": int, "exhausted": bool } }
gate_state: dict[int, dict] = {}

# Global rate limiting: timestamps of recent messages
rate_window: deque = deque()

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_rate_limited() -> bool:
    now = time.monotonic()
    while rate_window and now - rate_window[0] > RATE_LIMIT_WINDOW:
        rate_window.popleft()
    if len(rate_window) >= RATE_LIMIT_MAX:
        return True
    rate_window.append(now)
    return False


def gate_check(sender_id: int, text: str) -> tuple[bool, str | None]:
    """
    Returns (should_forward, reply_or_none).
    - should_forward=True  → pass message to OpenClaw
    - should_forward=False → reply_or_none is the gate response (or None = total silence)
    """
    if sender_id == OWNER_ID:
        return True, None

    state = gate_state.setdefault(sender_id, {
        "access": "none",
        "prompts_used": 0,
        "exhausted": False,
    })

    # Already exhausted — total silence
    if state["exhausted"]:
        return False, None

    # Full access
    if state["access"] == "full":
        return True, None

    # Guest access
    if state["access"] == "guest":
        if state["prompts_used"] >= GUEST_LIMIT:
            state["exhausted"] = True
            return False, None
        state["prompts_used"] += 1
        append = ""
        if state["prompts_used"] == GUEST_LIMIT:
            append = "\n\nThat was your last guest prompt. To continue, please provide the full access password."
        return True, append if append else None  # forward, but maybe append a note

    # No access yet — check if they're providing a password
    stripped = text.strip().lower()

    if stripped == FULL_PASSWORD.lower():
        state["access"] = "full"
        return False, "Full access granted. How can I help?"

    if stripped == GUEST_PASSWORD.lower():
        state["access"] = "guest"
        state["prompts_used"] = 0
        return False, (
            "You have guest access — 4 prompts available. "
            "For full access, ask Gianluca for the full access password. "
            "Once your 4 prompts are used up, I will stop responding entirely."
        )

    # Unknown — ask for password
    return False, (
        "Hi! This is a private assistant. "
        "Please provide the access password to continue."
    )


async def send_to_openclaw(sender_id: int, chat_id: int, message_id: int, text: str) -> str:
    """Send a message to OpenClaw via WebSocket RPC and return the reply."""
    payload = json.dumps({
        "type": "message",
        "channel": "telegram",
        "sender_id": sender_id,
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    })
    log.info(f"→ OpenClaw | chat={chat_id} sender={sender_id}: {text[:80]}")
    async with websockets.connect(WS_URL, open_timeout=10) as ws:
        await ws.send(payload)
        response = await asyncio.wait_for(ws.recv(), timeout=120)
    data = json.loads(response)
    return data.get("reply", "")


# ── Main handler ──────────────────────────────────────────────────────────────

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender: User = await event.get_sender()
    if not sender or sender.bot:
        return

    sender_id = sender.id
    chat_id   = event.chat_id
    message_id = event.id
    text = event.raw_text or ""

    # Media: stub — skip for now
    if event.media and not text:
        if not DRY_RUN:
            await event.reply("Media messages aren't supported yet — text only for now.")
        log.info(f"Media message from {sender_id} skipped.")
        return

    # Rate limit
    if is_rate_limited():
        log.warning("Global rate limit hit — dropping message.")
        return

    # Gate check
    forward, gate_reply = gate_check(sender_id, text)

    if not forward:
        if gate_reply is not None:
            if DRY_RUN:
                log.info(f"[DRY RUN] Gate reply to {sender_id}: {gate_reply}")
            else:
                await event.reply(gate_reply)
        else:
            log.info(f"Silence enforced for exhausted guest {sender_id}.")
        return

    # Forward to OpenClaw
    try:
        if DRY_RUN:
            log.info(f"[DRY RUN] Would forward to OpenClaw: {text[:80]}")
            reply_text = "[DRY RUN] This is where the agent reply would appear."
        else:
            reply_text = await send_to_openclaw(sender_id, chat_id, message_id, text)

        # Append guest exhaustion notice if needed
        state = gate_state.get(sender_id)
        if state and state["access"] == "guest" and state["prompts_used"] == GUEST_LIMIT:
            reply_text += (
                "\n\nThat was your last guest prompt. "
                "To continue, please provide the full access password."
            )

        if reply_text:
            if DRY_RUN:
                log.info(f"[DRY RUN] Reply to {sender_id}: {reply_text[:80]}")
            else:
                await event.reply(reply_text)

    except asyncio.TimeoutError:
        log.error("OpenClaw did not respond in time.")
        if not DRY_RUN:
            await event.reply("Sorry, the assistant is not responding right now. Try again shortly.")
    except Exception as e:
        log.exception(f"Relay error: {e}")
        if not DRY_RUN:
            await event.reply("Something went wrong on my end. Please try again.")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    log.info(f"Starting userbot relay [{mode}] → {WS_URL}")
    await client.start()
    log.info("Connected. Listening for messages...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
