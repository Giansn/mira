---
name: external-terminal-access
description: "Access external terminals and web interfaces through links and shared sessions"
---

# External Terminal Access Skill

## Overview

This skill enables access to external terminals, web interfaces, and shared sessions through various protocols and tools.

## Current Capabilities

### 1. SSH Terminal Access
- **Port:** 22 (already open)
- **User:** ubuntu
- **Host:** 172.31.14.61
- **Status:** Accessible via Termius, OpenSSH, etc.

### 2. Claude Code Terminal
- **Command:** `claude`
- **Status:** Installed and configured
- **Workspace:** `/home/ubuntu/.openclaw/workspace` (trusted)
- **Access:** Direct terminal interaction

### 3. Web Interfaces
- **OpenClaw Control UI:** `http://172.31.14.61:18789/`
- **Memory Visualization:** `http://172.31.14.61:5000/` (if running)
- **Browser Control:** Brave on port 9223 (CDP)

## Tools Needed

### 1. Link Processing Tool
```python
#!/usr/bin/env python3
"""
Process Termius/terminal sharing links and extract connection details.
"""

import re
import urllib.parse

def parse_termius_link(link):
    """Parse Termius multiplayer link."""
    parsed = urllib.parse.urlparse(link)
    query = urllib.parse.parse_qs(parsed.query)
    
    return {
        'peer_id': query.get('peerId', [''])[0],
        'terminal_title': query.get('terminalTitle', [''])[0],
        'connection_id': query.get('connectionId', [''])[0],
        'version': query.get('version', [''])[0],
        'pwd': query.get('pwd', [''])[0]
    }

def generate_ssh_command(details):
    """Generate SSH command from connection details."""
    return f"ssh ubuntu@172.31.14.61"
```

### 2. Terminal Session Manager
```python
#!/usr/bin/env python3
"""
Manage external terminal sessions.
"""

import subprocess
import time

class TerminalSession:
    def __init__(self):
        self.sessions = {}
    
    def start_claude_session(self):
        """Start Claude Code terminal session."""
        cmd = ["claude"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        session_id = f"claude_{int(time.time())}"
        self.sessions[session_id] = process
        return session_id
    
    def send_to_session(self, session_id, message):
        """Send input to terminal session."""
        if session_id in self.sessions:
            process = self.sessions[session_id]
            process.stdin.write(message + "\n")
            process.stdin.flush()
            return True
        return False
```

### 3. Web Interface Controller
```python
#!/usr/bin/env python3
"""
Control web interfaces via browser automation.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By

class WebInterface:
    def __init__(self):
        self.driver = None
    
    def connect_to_openclaw_ui(self):
        """Connect to OpenClaw Control UI."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("http://172.31.14.61:18789/")
        return self.driver.title
    
    def interact_with_ui(self, element_id, action, value=None):
        """Interact with UI elements."""
        if not self.driver:
            return "No active driver"
        
        element = self.driver.find_element(By.ID, element_id)
        if action == "click":
            element.click()
        elif action == "type" and value:
            element.send_keys(value)
        
        return "Action completed"
```

## Integration Methods

### Method 1: Direct SSH + Claude
```bash
# Connect via SSH
ssh ubuntu@172.31.14.61

# Start Claude
claude

# Or in one command
ssh ubuntu@172.31.14.61 -t "claude"
```

### Method 2: Termius Multiplayer
1. Share Termius link with connection details
2. Others join via Termius app
3. Shared terminal session
4. Run `claude` in shared terminal

### Method 3: WebSocket Terminal
```python
# Could implement WebSocket terminal server
import asyncio
import websockets

async def terminal_server(websocket, path):
    async for message in websocket:
        # Process terminal commands
        result = await run_command(message)
        await websocket.send(result)
```

## Setup Instructions

### 1. Install Dependencies
```bash
# Python packages
pip install selenium websockets

# Browser driver
sudo apt-get install chromium-chromedriver
```

### 2. Configure SSH Access
```bash
# Ensure SSH is running
sudo systemctl status ssh

# Check firewall
sudo ufw status
sudo ufw allow 22/tcp
```

### 3. Test Claude Access
```bash
# Test Claude installation
which claude
claude --help

# Test workspace trust
claude "Test message"
```

### 4. Test Web Interfaces
```bash
# Test OpenClaw UI
curl -s http://172.31.14.61:18789/ | grep -i "openclaw"

# Test memory visualization
curl -s http://172.31.14.61:5000/ 2>/dev/null || echo "Not running"
```

## Security Considerations

1. **SSH Security:**
   - Use key-based authentication
   - Consider changing default port
   - Implement fail2ban

2. **Terminal Sharing:**
   - Termius links contain session credentials
   - Share links securely
   - Revoke access when done

3. **Web Interfaces:**
   - OpenClaw UI has authentication
   - Memory visualization may be public
   - Consider firewall rules

## Troubleshooting

### Issue: Can't access SSH
```bash
# Check SSH service
sudo systemctl status ssh

# Check firewall
sudo ufw status

# Check network
netstat -tln | grep :22
```

### Issue: Claude not responding
```bash
# Check installation
which claude

# Test with print flag
claude --print "Test"

# Check workspace trust
# May need to run interactively first
```

### Issue: Web interfaces not accessible
```bash
# Check services
openclaw gateway status

# Check memory visualization
ps aux | grep "python3.*app.py"

# Check ports
netstat -tln | grep -E ":(18789|5000)"
```

## Future Enhancements

1. **WebSocket Terminal Server**
   - Real-time terminal sharing
   - Multiple concurrent sessions
   - Access control

2. **API Gateway**
   - REST API for terminal access
   - Claude Code API endpoint
   - Session management

3. **Integration with OpenClaw**
   - Native terminal tool
   - Session spawning with PTY
   - Better Claude integration

## References

- Termius Documentation: https://termius.com/help
- OpenClaw Gateway: `openclaw gateway --help`
- Claude Code: `claude --help`
- SSH Configuration: `/etc/ssh/sshd_config`

## Quick Start

1. **For SSH access:**
   ```bash
   ssh ubuntu@172.31.14.61
   ```

2. **For Claude conversation:**
   ```bash
   ssh ubuntu@172.31.14.61 -t "claude"
   ```

3. **For Termius sharing:**
   - Use Termius app with provided link
   - Join multiplayer session
   - Terminal access shared

4. **For web interface:**
   - Open browser to `http://172.31.14.61:18789/`
   - Use OpenClaw Control UI
   - May require gateway token