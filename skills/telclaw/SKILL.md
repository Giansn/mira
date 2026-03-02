---
name: telclaw
user-invocable: true
description: TelClaw - Telegram-based command bridge with risk-gated approvals, inline Y/N buttons, FastAPI MVP API, and mock/offline mode. Use when managing remote commands via Telegram or API with policy-based risk gating.
---

# TelClaw Skill

## Overview

TelClaw provides a Telegram-driven (and REST API) command bridge for Mira. Commands are classified by risk, gated through an approval flow, and executed in a sandboxed/simulated context. Mock and offline modes ensure safe testing.

## Architecture

- **PolicyEngine** (`policy_engine.py`): Classifies command risk 0-10. Supports mock_mode (-3 risk reduction). Deterministic risk overrides available per command.
- **Gate** (`gate.py`): Approval mechanism with Y/N options. Supports inline Telegram buttons.
- **Executor** (`executor.py`): Runs commands in simulated mode (no real side effects in mock).
- **TelClawBridge** (`bridge.py`): Core routing logic wiring PolicyEngine + Gate + Executor.
- **TelClawBot** (`telegram_bot.py`): Telegram bot bridge with inline approval buttons, command registry, wiring helpers for python-telegram-bot and aiogram.
- **CommandRegistry** (`commands.py`): Extended command set with fixed risk overrides.
- **FastAPI MVP** (`../../api_server.py`): REST API bridge exposing /api/commands, /api/approvals, /api/commands/{id}, /api/config.

## Risk Taxonomy

- **Safe (0-3):** Auto-execute, no approval needed
- **Moderate (4-5):** Y/N gate prompt required
- **High (6-8):** Formal approval required
- **Critical (9-10):** Formal approval required, strict logging

## Commands (MVP)

| Command | Risk | Description |
|---------|------|-------------|
| status/sts | 0 | System status |
| help | 0 | List commands |
| whoami | 0 | User identity |
| ping | 0 | Health check |
| time | 0 | Current UTC time |
| uptime | 1 | System uptime |
| disk | 3 | Disk usage |
| mem | 3 | Memory usage |
| config | 4 | Show/update config |
| ls | 4 | List workspace files |
| cat | 4 | Show file contents |
| logs | 4 | Recent log lines |
| start | 5 | Start a service |
| restart | 6 | Restart a service |
| stop | 6 | Stop a service |
| update | 7 | System updates |
| reset | 8 | Reset TelClaw state |
| shell | 9 | Execute shell command |
| kill | 9 | Kill a process |
| reboot | 10 | Reboot system |

## Config

File: `../../config/api_config.json`

```json
{
  "api_key": "changeme-please-set",
  "mock_mode": true,
  "offline_load": true,
  "allowed_commands": ["status","sts","restart","reset","config","reboot"],
  "thresholds": { "safe_max": 3 }
}
```

## Files

```
skills/telclaw/
  __init__.py          # Package init
  bridge.py            # Core TelClawBridge
  policy_engine.py     # Risk classification + mock_mode
  gate.py              # Approval gate with options
  executor.py          # Simulated executor
  telegram_bot.py      # Telegram bot bridge + inline buttons
  commands.py          # Extended command registry
  models.py            # Data models (CommandRequest, Approval, ExecutionResult)
  config.json          # TelClaw-specific config
  dry_run_sim.py       # Dry-run simulator
  test_sim.py          # Test harness (no external deps)
  README.md            # Quick reference

api_server.py          # FastAPI MVP bridge (workspace root)
config/api_config.json # API config (workspace root)
```

## Running

### FastAPI API server
```bash
python3 -m venv /home/ubuntu/.openclaw/venv
/home/ubuntu/.openclaw/venv/bin/pip install fastapi uvicorn
cd /home/ubuntu/.openclaw/workspace
/home/ubuntu/.openclaw/venv/bin/uvicorn api_server:app --host 127.0.0.1 --port 8000 &
```

### Test safe command
```bash
curl -s -X POST http://127.0.0.1:8000/api/commands \
  -H "X-API-Key: changeme-please-set" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"gianluca","command":"status","args":{}}' | python3 -m json.tool
```

### Test gated command
```bash
curl -s -X POST http://127.0.0.1:8000/api/commands \
  -H "X-API-Key: changeme-please-set" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"gianluca","command":"reboot","args":{}}' | python3 -m json.tool
```

### Approve a gated command
```bash
curl -s -X POST http://127.0.0.1:8000/api/approvals \
  -H "X-API-Key: changeme-please-set" \
  -H "Content-Type: application/json" \
  -d '{"command_id":"<ID>","approver_id":"admin","decision":"Y","rationale":"approved"}' | python3 -m json.tool
```

## TODO (next iteration)

- [ ] Wire deterministic risk overrides into api_server.py (restart=6, reboot=10, shell=9)
- [ ] Add offline_load seed data to api_server.py startup
- [ ] Wire Telegram bot bridge to a live bot token
- [ ] Add AEAP (Always Execute Approved Path) toggle
- [ ] Persistent approval store (optional)
- [ ] HMAC payload verification (optional)
- [ ] End-to-end integration tests
