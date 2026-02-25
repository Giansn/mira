# HEARTBEAT.md

## Active Tasks

### Telegram Rate Limit Monitoring
- Check recent Telegram session logs (last 30 lines) for "rate limit reached" errors
- If rate limit detected:
  1. Log timestamp in /tmp/rate-limit-detected.txt
  2. Send alert to Telegram: "Switched to Open Router (rate limit detected)"
  3. Use openrouter/anthropic-claude-sonnet-4-6 for all subsequent Telegram responses
  4. Continue with Open Router until March 1 (monthly reset)
- If no rate limit: Clear fallback state, continue using primary Anthropic key
