# PC Terminal TODO

## OpenClaw Config
- [ ] Find correct key for exec approval timeout (cat ~/.openclaw/openclaw.json), then set it to ~2 minutes
- [ ] Set up gateway-level message blocking for unknown senders after N prompts (hard enforcement, not just Mira self-silencing)

## Backups
- [ ] Set up regular automated backup of workspace .md files (cron job or git)

## System Cleanup
- [ ] Run disk/cache sweep (df -h, du -sh /tmp ~/.cache ~/.npm /var/log /var/cache)
- [ ] Clean unnecessary files in workspace
