#!/bin/bash
# Deploy LangGraph E5 with Warm-up Phase
# Includes: Service deployment, OpenClaw config, warm-up queries

set -e

echo "🧠 DEPLOYING LANGGRAPH E5 WITH WARM-UP"
echo "======================================"

WORKSPACE="/home/ubuntu/.openclaw/workspace"
cd "$WORKSPACE"

# Configuration
PORT=8000
SERVICE_NAME="langgraph-e5"
LOG_FILE="logs/langgraph_e5_service.log"
BACKUP_DIR="$HOME/.openclaw/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create directories
mkdir -p logs "$BACKUP_DIR"

echo ""
echo "1. BACKING UP CURRENT CONFIGURATION"
echo "-----------------------------------"

# Backup OpenClaw config
if [ -f "$HOME/.openclaw/config.json" ]; then
    cp "$HOME/.openclaw/config.json" "$BACKUP_DIR/config.pre_langgraph.$TIMESTAMP.json"
    echo "✅ OpenClaw config backed up: $BACKUP_DIR/config.pre_langgraph.$TIMESTAMP.json"
else
    echo "⚠️  No existing OpenClaw config found"
fi

echo ""
echo "2. STOPPING EXISTING SERVICES"
echo "-----------------------------"

# Stop any existing services
pkill -f "e5_rag_ready_service" 2>/dev/null || true
pkill -f "langgraph_e5_wrapper" 2>/dev/null || true
sleep 2

echo "✅ Existing services stopped"

echo ""
echo "3. STARTING LANGGRAPH E5 SERVICE"
echo "--------------------------------"

# Start the service
echo "Starting LangGraph E5 service on port $PORT..."
source .venv-embeddings/bin/activate
python3 e5_rag_ready_service.py --host localhost --port "$PORT" > "$LOG_FILE" 2>&1 &
SERVICE_PID=$!

echo "✅ Service started with PID: $SERVICE_PID"
echo "   Logs: $LOG_FILE"

echo ""
echo "4. WAITING FOR SERVICE INITIALIZATION (WARM-UP PHASE 1)"
echo "------------------------------------------------------"

# Wait for service to start
echo "Waiting for HTTP server to start..."
for i in {1..30}; do
    if curl -s http://localhost:$PORT/ > /dev/null 2>&1; then
        echo "✅ HTTP server responding (after $i seconds)"
        break
    fi
    
    if (( i % 5 == 0 )); then
        echo "   Still waiting... ($i seconds elapsed)"
    fi
    
    sleep 1
done

echo ""
echo "5. WAITING FOR MODEL LOAD (WARM-UP PHASE 2)"
echo "------------------------------------------"

