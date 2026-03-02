#!/bin/bash
# Simple heartbeat script for dashboard session

echo "Dashboard Session Heartbeat"
echo "==========================="
date
echo "Gateway URL: http://127.0.0.1:18789/"
echo "Dashboard URL: http://127.0.0.1:18789/#token=1f3c0559f9362ff5ff458c69eed348f6df5a7ec55bbc1287"
echo "Session ID: agent:main:subagent:d6ce8d75-79c6-4b38-aff3-8ddfe4853246"
echo "Status: Active and ready for dashboard/webchat conversations"

# Check if gateway is responding
if curl -s http://127.0.0.1:18789/ > /dev/null; then
    echo "Gateway: ✓ Running"
else
    echo "Gateway: ✗ Not responding"
fi