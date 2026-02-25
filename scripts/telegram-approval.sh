#!/bin/bash
# telegram-approval.sh
# Sends an approval request via Telegram inline buttons, waits for response.
# Usage: telegram-approval.sh "<command_description>" "<command_to_run>"
# Requires: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment or ~/.openclaw/.private/telegram-approval.env

ENV_FILE="$HOME/.openclaw/.private/telegram-approval.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set."
  exit 1
fi

DESCRIPTION="${1:-Unknown command}"
COMMAND="${2:-echo 'no command'}"
APPROVAL_ID="$(date +%s)-$$"
STATE_FILE="/tmp/tg-approval-$APPROVAL_ID.state"

# Send approval request with inline buttons
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"$TELEGRAM_CHAT_ID\",
    \"text\": \"Approval request:\n\`$DESCRIPTION\`\n\nID: $APPROVAL_ID\",
    \"reply_markup\": {
      \"inline_keyboard\": [[
        {\"text\": \"Grant\", \"callback_data\": \"grant-$APPROVAL_ID\"},
        {\"text\": \"Deny\", \"callback_data\": \"deny-$APPROVAL_ID\"}
      ]]
    }
  }")

MSG_ID=$(echo "$RESPONSE" | grep -o '"message_id":[0-9]*' | head -1 | cut -d: -f2)

echo "Waiting for Telegram approval (ID: $APPROVAL_ID)..."
echo "pending" > "$STATE_FILE"

# Poll for callback response (max 5 minutes)
OFFSET=0
DEADLINE=$(($(date +%s) + 300))

while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  UPDATES=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=$OFFSET&timeout=30")
  
  # Check for our callback
  if echo "$UPDATES" | grep -q "grant-$APPROVAL_ID"; then
    echo "approved" > "$STATE_FILE"
    # Acknowledge callback
    CB_ID=$(echo "$UPDATES" | grep -o '"id":"[0-9]*"' | head -1 | cut -d'"' -f4)
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/answerCallbackQuery" \
      -d "callback_query_id=$CB_ID&text=Granted" > /dev/null
    break
  elif echo "$UPDATES" | grep -q "deny-$APPROVAL_ID"; then
    echo "denied" > "$STATE_FILE"
    CB_ID=$(echo "$UPDATES" | grep -o '"id":"[0-9]*"' | head -1 | cut -d'"' -f4)
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/answerCallbackQuery" \
      -d "callback_query_id=$CB_ID&text=Denied" > /dev/null
    break
  fi

  # Advance offset to avoid re-reading
  LAST_ID=$(echo "$UPDATES" | grep -o '"update_id":[0-9]*' | tail -1 | cut -d: -f2)
  [ -n "$LAST_ID" ] && OFFSET=$((LAST_ID + 1))
  
  sleep 2
done

STATE=$(cat "$STATE_FILE")
rm -f "$STATE_FILE"

if [ "$STATE" = "approved" ]; then
  echo "Approved. Executing..."
  eval "$COMMAND"
  exit $?
else
  echo "Denied or timed out. Command not executed."
  exit 1
fi
