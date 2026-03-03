#!/bin/bash
# Stop E5 RAG HTTP Service

set -e

SERVICE_PID_FILE="/tmp/e5_rag_service.pid"
WORKSPACE_DIR="/home/ubuntu/.openclaw/workspace"

echo "🛑 Stopping E5 RAG HTTP Service"
echo "==============================="

if [ -f "$SERVICE_PID_FILE" ]; then
    PID=$(cat "$SERVICE_PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping process $PID..."
        kill "$PID"
        
        # Wait for process to terminate
        for i in {1..10}; do
            if kill -0 "$PID" 2>/dev/null; then
                sleep 1
            else
                break
            fi
        done
        
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            echo "Force killing process $PID..."
            kill -9 "$PID"
        fi
        
        rm -f "$SERVICE_PID_FILE"
        echo "✅ Service stopped"
    else
        echo "⚠️  Process $PID not running"
        rm -f "$SERVICE_PID_FILE"
    fi
else
    echo "⚠️  No PID file found. Trying to find and kill process..."
    
    # Try to find and kill the service
    PIDS=$(ps aux | grep "e5_rag_http_service.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "Found processes: $PIDS"
        for PID in $PIDS; do
            echo "Killing process $PID..."
            kill "$PID" 2>/dev/null || true
        done
        echo "✅ Service processes stopped"
    else
        echo "✅ No running service found"
    fi
fi

echo ""
echo "📝 Last 10 lines of log:"
tail -10 "$WORKSPACE_DIR/logs/e5_rag_service.log" 2>/dev/null || echo "No log file found"

echo ""
echo "To restart:"
echo "  cd $WORKSPACE_DIR"
echo "  ./start_e5_rag_service.sh"