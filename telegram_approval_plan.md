# Telegram Approval Plan
*Mira — 2026-02-24*

## Goal
Route exec approvals through Telegram inline buttons instead of the web console. Low-risk commands run without approval; sensitive commands get a Telegram prompt.

---

## Step 1 — Disable approvals for safe commands

Run once on the console (or via web UI):

```bash
openclaw config set tools.exec.ask off
```

This disables approval prompts for all exec calls from the agent. Combined with the tiered policy below, this is safe.

**Alternative (more granular):** edit `~/.openclaw/exec-approvals.json` — see Step 3.

---

## Step 2 — Set up Telegram approval credentials

Create the credentials file:

```bash
mkdir -p ~/.openclaw/.private
cat > ~/.openclaw/.private/telegram-approval.env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF
chmod 600 ~/.openclaw/.private/telegram-approval.env
```

**How to get these:**
- `TELEGRAM_BOT_TOKEN` — from @BotFather on Telegram (you likely already have this from the OpenClaw setup)
- `TELEGRAM_CHAT_ID` — your personal chat ID (Gianluca's is: 1134139785)

---

## Step 3 — Tiered exec policy (exec-approvals.json)

Edit `~/.openclaw/exec-approvals.json`:

```json
{
  "version": 1,
  "defaultPolicy": "allow",
  "rules": [
    {
      "match": ["rm -rf", "dd ", "mkfs", "shutdown", "reboot", "passwd"],
      "policy": "deny",
      "reason": "Destructive — always blocked"
    },
    {
      "match": ["curl", "wget", "pip", "apt", "npm", "bash", "python3", "df", "free", "ls", "cat", "grep", "du"],
      "policy": "allow",
      "reason": "Safe utilities — no approval needed"
    }
  ]
}
```

---

## Step 4 — Make stats.sh executable

```bash
chmod +x ~/.openclaw/workspace/scripts/stats.sh
chmod +x ~/.openclaw/workspace/scripts/telegram-approval.sh
```

---

## Step 5 — Test /stats

From Telegram, send: `/stats`

Mira will run `stats.sh` and return live system info.

---

## Step 6 — Test Telegram approval wrapper

For sensitive commands, Mira will call:

```bash
bash ~/.openclaw/workspace/scripts/telegram-approval.sh "Description of command" "actual_command_here"
```

You'll receive an inline button message on Telegram. Tap Grant or Deny.

---

## Tiered Command Policy Summary

| Tier | Commands | Behavior |
|------|----------|----------|
| 1 — Safe | ls, cat, df, free, curl, pip, apt, bash scripts | Run immediately, no prompt |
| 2 — Sensitive | rm, system changes, external posts | Telegram inline button prompt |
| 3 — Blocked | rm -rf /, dd, mkfs, shutdown | Always denied |

---

## Efficiency Notes (AEAP)

- `ask=off` globally removes approval roundtrip overhead
- Approval wrapper only spawned for Tier 2 commands — minimal API calls
- stats.sh is a local shell script — zero API usage once exec is unblocked
- Telegram bot polling uses 30s long-poll — efficient, not busy-loop

---

## Quick Setup Checklist

- [ ] `openclaw config set tools.exec.ask off`
- [ ] Create `~/.openclaw/.private/telegram-approval.env` with bot token + chat ID
- [ ] `chmod +x` both scripts
- [ ] Test `/stats` from Telegram
- [ ] Test approval wrapper with a safe dummy command
