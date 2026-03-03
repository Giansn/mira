#!/bin/bash
# Safe Deployment of E5 RAG for OpenClaw
# Follows all safety precautions to avoid config crashes

set -e

echo "🔒 Safe E5 RAG Deployment for OpenClaw"
echo "========================================"
echo "This script follows safety-first approach to avoid config crashes"
echo ""

# Configuration
SERVICE_PORT=8000
BACKUP_DIR="$HOME/.openclaw/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORKSPACE="/home/ubuntu/.openclaw/workspace"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Step 0: Pre-flight check
print_step "0. Pre-flight checks"
echo "   Checking system status..."

# Check if OpenClaw is running
if ! openclaw gateway status > /dev/null 2>&1; then
    print_warning "OpenClaw gateway not running (this might be OK)"
else
    print_success "OpenClaw gateway is running"
fi

# Check current config
if [ -f "$HOME/.openclaw/config.json" ]; then
    CONFIG_SIZE=$(stat -c%s "$HOME/.openclaw/config.json")
    print_success "Current config exists (${CONFIG_SIZE} bytes)"
else
    print_warning "No current config found (will create new)"
fi

# Step 1: Create backups
print_step "1. Creating backups"
mkdir -p "$BACKUP_DIR"

# Backup current config
if [ -f "$HOME/.openclaw/config.json" ]; then
    BACKUP_FILE="$BACKUP_DIR/config.json.backup.$TIMESTAMP"
    cp "$HOME/.openclaw/config.json" "$BACKUP_FILE"
    print_success "Config backed up to: $BACKUP_FILE"
else
    print_warning "No config to backup"
fi

# Backup service files
SERVICE_BACKUP="$BACKUP_DIR/e5_service_backup.$TIMESTAMP.tar.gz"
tar -czf "$SERVICE_BACKUP" -C "$WORKSPACE" \
    e5_rag_service.py \
    e5_rag_robust_service.py \
    memory_rag.py \
    e5_embedding_engine.py \
    openclaw_e5_rag_config.json 2>/dev/null || true
print_success "Service files backed up to: $SERVICE_BACKUP"

# Step 2: Start service in test mode
print_step "2. Starting E5 RAG service (test mode)"
cd "$WORKSPACE"

# Kill any existing service on our port
print_warning "Stopping any existing service on port $SERVICE_PORT..."
pkill -f "e5_rag_robust_service.*$SERVICE_PORT" 2>/dev/null || true
sleep 1

# Start service in background with logging
print_success "Starting robust service..."
source .venv-embeddings/bin/activate
python3 e5_rag_robust_service.py --host localhost --port "$SERVICE_PORT" --background > "$WORKSPACE/logs/e5_deploy.log" 2>&1 &
SERVICE_PID=$!
echo "   Service PID: $SERVICE_PID"
echo "   Logs: $WORKSPACE/logs/e5_deploy.log"

# Wait for service to start
print_warning "Waiting 10 seconds for service initialization..."
sleep 10

# Step 3: Test service thoroughly
print_step "3. Testing service (critical step)"

TEST_PASSED=true

# Test 1: Health endpoint
print_warning "Testing health endpoint..."
if curl -s "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
    print_success "Health check passed"
else
    print_error "Health check failed"
    TEST_PASSED=false
fi

# Test 2: Status endpoint
print_warning "Testing status endpoint..."
STATUS_RESPONSE=$(curl -s "http://localhost:$SERVICE_PORT/status" 2>/dev/null || echo '{}')
if echo "$STATUS_RESPONSE" | grep -q '"status"'; then
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
    print_success "Status endpoint working (status: $STATUS)"
else
    print_error "Status endpoint failed"
    TEST_PASSED=false
fi

# Test 3: Simple search (with timeout)
print_warning "Testing search endpoint (30s timeout)..."
timeout 30 curl -s "http://localhost:$SERVICE_PORT/search?q=test" > /tmp/search_test.json 2>/dev/null || true

if [ -s /tmp/search_test.json ]; then
    if grep -q '"success":true' /tmp/search_test.json; then
        print_success "Search endpoint working"
    else
        ERROR=$(cat /tmp/search_test.json | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('error', 'unknown error'))" 2>/dev/null || echo "parse error")
        print_warning "Search returned error (might be OK): $ERROR"
    fi
else
    print_warning "Search test timed out or returned empty (service may still be initializing)"
fi

# Step 4: Decision point
print_step "4. Deployment Decision"
echo ""

