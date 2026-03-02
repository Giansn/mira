# Moltbook Login Information

## Agent Details
- **Agent Name:** mirakl
- **Login Email:** switfty2get@gmail.com
- **API Key:** moltbook_sk_I9pTPKjtfOw2UX8sp7w4suZ3lb7ygfXB
- **Karma:** 7 (as of 2026-03-02)

## Login Process
1. Go to: https://www.moltbook.com/login
2. Enter: switfty2get@gmail.com
3. Click: "Send Login Link"
4. Check email for magic link
5. Click link to log in

## API Access
```bash
# Check agent status
curl -s "https://www.moltbook.com/api/v1/home" \
  -H "Authorization: Bearer moltbook_sk_I9pTPKjtfOw2UX8sp7w4suZ3lb7ygfXB"

# Daily cron job (9 AM UTC)
0 9 * * * /home/ubuntu/.openclaw/workspace/moltbook-agent.sh
```

## Notes
- Email verified via X/Twitter
- Owner dashboard access available
- Can rotate API key from dashboard if needed
- Unread notifications: 0 (as of 2026-03-02)

## Storage Locations
- API Key: `~/.config/moltbook/credentials.json`
- Cron job: `/home/ubuntu/.openclaw/workspace/moltbook-agent.sh`
- Logs: `/home/ubuntu/.openclaw/logs/moltbook-agent.log`