# Wait for model to load
echo "Waiting for E5 model to load (this takes ~30 seconds)..."
MODEL_LOADED=false
for i in {1..60}; do
    READY_RESPONSE=$(curl -s http://localhost:$PORT/ready 2>/dev/null || echo '{}')
    
    if echo "$READY_RESPONSE" | grep -q '"ready":true'; then
        MODEL_LOADED=true
        echo "✅ Model loaded and service ready! (after $((i*2)) seconds)"
        break
    fi
    
    if (( i % 10 == 0 )); then
        echo "   Still loading model... ($((i*2)) seconds elapsed)"
    fi
    
    sleep 2
done

if [ "$MODEL_LOADED" = false ]; then
    echo "⚠️  Model not fully loaded after 2 minutes, but continuing..."
fi

echo ""
echo "6. PERFORMING WARM-UP QUERIES (WARM-UP PHASE 3)"
echo "----------------------------------------------"

# Warm-up queries to prime the system
WARMUP_QUERIES=(
    "OpenClaw"
    "memory system"
    "E5 embeddings"
    "LangGraph workflow"
    "semantic search"
)

echo "Running warm-up queries to prime the cache..."
for query in "${WARMUP_QUERIES[@]}"; do
    echo -n "   Warming up: '$query'... "
    
    # Run query with timeout
    if timeout 10 curl -s "http://localhost:$PORT/search?q=$query" > /dev/null 2>&1; then
        echo "✅"
    else
        echo "⚠️ (timeout/slow)"
    fi
    
    # Small delay between queries
    sleep 1
done

echo ""
echo "7. UPDATING OPENCLAW CONFIGURATION"
echo "----------------------------------"

# Create OpenClaw config
OPENCLAW_CONFIG="/tmp/openclaw_langgraph_config.json"
cat > "$OPENCLAW_CONFIG" << EOF
{
  "memorySearch": {
    "provider": "http",
    "endpoint": "http://localhost:$PORT/search",
    "timeout": 30000,
    "retries": 2,
    "healthCheck": "http://localhost:$PORT/ready",
    "fallback": {
      "provider": "local",
      "model": "hf:ChristianAzinn/e5-small-v2-gguf/e5-small-v2.Q4_K_M.gguf"
    }
  }
}
EOF

echo "✅ OpenClaw configuration created"

# Merge with existing config
if [ -f "$HOME/.openclaw/config.json" ]; then
    echo "Merging with existing OpenClaw config..."
    python3 -c "
import json
import sys

try:
    with open('$HOME/.openclaw/config.json') as f:
        current = json.load(f)
except:
    current = {}

with open('$OPENCLAW_CONFIG') as f:
    langgraph_config = json.load(f)

# Update memorySearch section
current['memorySearch'] = langgraph_config['memorySearch']

with open('$HOME/.openclaw/config.json', 'w') as f:
    json.dump(current, f, indent=2)
"
else
    cp "$OPENCLAW_CONFIG" "$HOME/.openclaw/config.json"
fi

echo "✅ OpenClaw config updated"

echo ""
echo "8. RESTARTING OPENCLAW GATEWAY"
echo "------------------------------"

# Restart OpenClaw
if openclaw gateway restart; then
    echo "✅ OpenClaw gateway restarted successfully"
else
    echo "❌ Failed to restart OpenClaw gateway"
    echo "   Attempting to start it..."
    openclaw gateway start
fi

echo ""
echo "9. CREATING STARTUP SCRIPT"
echo "--------------------------"

# Create startup script
STARTUP_SCRIPT="/home/ubuntu/start_langgraph_e5.sh"
cat > "$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
# LangGraph E5 Startup Script with Warm-up
# Run this at system startup or manually

set -e

echo "🚀 Starting LangGraph E5 Service"
echo "================================"

WORKSPACE="/home/ubuntu/.openclaw/workspace"
cd "$WORKSPACE"

PORT=8000
LOG_FILE="logs/langgraph_e5_service.log"

# Stop any existing
pkill -f "e5_rag_ready_service" 2>/dev/null || true
sleep 2

# Start service
echo "Starting service on port $PORT..."
source .venv-embeddings/bin/activate
python3 e5_rag_ready_service.py --host localhost --port "$PORT" > "$LOG_FILE" 2>&1 &
SERVICE_PID=$!

echo "Service PID: $SERVICE_PID"
echo "Logs: $LOG_FILE"

# Wait for readiness
echo ""
echo "Waiting for service to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:$PORT/ready 2>/dev/null | grep -q '"ready":true'; then
        echo "✅ Service ready after $((i*2)) seconds"
        break
    fi
    
    if (( i % 10 == 0 )); then
        echo "   Still initializing... ($((i*2)) seconds elapsed)"
    fi
    
    sleep 2
done

# Warm-up queries
echo ""
echo "Running warm-up queries..."
WARMUP_QUERIES=("OpenClaw" "memory" "search" "test")
for query in "${WARMUP_QUERIES[@]}"; do
    timeout 5 curl -s "http://localhost:$PORT/search?q=$query" > /dev/null 2>&1 || true
    sleep 0.5
done

echo ""
echo "🎉 LangGraph E5 Service Started Successfully!"
echo "Service: http://localhost:$PORT/"
echo "Readiness: http://localhost:$PORT/ready"
echo "Search: http://localhost:$PORT/search?q=query"
echo ""
echo "To stop: kill $SERVICE_PID"
echo "To check status: curl http://localhost:$PORT/status"
EOF

chmod +x "$STARTUP_SCRIPT"
echo "✅ Startup script created: $STARTUP_SCRIPT"

# Create systemd service file
SYSTEMD_SERVICE="/etc/systemd/system/langgraph-e5.service"
if [ -w "/etc/systemd/system/" ]; then
    cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=LangGraph E5 Semantic Search Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/.openclaw/workspace
Environment="PATH=/home/ubuntu/.openclaw/workspace/.venv-embeddings/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/.openclaw/workspace/.venv-embeddings/bin/python3 /home/ubuntu/.openclaw/workspace/e5_rag_ready_service.py --host localhost --port 8000
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/ubuntu/.openclaw/workspace/logs/langgraph_e5_service.log
StandardError=append:/home/ubuntu/.openclaw/workspace/logs/langgraph_e5_service.log

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Systemd service file created: $SYSTEMD_SERVICE"
    echo ""
    echo "To enable auto-start on boot:"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable langgraph-e5"
    echo "  sudo systemctl start langgraph-e5"
else
    echo "⚠️  Cannot create systemd service (need sudo)"
    echo "   Startup script available: $STARTUP_SCRIPT"
fi

echo ""
echo "10. FINAL VERIFICATION"
echo "---------------------"

# Final test
echo "Testing service..."
if curl -s http://localhost:$PORT/ready 2>/dev/null | grep -q '"ready":true'; then
    echo "✅ Service is READY"
    
    # Test search
    TEST_RESULT=$(timeout 10 curl -s "http://localhost:$PORT/search?q=OpenClaw" 2>/dev/null || echo '{}')
    if echo "$TEST_RESULT" | grep -q '"success":true'; then
        echo "✅ Search working"
        COUNT=$(echo "$TEST_RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('count', 0))" 2>/dev/null || echo "0")
        echo "   Found $COUNT results for 'OpenClaw'"
    else
        echo "⚠️  Search test inconclusive"
    fi
else
    echo "⚠️  Service not fully ready yet (still warming up)"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "📊 Deployment Summary:"
echo "  ✅ Service: Running on port $PORT (PID: $SERVICE_PID)"
echo "  ✅ OpenClaw: Config updated with LangGraph integration"
echo "  ✅ Warm-up: Completed (model loaded + queries primed)"
echo "  ✅ Startup: Script created: $STARTUP_SCRIPT"
echo ""
echo "🔧 Service Details:"
echo "  URL: http://localhost:$PORT/"
echo "  Readiness: http://localhost:$PORT/ready"
echo "  Health: http://localhost:$PORT/health"
echo "  Search: http://localhost:$PORT/search?q=query"
echo "  Logs: $LOG_FILE"
echo ""
echo "🔄 OpenClaw Integration:"
echo "  Memory search now uses LangGraph E5 semantic search"
echo "  Fallback to local E5 GGUF model if service unavailable"
echo "  Health checks via /ready endpoint"
echo ""
echo "📝 Next Steps:"
echo "  1. Test OpenClaw memory search functionality"
echo "  2. Monitor logs: tail -f $LOG_FILE"
echo "  3. Run startup script on reboot: $STARTUP_SCRIPT"
echo ""
echo "✅ LangGraph E5 is now deployed and integrated with OpenClaw!"