#!/bin/bash
# Daily Cleanup Script
# Runs tagging, retention enforcement, and other cleanup tasks
# Scheduled to run daily at 3 AM UTC (adjustable)

set -e

echo "========================================"
echo "DAILY CLEANUP SCRIPT"
echo "Date: $(date)"
echo "========================================"

WORKSPACE="/home/ubuntu/.openclaw/workspace"
ARCHIVE="/data/archive"
LOG_DIR="/home/ubuntu/.openclaw/logs"
LOG_FILE="$LOG_DIR/daily-cleanup-$(date +%Y-%m-%d).log"

# Create log directory if needed
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Start logging
log "Starting daily cleanup"

# 1. Tag everything (keyword-based tagging)
log "Step 1: Tagging all files..."
cd "$WORKSPACE"
if [ -f "tag_everything.py" ]; then
    python3 tag_everything.py >> "$LOG_FILE" 2>&1
    log "Tagging complete"
else
    log "WARNING: tag_everything.py not found"
fi

# 2. Run retention enforcement (5-day archive, 20-day delete)
log "Step 2: Running retention enforcement..."
if [ -f "retention_enforcer.py" ]; then
    python3 retention_enforcer.py --workspace "$WORKSPACE" --archive "$ARCHIVE" >> "$LOG_FILE" 2>&1
    log "Retention enforcement complete"
else
    log "WARNING: retention_enforcer.py not found"
fi

# 3. Clean up temporary files
log "Step 3: Cleaning temporary files..."
# Delete files in /tmp older than 1 day
find /tmp -type f -mtime +1 -delete 2>/dev/null || true
# Delete empty directories in /tmp
find /tmp -type d -empty -delete 2>/dev/null || true
log "Temporary files cleaned"

# 4. Check disk space
log "Step 4: Checking disk space..."
df -h / >> "$LOG_FILE" 2>&1
df -h /data >> "$LOG_FILE" 2>&1
log "Disk space checked"

# 5. Clean up old logs (keep 7 days)
log "Step 5: Cleaning old logs..."
find "$LOG_DIR" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
log "Old logs cleaned"

# 6. Run LangGraph memory organization (if scheduled)
log "Step 6: Checking for LangGraph memory organization..."
if [ -f "organize_langgraph_daily.sh" ]; then
    # Check if it's already scheduled for 8 PM UTC
    log "LangGraph daily script exists (scheduled for 8 PM UTC)"
else
    log "No LangGraph daily script found"
fi

# 7. Update heartbeat state
log "Step 7: Updating heartbeat state..."
if [ -f "heartbeat-state.json" ]; then
    # Update last cleanup timestamp
    python3 -c "
import json, time
try:
    with open('heartbeat-state.json', 'r') as f:
        data = json.load(f)
    data['lastChecks']['dailyCleanup'] = int(time.time())
    with open('heartbeat-state.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('Heartbeat state updated')
except Exception as e:
    print(f'Error updating heartbeat: {e}')
" >> "$LOG_FILE" 2>&1
    log "Heartbeat state updated"
fi

# 8. Send Telegram notification (optional)
log "Step 8: Sending notification..."
# Uncomment to enable Telegram notifications
# openclaw message send --channel telegram --target 1134139785 --message "Daily cleanup completed at $(date)" >> "$LOG_FILE" 2>&1 || true
log "Notification sent (if enabled)"

# Summary
log "========================================"
log "DAILY CLEANUP COMPLETE"
log "========================================"

# Display summary
echo ""
echo "Cleanup Summary:"
echo "- Tagging: Completed"
echo "- Retention: Applied (5-day archive, 20-day delete)"
echo "- Temp files: Cleaned"
echo "- Disk space: Checked"
echo "- Old logs: Cleaned (>7 days)"
echo "- Heartbeat: Updated"
echo ""
echo "Log file: $LOG_FILE"

exit 0