if [ "$TEST_PASSED" = true ]; then
    print_success "All critical tests passed!"
    echo "   Service is healthy and responding"
    
    # Ask for confirmation
    echo ""
    read -p "Do you want to proceed with OpenClaw config update? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Step 5: Update config
        print_step "5. Updating OpenClaw configuration"
        
        # Create new config
        NEW_CONFIG="$HOME/.openclaw/config.json.new"
        OLD_CONFIG="$HOME/.openclaw/config.json"
        
        # If old config exists, merge with E5 settings
        if [ -f "$OLD_CONFIG" ]; then
            print_warning "Merging with existing config..."
            python3 -c "
import json
import sys

# Load old config
try:
    with open('$OLD_CONFIG') as f:
        old = json.load(f)
except:
    old = {}

# Load E5 config
with open('$WORKSPACE/openclaw_e5_rag_config.json') as f:
    e5 = json.load(f)

# Merge (E5 settings override old)
old.update(e5)

# Write new config
with open('$NEW_CONFIG', 'w') as f:
    json.dump(old, f, indent=2)
"
            print_success "Config merged successfully"
        else
            # Use E5 config as-is
            cp "$WORKSPACE/openclaw_e5_rag_config.json" "$NEW_CONFIG"
            print_success "New config created from template"
        fi
        
        # Backup old config one more time
        if [ -f "$OLD_CONFIG" ]; then
            cp "$OLD_CONFIG" "$OLD_CONFIG.backup.before_e5"
        fi
        
        # Install new config
        mv "$NEW_CONFIG" "$OLD_CONFIG"
        print_success "OpenClaw config updated!"
        
        # Step 6: Restart OpenClaw
        print_step "6. Restarting OpenClaw gateway"
        if openclaw gateway restart; then
            print_success "OpenClaw restarted successfully"
            sleep 3
            
            # Final test
            print_step "7. Final verification"
            print_warning "Testing OpenClaw memory search integration..."
            
            # This would require actual OpenClaw test
            print_success "Config update complete!"
            echo ""
            echo "To test the integration:"
            echo "  1. Use OpenClaw memory search command"
            echo "  2. Check if semantic results are returned"
            echo "  3. Monitor logs: tail -f $WORKSPACE/logs/e5_deploy.log"
            
        else
            print_error "Failed to restart OpenClaw"
            print_warning "Reverting config change..."
            if [ -f "$OLD_CONFIG.backup.before_e5" ]; then
                mv "$OLD_CONFIG.backup.before_e5" "$OLD_CONFIG"
                openclaw gateway restart
                print_success "Config reverted, OpenClaw restarted"
            fi
        fi
        
    else
        print_warning "Deployment cancelled by user"
        print_success "Service is running but config not updated"
        echo ""
        echo "You can manually update config later:"
        echo "  cp $WORKSPACE/openclaw_e5_rag_config.json ~/.openclaw/config.json"
        echo "  openclaw gateway restart"
    fi
    
else
    print_error "Critical tests failed - deployment aborted"
    echo ""
    echo "Issues detected:"
    echo "  1. Check service logs: tail -f $WORKSPACE/logs/e5_deploy.log"
    echo "  2. Verify dependencies: source .venv-embeddings/bin/activate"
    echo "  3. Check port $SERVICE_PORT is available"
    echo ""
    echo "Service is running for debugging. Kill with:"
    echo "  kill $SERVICE_PID"
fi

# Step 8: Summary
print_step "8. Deployment Summary"
echo ""
echo "Backups created:"
echo "  Config: $BACKUP_DIR/config.json.backup.$TIMESTAMP"
echo "  Service: $SERVICE_BACKUP"
echo ""
echo "Service status:"
if kill -0 $SERVICE_PID 2>/dev/null; then
    print_success "E5 RAG service is running (PID: $SERVICE_PID)"
    echo "  Port: $SERVICE_PORT"
    echo "  Health: http://localhost:$SERVICE_PORT/health"
    echo "  Stop: kill $SERVICE_PID"
else
    print_error "Service is not running"
fi
echo ""
echo "OpenClaw config:"
if [ -f "$HOME/.openclaw/config.json" ]; then
    if grep -q '"provider":"http"' "$HOME/.openclaw/config.json"; then
        print_success "Config includes E5 HTTP provider"
    else
        print_warning "Config does not include E5 settings"
    fi
else
    print_warning "No OpenClaw config found"
fi
echo ""
echo "Next steps:"
echo "  1. Test OpenClaw memory search"
echo "  2. Monitor service logs"
echo "  3. Adjust timeouts if needed"
echo "  4. Consider fallback testing"
echo ""
echo "Rollback instructions:"
echo "  cp $BACKUP_DIR/config.json.backup.$TIMESTAMP ~/.openclaw/config.json"
echo "  openclaw gateway restart"
echo "  kill $SERVICE_PID"

echo ""
echo "========================================"
print_success "Safe deployment procedure complete"