# Dashboard Website Connection Skill

Connect your OpenClaw dashboard to an external website with HTTPS, SSL certificates, and proper security configuration.

## Quick Start

### 1. Setup Dashboard
```bash
# Run the setup script (requires sudo)
./setup_dashboard.sh entrosana.com your@email.com
```

### 2. Test Connection
```bash
# Run diagnostic tests
./diagnose_dashboard.sh

# Or run Python test
python3 test_connection.py
```

### 3. Emergency Repair
```bash
# If dashboard goes down
./emergency_repair.sh
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Comprehensive documentation |
| `setup_dashboard.sh` | Complete setup script |
| `diagnose_dashboard.sh` | Diagnostic tool |
| `emergency_repair.sh` | Emergency recovery |
| `test_connection.py` | Python test suite |

## Architecture

```
Public Internet (HTTPS) → NGINX (SSL Termination) → OpenClaw Gateway (18789)
```

### 3-Layer Firewall
1. **AWS Security Group** - EC2 level
2. **AWS Network ACL** - Subnet level (STATEFUL - most common issue)
3. **UFW** - Instance firewall

## Common Issues

### 1. "disconnected (1006): no reason"
- WebSocket connection failing
- Check NGINX WebSocket headers
- Check all 3 firewall layers

### 2. "net::ERR_CONNECTION_TIMED_OUT"
- Firewall blocking at some layer
- Check NACL outbound rules (most common)

### 3. 502 Bad Gateway
- OpenClaw gateway not running
- Run: `openclaw gateway restart`

## Quick Commands

```bash
# Check status
openclaw gateway status
sudo systemctl status nginx

# Restart services
openclaw gateway restart
sudo systemctl restart nginx

# Check firewall
sudo ufw status verbose

# Test connectivity
curl -I https://entrosana.com/
```

## Security

- SSL certificates via Let's Encrypt
- Rate limiting in NGINX
- Security headers
- Token-based authentication
- Regular certificate renewal

## Integration with OpenClaw

This skill integrates with:
- OpenClaw memory system (stores configuration)
- Heartbeat monitoring (regular health checks)
- Session management (dashboard sessions)
- ACP coordination (for complex setups)

## For entrosana.com

Current configuration:
- Domain: `entrosana.com`
- Gateway port: `18789`
- Token: `1f3c0559f9362ff5ff458c69eed348f6df5a7ec55bbc1287`
- URL: `https://entrosana.com/#token=TOKEN`

## Maintenance

### Daily
- Check dashboard accessibility
- Monitor error logs

### Weekly  
- Review connection statistics
- Check for security updates

### Monthly
- SSL certificate renewal (auto)
- Firewall rule review

## Support

See `SKILL.md` for detailed troubleshooting and configuration examples.