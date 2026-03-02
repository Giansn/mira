#!/bin/bash
# Status: Show hot-workspace status

WORKSPACE="${WORKSPACE:-/home/ubuntu/.openclaw/workspace}"

echo "=== Hot Workspace Status ==="

# Prewarm status
echo ""
echo "--- Prewarm Status ---"
PREWARM_COUNT=$(find "$WORKSPACE" -maxdepth 1 \( -name "thesis*.md" -o -name "AGENTS.md" -o -name "SOUL.md" -o -name "USER.md" -o -name "TOOLS.md" -o -name "HEARTBEAT.md" \) 2>/dev/null | wc -l)
echo "Hot files in workspace: $PREWARM_COUNT"

# Scratch status
echo ""
echo "--- Scratch Space ---"
if [ -n "$HOT_SCRATCH" ]; then
    echo "Scratch directory: $HOT_SCRATCH"
    if [ -d "$HOT_SCRATCH" ]; then
        SCRATCH_SIZE=$(du -sh "$HOT_SCRATCH" 2>/dev/null | cut -f1)
        SCRATCH_FILES=$(find "$HOT_SCRATCH" -type f 2>/dev/null | wc -l)
        echo "Current usage: $SCRATCH_SIZE with $SCRATCH_FILES files"
    else
        echo "Status: Not initialized"
    fi
else
    echo "Scratch directory: Not set (run 'scratch' command)"
fi

# Memory status
echo ""
echo "--- Memory ---"
if [ -f /proc/meminfo ]; then
    echo "Kernel cache (Cached): $(grep '^Cached:' /proc/meminfo | awk '{print $2}')KB"
    echo "Available: $(grep '^MemAvailable:' /proc/meminfo | awk '{print $2}')KB"
    echo "Free: $(grep '^MemFree:' /proc/meminfo | awk '{print $2}')KB"
fi

echo ""
echo "======================"
