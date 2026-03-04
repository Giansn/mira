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

### ~~Memory Graph Maintenance (every 5 heartbeats ~2.5 hours)~~ **NOW HANDLED BY DAILY CRON JOB**
- **Cron job**: `0 20 * * *` (8 PM UTC / 3 PM Colombia time)
- **Script**: `/home/ubuntu/.openclaw/workspace/organize_langgraph_daily.sh`
- **Logs**: `/home/ubuntu/.openclaw/logs/langgraph-daily-YYYY-MM-DD.log`
- **Tasks (now automated daily):**
  - Update semantic embeddings for new memories
  - Compute relationships between memory chunks  
  - Extract tags and keywords from recent content
  - Generate memory health report
  - Flag stale memory files (>7 days without updates)
- **Integration:** LangGraph + sentence-transformers (intfloat/e5-small-v2)
- **Expected output:** Memory summary with stats and recommendations

**Note:** This task has been automated via cron job. Manual heartbeat execution no longer needed.

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

### Cron Job Health Monitoring (every 3 heartbeats ~1.5 hours)
- **LangGraph Daily Job**: Check if running successfully
- **Method**: Check latest log file for errors
- **Check**: `tail -5 /home/ubuntu/.openclaw/logs/langgraph-daily-$(date +%Y-%m-%d).log 2>/dev/null | grep -E "(ERROR|failed|✗)"`
- **If errors found**: Report in heartbeat, check exit code in log
- **If successful**: Verify "completed successfully" message in log
- **Next scheduled run**: 2026-03-04 8 PM UTC (3 PM Colombia time)

### Continuous LangGraph-E5 Sync (every 5 heartbeats ~2.5 hours)
- **Script**: `/home/ubuntu/.openclaw/workspace/langgraph_e5_sync.py`
- **Command**: `python3 /home/ubuntu/.openclaw/workspace/langgraph_e5_sync.py --sync --timeout 30`
- **Tasks**:
  - Check for changed memory files since last sync
  - If changes detected AND LangGraph available, sync embeddings to E5 cache
  - If LangGraph loading times out (>30s), skip and log warning
  - Update sync state file with results
  - Log sync statistics and E5 cache age
- **Integration**: On-the-run sync system with incremental updates
- **Expected output**: Sync completed or skipped with reason, E5 cache age < 3 hours
- **Failure handling**: If sync fails 3 times in a row, alert in heartbeat
- **State file**: `/home/ubuntu/.openclaw/workspace/memory/embeddings/sync_state.json`
