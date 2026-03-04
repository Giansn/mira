#!/bin/bash
# Moltbook Daily Agent - Fixed Version
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
echo "$(date): Starting Moltbook agent (fixed version)" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log

# Try to get agent info
curl -s https://www.moltbook.com/api/v1/home -H "Authorization: Bearer $MOLTBOOK_API_KEY" > /tmp/moltbook-response.json 2>&1
CURL_EXIT=$?

if [ $CURL_EXIT -eq 0 ]; then
    # Check if response is valid JSON
    if jq -e . /tmp/moltbook-response.json >/dev/null 2>&1; then
        echo "API response received successfully" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        
        # Extract and log useful information
        AGENT_NAME=$(jq -r '.your_account.name // "unknown"' /tmp/moltbook-response.json 2>/dev/null)
        AGENT_KARMA=$(jq -r '.your_account.karma // "0"' /tmp/moltbook-response.json 2>/dev/null)
        UNREAD_NOTIFICATIONS=$(jq -r '.your_account.unread_notification_count // "0"' /tmp/moltbook-response.json 2>/dev/null)
        UNREAD_DMS=$(jq -r '.your_direct_messages.unread_message_count // "0"' /tmp/moltbook-response.json 2>/dev/null)
        PENDING_REQUESTS=$(jq -r '.your_direct_messages.pending_request_count // "0"' /tmp/moltbook-response.json 2>/dev/null)
        POSTS_WITH_NOTIFICATIONS=$(jq -r '.activity_on_your_posts | length // 0' /tmp/moltbook-response.json 2>/dev/null)
        FOLLOWING_COUNT=$(jq -r '.posts_from_accounts_you_follow.total_following // "0"' /tmp/moltbook-response.json 2>/dev/null)
        
        echo "Agent: $AGENT_NAME" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Karma: $AGENT_KARMA" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Unread notifications: $UNREAD_NOTIFICATIONS" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Posts with new activity: $POSTS_WITH_NOTIFICATIONS" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Unread DMs: $UNREAD_DMS" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Pending DM requests: $PENDING_REQUESTS" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Following: $FOLLOWING_COUNT accounts" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        
        # Log what_to_do_next suggestions (first 2)
        echo "Suggested actions:" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        jq -r '.what_to_do_next[0:2] | .[]' /tmp/moltbook-response.json 2>/dev/null | while read line; do
            echo "  - $line" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        done
        
        # Check for promotional content in feed
        PROMO_COUNT=$(jq -r '.posts_from_accounts_you_follow.posts[] | select(.author_name | contains("cybercentry")) | .author_name' /tmp/moltbook-response.json 2>/dev/null | wc -l)
        if [ "$PROMO_COUNT" -gt 0 ]; then
            echo "Promotional content detected: $PROMO_COUNT posts from cybercentry (skipped per policy)" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        fi
        
        echo "Status: SUCCESS - Agent data retrieved" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
    else
        echo "Invalid JSON response" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        # Log first 200 chars of response for debugging
        head -c 200 /tmp/moltbook-response.json >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
        echo "Status: ERROR - Invalid JSON" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
    fi
else
    echo "API request failed (curl exit code: $CURL_EXIT)" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
    echo "Status: ERROR - API request failed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
fi

# Clean up
rm -f /tmp/moltbook-response.json

# Log completion
echo "$(date): Moltbook agent completed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log