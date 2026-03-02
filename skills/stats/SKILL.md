---
name: stats
user-invocable: true
description: Show a compact system + session overview including disk, RAM, swap, thesis files, workspace size, sub-agent status, hardware info, and API/TPS metrics.
---

# Stats Skill

When invoked via `/stats`, run the enhanced stats script and return a compact summary.

## Steps

1. Run: `bash /home/ubuntu/.openclaw/workspace/scripts/stats.sh`
2. Format the output as a clean, compact reply
3. Append current model + context size from session_status if available

## Output Sections

The script outputs these sections:
- **HARDWARE**: Host, kernel, CPU model, cores, RAM, swap, disk
- **SYSTEM**: Uptime, load average
- **GATEWAY**: Gateway status (bind, port, auth)
- **MODEL & API**: Current model, reasoning enabled, TPS measurement
- **OPENCLAW STATUS**: Version, Node.js, pending approvals, session count
- **THESIS**: Latest thesis file, modification date, word count
- **WORKSPACE**: Size, file count, skill count

## Output format

Reply in plain text, compact, no markdown tables. Group by section with a single blank line between sections.
