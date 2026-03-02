# HEARTBEAT.md

## Active Tasks

### Moltbook (daily at 9 AM UTC)
- Cron job: `0 9 * * *` (daily 9 AM UTC)
- Agent: zai/glm-4.7-flash (free)
- Budget: **10000 tokens** (max)
- **Tasks:**
  - Check agent status
  - Browse feed, engage (follow/comment/upvote if interesting)
  - Check notifications and DMs
  - Report summary
- **Skip:** Promotional content, marketing, sales pitches, crypto/token minting
- **Cron:** `0 9 * * *`

### Memory Graph Maintenance (every 5 heartbeats ~2.5 hours)
- Run: `python3 /home/ubuntu/.openclaw/workspace/memory_heartbeat.py --summary`
- **Tasks:**
  - Update semantic embeddings for new memories
  - Compute relationships between memory chunks
  - Extract tags and keywords from recent content
  - Generate memory health report
  - Flag stale memory files (>7 days without updates)
- **Integration:** LangGraph + sentence-transformers (all-MiniLM-L6-v2)
- **Expected output:** Memory summary with stats and recommendations

### Self-Maintenance (every 10 heartbeats ~5 hours)
- Review memory/YYYY-MM-DD.md files, distill key takeaways to MEMORY.md
- Prune outdated entries from MEMORY.md
- Check for unused/skipped files in workspace, flag for cleanup
- Review recent decisions, reflect on what worked/didn't
- Update skills/SOUL.md if I learned something new about myself

### Async Agent Pattern Processing (every heartbeat)
- Run: `python3 /home/ubuntu/.openclaw/workspace/skills/async-agent-pattern/process_queue.py --type claude --max 3`
- **Tasks:**
  - Process queued Claude messages (2 minute timeout per message)
  - Process browser automation requests (when browser available)
  - Process background jobs (10 minute timeout per job)
  - Process API calls (service-specific timeouts)
- **Integration:** Externalizes state for session-fragile operations
- **Expected output:** Operations completed, results stored, state checkpoints updated

### Telegram Rate Limit Monitoring
- Check recent Telegram session logs (last 30 lines) for "rate limit reached" errors
- If rate limit detected:
  1. Log timestamp in /tmp/rate-limit-detected.txt
  2. Send alert to Telegram: "Switched to Open Router (rate limit detected)"
  3. Use openrouter/anthropic-claude-sonnet-4-6 for all subsequent Telegram responses
  4. Continue with Open Router until March 1 (monthly reset)
- If no rate limit: Clear fallback state, continue using primary Anthropic key
