#!/bin/bash
# Start E5 RAG HTTP Service for OpenClaw Integration

set -e

# Configuration
HOST="${1:-localhost}"
PORT="${2:-8000}"
WORKSPACE_DIR="/home/ubuntu/.openclaw/workspace"
VENV_DIR="$WORKSPACE_DIR/.venv-embeddings"
SERVICE_PID_FILE="/tmp/e5_rag_service.pid"
LOG_FILE="$WORKSPACE_DIR/logs/e5_rag_service.log"

echo "🚀 Starting E5 RAG HTTP Service for OpenClaw"
echo "============================================"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workspace: $WORKSPACE_DIR"
echo ""

# Create logs directory
mkdir -p "$WORKSPACE_DIR/logs"

# Check if service is already running
if [ -f "$SERVICE_PID_FILE" ]; then
    PID=$(cat "$SERVICE_PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "⚠️  E5 RAG service is already running (PID: $PID)"
        echo "   To restart, run: $0 --restart"
        exit 1
    else
        echo "⚠️  Stale PID file found, removing..."
        rm -f "$SERVICE_PID_FILE"
    fi
fi

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "🔧 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Virtual environment not found: $VENV_DIR"
    echo "   Please run: python3 -m venv $VENV_DIR"
    echo "   Then install dependencies from requirements.txt"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import sentence_transformers; import torch; print('✅ Sentence Transformers available'); print('✅ PyTorch available')" 2>/dev/null || {
    echo "❌ Missing dependencies"
    echo "   Installing from requirements.txt..."
    pip install -r "$WORKSPACE_DIR/requirements.txt" 2>&1 | tail -20
}

# Start the HTTP service in background
echo "🚀 Starting HTTP service on http://$HOST:$PORT..."
cd "$WORKSPACE_DIR"

# Run service in background
python3 e5_rag_http_service.py --host "$HOST" --port "$PORT" --background > "$LOG_FILE" 2>&1 &

# Save PID
SERVICE_PID=$!
echo "$SERVICE_PID" > "$SERVICE_PID_FILE"

echo "✅ Service started with PID: $SERVICE_PID"
echo "📝 Logs: $LOG_FILE"
echo ""

# Wait a moment for service to start
sleep 3

# Test the service
echo "🧪 Testing service connectivity..."
curl -s "http://$HOST:$PORT/status" > /tmp/service_test.json 2>/dev/null

if [ $? -eq 0 ]; then
    STATUS=$(python3 -c "import json; data=json.load(open('/tmp/service_test.json')); print(data.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "✅ Service is responding (status: $STATUS)"
else
    echo "⚠️  Service may not be fully started yet"
    echo "   Check logs: tail -f $LOG_FILE"
fi

echo ""
echo "🔗 OpenClaw Configuration:"
echo "=========================="
cat << EOF
Add to your OpenClaw config:

"memorySearch": {
  "provider": "http",
  "endpoint": "http://$HOST:$PORT/search",
  "timeout": 10000,
  "retries": 2
}

Or use the pre-made config:
cp $WORKSPACE_DIR/openclaw_e5_rag_config.json ~/.openclaw/config.json
EOF

echo ""
echo "📋 Available endpoints:"
echo "  GET  http://$HOST:$PORT/              - Service info"
echo "  GET  http://$HOST:$PORT/status        - Service status"
echo "  GET  http://$HOST:$PORT/stats         - Memory statistics"
echo "  GET  http://$HOST:$PORT/search?q=query - Search (GET)"
echo "  POST http://$HOST:$PORT/search        - Search (JSON)"
echo "  POST http://$HOST:$PORT/update        - Update embeddings"
echo "  POST http://$HOST:$PORT/initialize    - Initialize service"
echo ""
echo "🛑 To stop the service:"
echo "  kill $SERVICE_PID"
echo "  or"
echo "  ./stop_e5_rag_service.sh"
echo ""
echo "📊 To test search:"
echo "  curl 'http://$HOST:$PORT/search?q=OpenClaw%20system'"
echo "  or"
echo "  curl -X POST http://$HOST:$PORT/search -H 'Content-Type: application/json' -d '{\"query\":\"memory system\"}'"
echo ""
echo "============================================"
echo "✅ E5 RAG HTTP Service ready for OpenClaw integration"
echo "   Semantic memory search via HTTP API"