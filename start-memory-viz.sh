#!/bin/bash
# Start Memory Visualization Web Interface

cd /home/ubuntu/.openclaw/workspace/memory-viz

echo "========================================="
echo "OpenClaw Memory Visualization Interface"
echo "========================================="
echo ""
echo "Starting web server..."
echo "Access at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Check if already running
if curl -s http://localhost:5000/api/stats > /dev/null 2>&1; then
    echo "Server is already running on http://localhost:5000"
    echo "You can access it now."
    exit 0
fi

# Start the server
python3 app.py