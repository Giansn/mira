---
name: notion-browser-bridge
description: "Access Notion pages via browser automation when API access isn't available. Use when: (1) Notion page requires authentication but API integration is complex, (2) Need to read/write to Notion without OAuth setup, (3) Quick access to Notion content via browser control, (4) Notion's new API (post-2025-09-03) requires public OAuth integration which is overkill for internal use."
---

# Notion Browser Bridge

## Overview

This skill enables browser-based access to Notion pages when API integration isn't practical. After Notion's September 2025 API changes, creating simple internal integrations with `secret_` tokens is no longer possible—all new integrations require public OAuth flow. This skill provides an alternative using OpenClaw's browser automation capabilities.

## When to Use This Approach

**Use browser automation when:**
- You need quick, one-time access to a Notion page
- Setting up OAuth integration is overkill for your use case
- The page is already accessible via browser (you're logged in)
- You need to read content or make simple edits

**Use Notion API when:**
- You need programmatic, scalable access
- You can set up OAuth integration
- You need to create/update databases programmatically
- You're building a production integration

## Setup Requirements

### 1. Browser Configuration

OpenClaw needs a browser profile with remote debugging enabled. The `brave-remote` profile works well:

```bash
# Check if brave-remote profile exists
openclaw browser status --browser-profile brave-remote

# If not, configure it in openclaw.json:
# "browser": {
#   "profiles": {
#     "brave-remote": {
#       "cdpUrl": "http://127.0.0.1:9223",
#       "color": "#FF0000"
#     }
#   }
# }
```

### 2. Start Browser with Remote Debugging

Launch Brave with remote debugging:
```bash
brave-browser --remote-debugging-port=9223 --user-data-dir=/tmp/brave-profile
```

Or use an existing browser instance that has remote debugging enabled.

## Core Workflow

### 1. Connect to Notion Page

```javascript
// Using browser tool
browser({
  action: "open",
  profile: "brave-remote",
  targetUrl: "https://www.notion.so/Your-Page-ID"
})
```

### 2. Read Page Content

```javascript
// Take snapshot to understand page structure
browser({
  action: "snapshot",
  profile: "brave-remote",
  targetId: "TARGET_ID_FROM_OPEN_RESPONSE"
})
```

### 3. Interact with Elements

```javascript
// Click on links or buttons
browser({
  action: "act",
  profile: "brave-remote",
  targetId: "TARGET_ID",
  request: {
    kind: "click",
    ref: "e126" // Reference from snapshot
  }
})
```

## Common Patterns

### Pattern 1: Read Notion Table

Many Notion pages use tables for project tracking. After taking a snapshot:

1. Look for `table` elements in the snapshot
2. Extract row and cell data from the structured output
3. Map to your local project structure

### Pattern 2: Navigate Linked Pages

Notion pages often link to subpages. To access them:

1. Find link elements in the snapshot (look for `link` refs)
2. Click on the link using its ref
3. Wait for navigation, then snapshot the new page

### Pattern 3: Sync to Local Files

Create a sync workflow between Notion and local files (like PROJECT.md):

1. Read Notion content via browser
2. Parse and structure the data
3. Update local markdown files
4. Optionally: Push changes back to Notion by typing into editable fields

## Troubleshooting

### Issue: "Profile not found"
**Solution:** Ensure the browser profile is configured in `openclaw.json` and the browser is running with remote debugging.

### Issue: "Can't reach browser control service"
**Solution:** Check if the gateway is running (`openclaw gateway status`). Restart if needed.

### Issue: Notion page requires login
**Solution:** Ensure you're already logged into Notion in the browser instance before automation.

### Issue: Elements not found in snapshot
**Solution:** Use `refs: "aria"` in snapshot for more stable element references:
```javascript
browser({
  action: "snapshot",
  profile: "brave-remote",
  targetId: "TARGET_ID",
  refs: "aria"
})
```

## Security Considerations

1. **Authentication:** The browser session uses your existing Notion login. Don't share the browser profile.
2. **Rate limiting:** Notion may rate limit browser interactions. Add delays between actions.
3. **Data privacy:** Only access pages you have permission to view.

## Example: MA Kooperation Page Sync

Today's successful implementation:

1. **Page:** `https://www.notion.so/MA-Kooperation-3165477ed88480cbbee8e7d1a91b50fe`
2. **Content:** Project tracking table with deadlines, costs, bonuses
3. **Structure:** Table → Rows → Cells with project details
4. **Sync:** Extracted to PROJECT.md under "Ghostwriting" section

## References

See `references/notion_patterns.md` for detailed element patterns and common Notion page structures.
