#!/bin/bash
# Daily LangGraph Memory Organization (3 PM Colombia / 8 PM UTC)
# Because even AIs need to clean their rooms occasionally.
# Sends Telegram "library sorted" notification on success.

LOG_DIR="/home/ubuntu/.openclaw/logs"
LOG_FILE="$LOG_DIR/langgraph-daily-$(date +%Y-%m-%d).log"
WORKSPACE="/home/ubuntu/.openclaw/workspace"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "=== LangGraph Daily Organization $(date) ===" | tee -a "$LOG_FILE"

# Activate the virtual environment (where langgraph actually lives)
if [ -f "$WORKSPACE/.venv-embeddings/bin/activate" ]; then
    source "$WORKSPACE/.venv-embeddings/bin/activate"
    echo "✓ Virtual environment activated" | tee -a "$LOG_FILE"
else
    echo "✗ ERROR: Virtual environment not found at $WORKSPACE/.venv-embeddings" | tee -a "$LOG_FILE"
    exit 1
fi

# Change to workspace directory
cd "$WORKSPACE" || {
    echo "✗ ERROR: Cannot cd to $WORKSPACE" | tee -a "$LOG_FILE"
    exit 1
}

echo "Running memory heartbeat with full analysis..." | tee -a "$LOG_FILE"

# Run the full analysis (not just summary)
python3 memory_heartbeat.py --analyze 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ LangGraph organization completed successfully" | tee -a "$LOG_FILE"
    
    # Extract key stats from log
    echo "" | tee -a "$LOG_FILE"
    echo "=== Quick Summary ===" | tee -a "$LOG_FILE"
    tail -20 "$LOG_FILE" | grep -E "(total_memories|total_tags|recommendations|avg_connections)" | head -5 | tee -a "$LOG_FILE"
    
    # Send Telegram notification on success
    echo "Sending Telegram notification..." | tee -a "$LOG_FILE"
    /home/ubuntu/.npm-global/bin/openclaw message send --channel telegram --target 1134139785 --message "library sorted" 2>&1 | tee -a "$LOG_FILE"
    echo "Telegram notification sent" | tee -a "$LOG_FILE"
else
    echo "✗ ERROR: LangGraph organization failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"
    echo "Check $LOG_FILE for details" | tee -a "$LOG_FILE"
fi

echo "=== Completion $(date) ===" | tee -a "$LOG_FILE"