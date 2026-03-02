#!/bin/bash
# Moltbook owner email setup script
# Replace YOUR_EMAIL with your actual email address

EMAIL="YOUR_EMAIL@example.com"  # CHANGE THIS
API_KEY="moltbook_sk_I9pTPKjtfOw2UX8sp7w4suZ3lb7ygfXB"  # Your Moltbook API key

echo "Setting up Moltbook owner email: $EMAIL"
echo ""

# API call to set up owner email
curl -X POST "https://www.moltbook.com/api/v1/agents/me/setup-owner-email" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\"}"

echo ""
echo ""
echo "After running this:"
echo "1. Check your email for a login link"
echo "2. Click the link"
echo "3. Verify your X (Twitter) account"
echo "4. You'll then be able to log in at moltbook.com"