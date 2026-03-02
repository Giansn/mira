# Session Manager

A clean solution to OpenClaw's confusing session management.

## The Problem
OpenClaw creates session keys like `agent:main:telegram:slash:1134139785`. Users want simple names like "telegram" and "dashboard". The web control UI shows duplicate sessions with the same name.

## The Solution
This session manager provides:
1. **Human-readable session names** - Map internal keys to simple names
2. **Session cleanup** - Remove old, duplicate sessions automatically
3. **Clear visibility** - See exactly what sessions exist and what they're for

## Quick Start

### 1. List current sessions
```bash
./session-manager/list-sessions
```

### 2. Clean up old sessions
```bash
./session-manager/cleanup-sessions
```

### 3. Check the session mapping
```bash
cat session-manager/session-map.json
```

## How It Works

### Source-Based Session Identification
The new system identifies sessions by their source (domain/origin):

1. **entrosana.com** - Main dashboard sessions from the entrosana.com domain
2. **telegram** - Telegram messaging sessions  
3. **webchat** - Webchat interface sessions
4. **cron** - Automated cron job sessions

### Session Mapping
The `session-map.json` file now includes:
- Direct session name mapping
- Source pattern matching
- Session protection rules

```json
{
  "sessions": {
    "telegram": "agent:main:telegram:slash:1134139785",
    "entrosana-dashboard": "agent:main:main",
    "telegram-legacy": "telegram:slash:1134139785"
  },
  "source_mapping": {
    "entrosana.com": {
      "patterns": ["agent:main:main"],
      "description": "Main dashboard from entrosana.com domain"
    },
    "telegram": {
      "patterns": ["agent:main:telegram:*", "telegram:*"],
      "description": "Telegram messaging sessions"
    }
  }
}
```

### Key Improvement
The main dashboard session (`agent:main:main`) is now properly identified as coming from **entrosana.com**, not just a generic "dashboard". This solves the confusion of seeing "two sessions called Gianluca" - one is your Telegram session, the other is the entrosana.com dashboard session.

### Session Cleanup
The cleanup script:
1. Creates backups before making changes
2. Keeps protected sessions (from the mapping)
3. Keeps sessions less than 24 hours old
4. Removes old, duplicate sessions

## Integration with OpenClaw Control UI

If you're using the OpenClaw Control UI (like the HTML interface you shared), this manager helps you understand what sessions it's creating and clean them up regularly.

## Common Issues & Solutions

### Issue: "Two sessions called Gianluca"
**Solution**: Run `./cleanup-sessions`. The web UI might create duplicate sessions that need cleaning.

### Issue: Session names are confusing
**Solution**: Use `./list-sessions` to see the mapping between internal keys and human names.

### Issue: Too many old sessions
**Solution**: Set up a cron job to run `./cleanup-sessions` daily.

## Setting Up Daily Cleanup
Add to crontab:
```bash
0 2 * * * /home/ubuntu/.openclaw/workspace/session-manager/cleanup-sessions
```

## Files
- `SKILL.md` - Skill documentation
- `session-map.json` - Session name mapping
- `list-sessions` - List sessions with human names
- `cleanup-sessions` - Clean up old sessions
- `README.md` - This file

## Notes
- Always creates backups before cleaning
- Never deletes protected sessions
- Keeps recent sessions (<24h) even if not protected
- Run cleanup regularly to prevent session buildup