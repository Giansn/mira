---
name: system-diagnostics
description: "Diagnose and troubleshoot OpenClaw system issues. Use when: (1) Services are failing (gateway, browser, cron jobs), (2) API integrations not working, (3) Logs show errors, (4) System performance issues, (5) Configuration problems need investigation."
---

# System Diagnostics

## Overview

This skill provides systematic approaches to diagnosing OpenClaw system issues. It includes checklists, scripts, and troubleshooting guides for common problems encountered in production.

## Quick Diagnostic Checklist

### 1. Service Status Check
```bash
# Check OpenClaw gateway
openclaw gateway status

# Check running processes
ps aux | grep openclaw

# Check systemd services
systemctl status openclaw-gateway 2>/dev/null || echo "No systemd service"
```

### 2. Log Inspection
```bash
# Recent gateway logs
tail -50 /home/ubuntu/.openclaw/logs/gateway.log

# Error patterns
grep -i error /home/ubuntu/.openclaw/logs/*.log | tail -20

# Specific service logs
ls -la /home/ubuntu/.openclaw/logs/
```

### 3. Configuration Verification
```bash
# Check config file
cat /home/ubuntu/.openclaw/openclaw.json | jq . 2>/dev/null || cat /home/ubuntu/.openclaw/openclaw.json

# Validate config
openclaw config validate
```

## Common Issue Categories

### Category 1: Gateway Issues

**Symptoms:**
- "Cannot connect to gateway"
- Gateway process not running
- Authentication failures

**Diagnosis:**
```bash
# Check if gateway is running
netstat -tlnp | grep :18789

# Check gateway PID
cat /home/ubuntu/.openclaw/gateway.pid 2>/dev/null

# Test gateway connection
curl -s http://localhost:18789/status
```

**Solutions:**
- Restart gateway: `openclaw gateway restart`
- Check firewall rules
- Verify bind address in config

### Category 2: Browser Control Issues

**Symptoms:**
- "Profile not found"
- Browser not starting
- CDP connection failures

**Diagnosis:**
```bash
# Check browser profiles
openclaw browser status

# Check Chrome/Chromium installation
which google-chrome-stable || which chromium-browser

# Test CDP connection
curl -s http://localhost:9223/json/version 2>/dev/null || echo "CDP not available"
```

**Solutions:**
- Start browser with remote debugging
- Configure correct CDP URL in profiles
- Check browser installation

### Category 3: API Integration Issues

**Symptoms:**
- "401 Unauthorized" errors
- API calls failing
- Rate limit errors

**Diagnosis:**
```bash
# Check environment variables
env | grep -i api

# Check credential files
ls -la ~/.config/*/credentials.json 2>/dev/null

# Test API connectivity
curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | head -5
```

**Solutions:**
- Verify API keys
- Check rate limits
- Update expired credentials

### Category 4: Cron Job Issues

**Symptoms:**
- Scheduled tasks not running
- Script errors in cron logs
- Permission issues

**Diagnosis:**
```bash
# Check crontab
crontab -l

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Check script permissions
ls -la /home/ubuntu/.openclaw/workspace/*.sh
```

**Solutions:**
- Fix script paths (use full paths in cron)
- Set correct permissions
- Add error logging

## Diagnostic Scripts

### `scripts/health_check.py`
Comprehensive system health check:
- Service status
- Disk space
- Memory usage
- Log errors
- API connectivity

### `scripts/diagnose_service.py`
Diagnose specific service issues:
- Gateway diagnostics
- Browser diagnostics
- API diagnostics

### `scripts/log_analyzer.py`
Analyze logs for patterns:
- Error frequency
- Performance issues
- Security concerns

### `scripts/config_validator.py`
Validate configuration files:
- JSON syntax
- Required fields
- Value ranges

## Real-World Examples

### Example 1: Moltbook Cron Failure (Today's Issue)
**Symptoms:** 401 errors, "openclaw: command not found"

**Diagnosis:**
```bash
# Check cron entry
crontab -l | grep moltbook

# Check script
cat /home/ubuntu/.openclaw/workspace/moltbook-agent.sh

# Check API key
cat ~/.config/moltbook/credentials.json

# Check openclaw command path
which openclaw
```

**Root Causes:**
1. Script uses `openclaw` without full path
2. Environment doesn't have PATH set in cron
3. API key not being passed correctly

**Fix:**
```bash
# Update script to use full path
#!/bin/bash
/home/ubuntu/.npm-global/bin/openclaw sessions_spawn ...

# Or set PATH in script
export PATH=$PATH:/home/ubuntu/.npm-global/bin
```

### Example 2: Gateway Connection Issues
**Symptoms:** entrosana.com can't connect

**Diagnosis:**
```bash
# Check gateway is running
openclaw gateway status

# Check bind address
grep -A5 '"bind"' /home/ubuntu/.openclaw/openclaw.json

# Check firewall
sudo ufw status

# Test remote connection
curl -s http://$(hostname -I | awk '{print $1}'):18789/status
```

### Example 3: Browser Profile Issues
**Symptoms:** "Profile brave-remote not found"

**Diagnosis:**
```bash
# Check configured profiles
grep -A10 '"profiles"' /home/ubuntu/.openclaw/openclaw.json

# Check if browser is running with CDP
ps aux | grep remote-debugging

# Test CDP endpoint
curl -s http://localhost:9223/json/version
```

## Troubleshooting Methodology

### Step 1: Reproduce the Issue
- What exactly is failing?
- Error messages?
- When did it start?

### Step 2: Check Basics
- Services running?
- Logs show errors?
- Configuration valid?

### Step 3: Isolate the Problem
- Which component is failing?
- Is it network, config, or code?
- Can you reproduce manually?

### Step 4: Test Fixes
- Make one change at a time
- Test after each change
- Document what works

### Step 5: Prevent Recurrence
- Add monitoring
- Improve error handling
- Update documentation

## Prevention Strategies

### 1. Monitoring
- Regular health checks
- Alert on errors
- Performance metrics

### 2. Documentation
- Keep runbooks updated
- Document known issues
- Share solutions

### 3. Testing
- Test configuration changes
- Validate scripts before cron
- Simulate failures

### 4. Maintenance
- Regular updates
- Log rotation
- Backup configurations

## References

- `references/log_patterns.md`: Common error patterns and solutions
- `references/service_ports.md`: Ports used by OpenClaw services
- `references/api_troubleshooting.md`: API integration troubleshooting
- `references/performance_metrics.md`: Performance benchmarks and targets

## Integration with Heartbeat

Add diagnostic checks to HEARTBEAT.md:
```markdown
### System Diagnostics (every 6 heartbeats)
- Run health_check.py
- Check for critical errors in logs
- Verify API connectivity
- Report any issues found
```

## Emergency Procedures

### Critical Issue: Gateway Down
1. Check logs: `tail -100 /home/ubuntu/.openclaw/logs/gateway.log`
2. Restart: `openclaw gateway restart`
3. If fails: `openclaw gateway stop && openclaw gateway start`
4. Check: `openclaw gateway status`

### Critical Issue: API Keys Expired
1. Identify which API is failing
2. Check credential files
3. Test with new keys
4. Update configuration

### Critical Issue: Disk Full
1. Check: `df -h`
2. Clean logs: `find /home/ubuntu/.openclaw/logs -name "*.log" -mtime +7 -delete`
3. Clear temp files
4. Expand disk if needed
