# Session Manager Skill

A clean, human-friendly session management system for OpenClaw.

## Problem
OpenClaw session keys are complex internal identifiers (`agent:main:telegram:slash:1134139785`). Users want simple names like "telegram" and "dashboard" and control over which sessions are active.

## Solution
This skill maintains a mapping between human-readable session names and OpenClaw's internal session keys, plus provides cleanup and management tools.

## Files
- `session-manager/SKILL.md` - This file
- `session-manager/session-map.json` - Mapping of human names to session keys
- `session-manager/cleanup-script.sh` - Script to clean up old sessions
- `session-manager/README.md` - User documentation

## Usage

### List current sessions with human names
```bash
./session-manager/list-sessions
```

### Rename a session
```bash
./session-manager/rename-session "agent:main:telegram:slash:1134139785" "telegram"
```

### Clean up old sessions (keep only active ones)
```bash
./session-manager/cleanup-sessions
```

### View session mapping
```bash
cat session-manager/session-map.json
```

## How It Works
1. Scans OpenClaw session store
2. Maps internal keys to human names based on patterns
3. Provides commands to manage sessions
4. Can integrate with OpenClaw Control UI via configuration

## Session Patterns
- `agent:main:telegram:*` → "telegram"
- `agent:main:main` → "dashboard" 
- `agent:main:webchat:*` → "webchat"
- `agent:main:cron:*` → "cron-[name]"

## Integration with OpenClaw Control UI
If the Control UI supports custom session labels, this skill can generate a configuration file for it.