#!/bin/bash
# Activate: Run prewarm + scratch

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Activating Hot Workspace ==="

# Run prewarm
echo ""
echo "--- Prewarming ---"
bash "$SCRIPT_DIR/prewarm.sh"

# Set up scratch
echo ""
echo "--- Scratch Space ---"
eval "$(bash "$SCRIPT_DIR/scratch.sh")"

echo ""
echo "=== Hot Workspace Active ==="
