---
name: hot-workspace
version: 1.1.0
description: Hybrid disk+RAM workspace optimization. Pre-warm kernel cache, monitor access patterns.
homepage: https://github.com/openclaw/hot-workspace
metadata: {"category": "performance", "platform": "linux"}
---

# Hot Workspace

Hybrid disk+RAM workspace optimization for OpenClaw. Pre-warms kernel file cache and monitors access patterns. Based on 77-branch swarm simulation.

## Quick Start

```bash
# Load frequently-accessed files into RAM (recommended)
hot-workspace prewarm

# Monitor file access patterns
hot-workspace monitor

# Status
hot-workspace status
```

## Why This Design (from 77-branch swarm)

| Configuration | Score | Verdict |
|--------------|-------|---------|
| monitor-only | 0.832 | ✅ Win |
| prewarm-cat | 0.832 | ✅ Win |
| prewarm-fadvise | 0.829 | ✅ Win |
| scratch-tmp | 0.738 | ⚠️ Optional |
| scratch-devshm | 0.691 | ❌ Skip |

**Key insight:** Scratch/tmpfs adds complexity without proportional benefit. Prewarm + monitor = best safety/speed tradeoff.

## Commands

### prewarm

Load frequently-accessed workspace files into kernel cache.

```bash
hot-workspace prewarm
```

Files: thesis*.md, memory/*.md, AGENTS.md, SOUL.md, USER.md, TOOLS.md

### monitor

Track file access patterns to learn which files to pre-warm.

```bash
hot-workspace monitor
```

Log format: `timestamp file_path access_count`

### status

Show hot-workspace status.

```bash
hot-workspace status
```

## Configuration

```yaml
prewarm:
  enabled: true
  patterns:
    - "thesis*.md"
    - "memory/*.md"
    - "AGENTS.md"
    - "SOUL.md"
    - "USER.md"
    - "TOOLS.md"

monitor:
  enabled: true
  log_file: ".hot-workspace-access.log"

# Scratch is disabled by default (low value per swarm)
scratch:
  enabled: false
```

## Philosophy

- Workspace stays on disk (safety)
- Pre-warm on startup = instant cache hits
- Monitor to learn access patterns over time
- Scratch disabled — too much risk, too little gain
