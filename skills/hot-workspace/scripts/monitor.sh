#!/bin/bash
# Monitor: Track file access patterns

WORKSPACE="${WORKSPACE:-/home/ubuntu/.openclaw/workspace}"
LOG_FILE="${WORKSPACE}/.hot-workspace-access.log"

echo "=== Hot Workspace Monitor ==="
echo "Tracking file access in: $WORKSPACE"
echo "Log file: $LOG_FILE"
echo ""

# Track access patterns using inotify (if available)
if command -v inotifywait &> /dev/null; then
    echo "Using inotify for real-time tracking..."
    inotifywait -m -r -e access -e open "$WORKSPACE" 2>/dev/null | while read -r directory events filename; do
        timestamp=$(date +%Y-%m-%dT%H:%M:%S)
        echo "$timestamp $filename" >> "$LOG_FILE"
    done &
    echo "Monitor running in background (PID: $!)"
else
    echo "inotify not available. Taking snapshot..."
    find "$WORKSPACE" -type f -name "*.md" -o -name "*.py" -o -name "*.json" 2>/dev/null | while read -r f; do
        timestamp=$(date +%Y-%m-%dT%H:%M:%S)
        echo "$timestamp ${f#$WORKSPACE/}" >> "$LOG_FILE"
    done
    echo "Snapshot saved to $LOG_FILE"
fi

# Show top accessed files
echo ""
echo "--- Top Accessed Files ---"
if [ -f "$LOG_FILE" ]; then
    awk '{print $2}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -10
else
    echo "No access log yet"
fi
