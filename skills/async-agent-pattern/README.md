# Async Agent Pattern

Implements the architectural pattern from the Moltbook post "Async scan results broke my naive agent pattern — here's what I rebuilt".

## Problem

Agent sessions are fragile. Long-running operations break on:
- Session timeouts
- Model switches  
- System restarts
- Network interruptions

## Solution

Externalize state, design for idempotent resumption:
```
Intent → Queue → Checkpoint → Process → Store → Resume
```

## Architecture

### Queue System
- JSONL files for different operation types
- Atomic append operations
- Timestamp ordering

### State Checkpoints
- Exact workflow position tracking
- Not just associative memory
- Schema-enforced consistency

### Processing Engine  
- Idempotent operations
- Configurable timeouts (Claude: 120s, Jobs: 600s)
- Heartbeat/cron integration

### Results Storage
- Structured by operation type
- Integrated with main memory system
- Cleanup policies

## Usage

### Queue Operations
```python
from queue_manager import QueueManager

queue = QueueManager()
queue.add_claude_message("Hello Claude", purpose="test")
queue.add_browser_action("screenshot", {"url": "https://example.com"})
queue.add_job("memory_graph", "python3 memory_heartbeat.py --summary")
queue.add_api_call("moltbook", "/api/v1/home", "GET")
```

### Process Queue
```bash
# Process all operations (max 10)
python3 process_queue.py

# Process specific type (max 5)
python3 process_queue.py --type claude --max 3

# Show statistics
python3 process_queue.py --stats

# Cleanup old results
python3 process_queue.py --cleanup 7
```

### Heartbeat Integration
Added to `HEARTBEAT.md`:
```markdown
### Async Agent Pattern Processing (every heartbeat)
- Run: `python3 skills/async-agent-pattern/process_queue.py --type claude --max 3`
```

## Timeout Configuration

- **Claude messages:** 120 seconds (2 minutes)
- **Browser actions:** Service-dependent
- **Background jobs:** 600 seconds (10 minutes)  
- **API calls:** Service-specific

Adjust in `process_queue.py` if needed.

## Inspired By

Moltbook post by `juliaopenclaw`: "Async scan results broke my naive agent pattern — here's what I rebuilt".

Key insight: "Externalize the state. Write it to a file immediately after submission. Then your agent can terminate. A subsequent run picks up the state file, checks job status, and processes results if ready."

## Benefits

1. **Session Resilience:** Survives restarts, timeouts, interruptions
2. **Resource Efficiency:** No hanging terminal sessions
3. **Better UX:** Responses when ready, not blocked on processing
4. **Scalability:** Queue and batch multiple operations
5. **Debugging:** Complete audit trail

## Examples

See `examples/basic_usage.py` for complete workflows.

## Next Steps

1. **Enhanced dependency tracking** between operations
2. **Priority queues** for urgent vs background operations
3. **Webhook integration** for immediate processing
4. **Dashboard** for monitoring queue status
5. **Integration tests** for reliability validation