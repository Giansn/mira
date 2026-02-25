#!/bin/bash
# Monitor for Anthropic rate limits and switch to Open Router fallback

LOG_FILE="/tmp/openclaw/openclaw-2026-02-23.log"
STATE_FILE="/tmp/rate-limit-fallback-active.state"

# Check if rate limit was hit in the last 2 minutes
if tail -100 "$LOG_FILE" 2>/dev/null | grep -q "rate limit reached"; then
    if [ ! -f "$STATE_FILE" ]; then
        # First time detecting rate limit - activate fallback
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Rate limit detected. Switching to Open Router." >> /tmp/rate-limit-log.txt
        touch "$STATE_FILE"
        
        # Notify via sending to main session (if possible)
        # For now, just log it
        exit 0
    fi
else
    # No rate limit detected - clear state
    rm -f "$STATE_FILE"
fi
