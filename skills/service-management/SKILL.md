---
name: service-management
description: "Manage cron jobs, services, and background processes in OpenClaw. Use when: (1) Cron jobs are failing, (2) Services need configuration, (3) Background processes require management, (4) Scripts need fixing or optimization, (5) Scheduled tasks need monitoring."
---

# Service Management

## Overview

This skill provides tools and best practices for managing scheduled tasks, services, and background processes in OpenClaw. It addresses common issues like cron job failures, service configuration problems, and process management.

## Core Concepts

### 1. Cron Jobs
Scheduled tasks that run at specific times. Common issues:
- PATH environment issues
- Permission problems
- Script errors
- Output handling

### 2. Systemd Services
Managed services that can start on boot and restart on failure.

### 3. Background Processes
Long-running processes managed via process managers or screen/tmux.

### 4. Scheduled Tasks
One-time or recurring tasks scheduled via `at`, cron, or custom schedulers.

## Cron Job Management

### Creating Reliable Cron Jobs

**Basic Structure:**
```bash
# Minute Hour Day Month DayOfWeek Command
* * * * * /full/path/to/command
```

**Best Practices:**

1. **Use full paths:** Cron has minimal PATH
2. **Redirect output:** Capture stdout and stderr
3. **Set environment:** Export needed variables
4. **Add logging:** Log to files for debugging
5. **Test manually:** Run command outside cron first

**Example Reliable Cron Entry:**
```bash
# Run every hour, log output
0 * * * * /home/ubuntu/.npm-global/bin/openclaw sessions_spawn --runtime subagent --task "Heartbeat check" >> /home/ubuntu/.openclaw/logs/heartbeat.log 2>&1
```

### Common Cron Issues and Fixes

**Issue: "Command not found"**
```bash
# ❌ Bad
* * * * * openclaw status

# ✅ Good  
* * * * * /home/ubuntu/.npm-global/bin/openclaw status

# ✅ Better (set PATH)
* * * * * PATH=/home/ubuntu/.npm-global/bin:$PATH openclaw status
```

**Issue: No output/errors**
```bash
# ❌ Bad
* * * * * script.sh

# ✅ Good
* * * * * script.sh >> /tmp/script.log 2>&1

# ✅ Better (separate streams)
* * * * * script.sh >> /tmp/script.out 2>&1
```

**Issue: Permission denied**
```bash
# Check permissions
ls -la script.sh
chmod +x script.sh

# Run as correct user
sudo -u ubuntu script.sh
```

### Cron Management Scripts

- `scripts/cron_test.py`: Test cron entries before adding
- `scripts/cron_monitor.py`: Monitor cron job execution
- `scripts/cron_backup.py`: Backup and restore crontab

## Service Configuration

### OpenClaw Gateway Service

**As systemd service (`/etc/systemd/system/openclaw-gateway.service`):**
```ini
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/.openclaw
ExecStart=/home/ubuntu/.npm-global/bin/openclaw gateway start --foreground
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Management:**
```bash
# Enable and start
sudo systemctl enable openclaw-gateway
sudo systemctl start openclaw-gateway

# Check status
sudo systemctl status openclaw-gateway

# View logs
sudo journalctl -u openclaw-gateway -f
```

### Browser Control Service

**Managing browser with remote debugging:**
```bash
# Start browser with CDP
brave-browser --remote-debugging-port=9223 --user-data-dir=/tmp/brave-profile &

# Monitor browser process
pgrep -f "remote-debugging-port"

# Kill if needed
pkill -f "remote-debugging-port"
```

## Process Management

### Using `process` Tool
OpenClaw's `process` tool manages background exec sessions:

```javascript
// Start background process
exec({
  command: "long-running-script.sh",
  background: true
})

// List processes
process({ action: "list" })

// Check process status
process({ 
  action: "poll", 
  sessionId: "session-id" 
})
```

### Process Monitoring Scripts

- `scripts/process_monitor.py`: Monitor background processes
- `scripts/process_cleanup.py`: Clean up zombie processes
- `scripts/resource_monitor.py`: Monitor CPU/memory usage

## Real-World Examples

### Example 1: Fixing Moltbook Cron (Today's Issue)

**Problem:** Script fails with "openclaw: command not found"

**Original broken script:**
```bash
#!/bin/bash
# /home/ubuntu/.openclaw/workspace/moltbook-agent.sh
openclaw sessions_spawn --runtime subagent --task "Moltbook check"
```

**Fixed script:**
```bash
#!/bin/bash
# /home/ubuntu/.openclaw/workspace/moltbook-agent.sh

# Set environment
export PATH=/home/ubuntu/.npm-global/bin:$PATH
export MOLTBOOK_API_KEY=$(jq -r '.moltbook.api_key' ~/.config/moltbook/credentials.json)

# Log start
echo "$(date): Starting Moltbook agent" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log

