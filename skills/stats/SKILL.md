---
name: stats
user-invocable: true
description: Show a compact system + session overview including disk, RAM, swap, thesis files, workspace size, and sub-agent status.
---

# Stats Skill

When invoked via `/stats`, run the stats script and return a compact summary.

## Steps

1. Run: `bash /home/ubuntu/.openclaw/workspace/scripts/stats.sh`
2. Format the output as a clean, compact reply
3. Append current model + context size from session_status if available

## Output format

Reply in plain text, compact, no markdown tables. Group by section with a single blank line between sections.
