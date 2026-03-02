#!/bin/bash
# Moltbook Daily Agent
# Runs daily at 9 AM UTC to check Moltbook activity
# Uses secure API manager for encrypted key storage

# Set environment
export PATH=/home/ubuntu/.npm-global/bin:$PATH

# Get API key from secure storage
SECURE_MANAGER="/home/ubuntu/.openclaw/workspace/secure-api-manager.sh"
if [ -f "$SECURE_MANAGER" ]; then
    export MOLTBOOK_API_KEY=$(bash "$SECURE_MANAGER" decrypt moltbook 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$MOLTBOOK_API_KEY" ]; then
        echo "ERROR: Failed to decrypt Moltbook API key" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        exit 1
    fi
else
    # Fallback to old credentials file
    export MOLTBOOK_API_KEY=$(jq -r '.moltbook.api_key' ~/.config/moltbook/credentials.json 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$MOLTBOOK_API_KEY" ]; then
        echo "ERROR: No API key found" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        exit 1
    fi
fi

# Log start
echo "$(date): Starting Moltbook agent" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log

# Simple Moltbook check - verify API works and log status
echo "Moltbook API test:" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log

# Try to get agent info
curl -s https://www.moltbook.com/api/v1/home -H "Authorization: Bearer $MOLTBOOK_API_KEY" > /tmp/moltbook-response.json 2>&1

if [ $? -eq 0 ]; then
    # Check if response is valid JSON
    if jq -e . /tmp/moltbook-response.json >/dev/null 2>&1; then
        # Extract relevant info
        echo "Response received:" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        jq '. | {statusCode, message, error} // {success: true}' /tmp/moltbook-response.json >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
    else
        echo "Invalid JSON response" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        cat /tmp/moltbook-response.json | head -c 200 >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
    fi
else
    echo "API request failed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
fi

# Clean up
rm -f /tmp/moltbook-response.json

# Log completion
echo "$(date): Moltbook agent completed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log