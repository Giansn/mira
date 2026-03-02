#!/bin/bash
# Moltbook Daily Agent
# Runs daily at 9 AM UTC to check Moltbook activity

# Set environment
export PATH=/home/ubuntu/.npm-global/bin:$PATH
export MOLTBOOK_API_KEY=$(jq -r '.moltbook.api_key' ~/.config/moltbook/credentials.json)

# Log start
echo "$(date): Starting Moltbook agent" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log

# Simple Moltbook check - just verify API works and log status
echo "Moltbook API test:" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
curl -s https://www.moltbook.com/api/v1/home -H "Authorization: Bearer $MOLTBOOK_API_KEY" | jq '.your_account' >> /home/ubuntu/.openclaw/logs/moltbook-agent.log 2>&1 || echo "API check failed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log

# Log completion
echo "$(date): Moltbook agent completed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log