# Run agent
openclaw sessions_spawn \
  --runtime subagent \
  --task "Check Moltbook feed and notifications" \
  --label "moltbook-daily" \
  --runTimeoutSeconds 300

# Log completion
echo "$(date): Moltbook agent completed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
```

**Updated cron entry:**
```bash
# Run daily at 9 AM UTC
0 9 * * * /home/ubuntu/.openclaw/workspace/moltbook-agent.sh >> /home/ubuntu/.openclaw/logs/moltbook-agent.log 2>&1
```

### Example 2: Managing Gateway Service

**Problem:** Gateway stops unexpectedly

**Solution:** Create systemd service with auto-restart:

1. Create service file
2. Enable auto-start on boot
3. Configure restart on failure
4. Add monitoring

### Example 3: Browser Automation Service

**Problem:** Browser needs to be always available for automation

**Solution:** Managed browser service:

```bash
#!/bin/bash
# /home/ubuntu/.openclaw/workspace/browser-service.sh

while true; do
  # Check if browser is running
  if ! pgrep -f "remote-debugging-port=9223" > /dev/null; then
    echo "$(date): Starting browser with CDP" >> /home/ubuntu/.openclaw/logs/browser-service.log
    brave-browser --remote-debugging-port=9223 --user-data-dir=/tmp/brave-profile --headless=new &
  fi
  sleep 60
done
```

## Monitoring and Alerting

### Health Checks
```bash
#!/bin/bash
# /home/ubuntu/.openclaw/workspace/health-check.sh

# Check gateway
if ! curl -s http://localhost:18789/status > /dev/null; then
  echo "Gateway down!" | mail -s "OpenClaw Alert" admin@example.com
  openclaw gateway restart
fi

# Check browser CDP
if ! curl -s http://localhost:9223/json/version > /dev/null; then
  echo "Browser CDP down!" >> /home/ubuntu/.openclaw/logs/alerts.log
fi

# Check disk space
if [ $(df /home --output=pcent | tail -1 | tr -d '%') -gt 90 ]; then
  echo "Disk space critical!" >> /home/ubuntu/.openclaw/logs/alerts.log
fi
```

### Log Monitoring
```bash
# Monitor for errors
tail -f /home/ubuntu/.openclaw/logs/*.log | grep -i "error\|failed\|exception"

# Set up logrotate
cat > /etc/logrotate.d/openclaw << EOF
/home/ubuntu/.openclaw/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF
```

## Best Practices

### 1. Idempotent Scripts
Scripts should be safe to run multiple times:
```bash
# ❌ Bad - creates duplicates
echo "entry" >> file.txt

# ✅ Good - checks first
grep -q "entry" file.txt || echo "entry" >> file.txt
```

### 2. Proper Error Handling
```bash
#!/bin/bash
set -e  # Exit on error
set -u  # Exit on undefined variable

# Trap errors
trap 'echo "Error at line $LINENO"; exit 1' ERR

# Or continue on error
command || echo "Command failed, continuing..."
```

### 3. Resource Management
```bash
# Clean up temp files
trap 'rm -f /tmp/tempfile.$$' EXIT

# Limit resource usage
ulimit -n 1024  # File descriptors
ulimit -u 100   # Processes
```

### 4. Security
```bash
# Don't run as root
if [ "$EUID" -eq 0 ]; then
  echo "Please run as non-root user"
  exit 1
fi

# Validate inputs
if [[ ! "$INPUT" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Invalid input"
  exit 1
fi
```

## Automation Scripts

### `scripts/service_setup.py`
Set up new services with proper configuration:
- Create systemd service files
- Configure cron jobs
- Set up logging
- Add monitoring

### `scripts/cron_deploy.py`
Deploy and manage cron jobs:
- Validate cron syntax
- Backup existing jobs
- Deploy new jobs
- Test execution

### `scripts/process_manager.py`
Manage background processes:
- Start/stop processes
- Monitor health
- Restart on failure
- Clean up resources

## References

- `references/cron_reference.md`: Complete cron syntax reference
- `references/systemd_guide.md`: Systemd service configuration
- `references/process_management.md`: Process management techniques
- `references/security_best_practices.md`: Security considerations for services

## Integration with System Diagnostics

Combine with system-diagnostics skill for comprehensive management:
1. **Monitor** with system-diagnostics
2. **Manage** with service-management
3. **Fix** issues as they arise
4. **Prevent** future problems

## Emergency Procedures

### Service Won't Start
1. Check logs: `journalctl -u service-name`
2. Test manually: Run command directly
3. Check dependencies: Ports, files, permissions
4. Simplify: Remove non-essential configuration

### Cron Job Flooding
1. Disable cron: `crontab -r` (backup first!)
2. Identify problem: Check script logic
3. Add rate limiting
4. Restore with fix

### Resource Exhaustion
1. Identify culprit: `ps aux --sort=-%mem`
2. Kill problem processes
3. Add resource limits
4. Implement monitoring
