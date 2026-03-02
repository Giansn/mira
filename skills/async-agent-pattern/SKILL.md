---
name: async-agent-pattern
description: "Implements the async job-state pattern from Moltbook post: externalize intent, process via cron/heartbeat, store results for session-fragile operations"
---

# Async Agent Pattern Skill

## Overview

Implements the architectural pattern described in the Moltbook post "Async scan results broke my naive agent pattern — here's what I rebuilt". Solves session-fragility for:

1. **Claude CLI conversations** - Instead of maintaining interactive terminal sessions
2. **Browser automation** - Notion bridge and other web interactions
3. **Long-running tasks** - Memory graph maintenance, data processing
4. **External API calls** - Moltbook, ScrapeSense, and other async APIs

## Core Pattern

**Problem:** Agent sessions are fragile. Long-running operations break on:
- Session timeouts
- Model switches
- System restarts
- Network interruptions

**Solution:** Externalize state, design for idempotent resumption:

```
Intent → Queue → Checkpoint → Process → Store → Resume
```

## Components

### 1. Message Queue System
- **Location:** `queue/` directory
- **Format:** JSONL (one JSON object per line)
- **Types:** `claude`, `browser`, `job`, `api`

### 2. State Checkpoint Files
- **Location:** `state/` directory  
- **Purpose:** Track workflow position, not just memory
- **Schema:** Exact fields for each operation type

### 3. Processing Engine
- **Scripts:** `process_queue.py` (main processor)
- **Cron integration:** Runs via heartbeat or scheduled jobs
- **Idempotent:** Can be interrupted and resumed safely

### 4. Results Storage
- **Location:** `results/` directory
- **Format:** Structured by operation type and timestamp
- **Integration:** With main memory system (`MEMORY.md`)

## Implementation

### Queue File Format (JSONL)

```json
{"id": "claude_001", "type": "claude", "message": "Hello Claude", "timestamp": "2026-03-02T05:10:00Z", "status": "pending"}
{"id": "browser_001", "type": "browser", "action": "notion_screenshot", "url": "https://notion.so/...", "timestamp": "2026-03-02T05:11:00Z", "status": "pending"}
{"id": "job_001", "type": "job", "name": "memory_graph", "command": "python3 memory_heartbeat.py --summary", "timestamp": "2026-03-02T05:12:00Z", "status": "pending"}
```

### State Checkpoint Format

```json
{
  "pending_operations": [
    {
      "id": "claude_001",
      "type": "claude",
      "message": "Hello Claude",
      "submitted_at": "2026-03-02T05:10:00Z",
      "last_checked": null,
      "status": "pending",
      "purpose": "test_integration"
    }
  ],
  "completed_operations": [],
  "failed_operations": []
}
```

## Usage

### 1. Add to Queue

```python
from skills.async_agent_pattern.queue_manager import QueueManager

queue = QueueManager()
queue.add_claude_message("Test message for Claude")
queue.add_browser_action("notion_screenshot", {"url": "https://notion.so/..."})
queue.add_job("memory_graph", "python3 memory_heartbeat.py --summary")
```

### 2. Process Queue (via cron/heartbeat)

```bash
# Manual processing
python3 skills/async-agent-pattern/scripts/process_queue.py

# Via heartbeat (add to HEARTBEAT.md)
python3 skills/async-agent-pattern/scripts/process_queue.py --type claude
python3 skills/async-agent-pattern/scripts/process_queue.py --type browser
python3 skills/async-agent-pattern/scripts/process_queue.py --type job
```

### 3. Check Results

```python
from skills.async_agent_pattern.results_manager import ResultsManager

results = ResultsManager()
claude_responses = results.get_claude_responses(limit=10)
browser_results = results.get_browser_results()
job_outputs = results.get_job_outputs()
```

## Integration Points

### With Claude Code
- Messages queued instead of direct CLI calls
- Processed via `claude --print` in controlled sessions
- Responses stored and integrated into conversation flow

### With Browser Automation
- Screenshot requests queued
- Processed when browser is available
- Images stored with metadata

### With Long-running Tasks
- Jobs queued with dependencies
- Processed in isolation
- Progress checkpoints maintained

### With Memory System
- Results feed into `MEMORY.md`
- Daily logs capture async operations
- Semantic connections maintained

## Example Workflows

### Claude Conversation Flow
```
User asks question → Queue Claude message → Heartbeat processes → Store response → User reads response
```

### Browser Automation Flow  
```
Need Notion screenshot → Queue browser action → Next available session processes → Store image → Use in documentation
```

### Job Processing Flow
```
Memory graph needed → Queue job → Cron processes → Store results → Update visualization
```

## Benefits

1. **Session Resilience:** Survives restarts, timeouts, interruptions
2. **Resource Efficiency:** No hanging terminal sessions
3. **Better UX:** User gets responses when ready, not blocked on processing
4. **Scalability:** Multiple operations can be queued and batched
5. **Debugging:** Complete audit trail of queued → processed → stored

## Inspired By

Moltbook post: "Async scan results broke my naive agent pattern — here's what I rebuilt" by juliaopenclaw.

Key insight: "Externalize the state. Write it to a file immediately after submission. Then your agent can terminate. A subsequent run picks up the state file, checks job status, and processes results if ready."

## Next Steps

1. Implement `queue_manager.py`
2. Implement `process_queue.py` 
3. Integrate with heartbeat system
4. Test with Claude conversations
5. Extend to browser automation
6. Document patterns for other skill developers