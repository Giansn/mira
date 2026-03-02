#!/bin/bash
# Prewarm: Load frequently-accessed files into kernel cache

WORKSPACE="${WORKSPACE:-/home/ubuntu/.openclaw/workspace}"

# Files to prewarm (by pattern)
PREWARM_PATTERNS=(
    "thesis*.md"
    "memory/*.md"
    "AGENTS.md"
    "SOUL.md"
    "USER.md"
    "TOOLS.md"
    "HEARTBEAT.md"
)

echo "Prewarming workspace files..."

count=0
for pattern in "${PREWARM_PATTERNS[@]}"; do
    for file in $WORKSPACE/$pattern; do
        if [ -f "$file" ]; then
            # Read file into kernel cache (discard output)
            cat "$file" > /dev/null 2>&1
            echo "  Prewarmed: ${file#$WORKSPACE/}"
            count=$((count + 1))
        fi
    done
done

echo "Prewarmed $count files into kernel cache."

# Show cache stats
if [ -f /proc/meminfo ]; then
    cached=$(grep '^Cached:' /proc/meminfo | awk '{print $2}')
    echo "Kernel cache (Cached): ${cached}KB"
fi
