# Dashboard Access Through Custom Domain

## Overview
Toolset for exposing OpenClaw dashboards via custom domains with HTTPS, SSL, and proper firewall configuration.

## Tools
- **`setup_dashboard.sh`** - One-command deployment: NGINX + SSL + firewall + OpenClaw config
  - Location: `/home/ubuntu/.openclaw/workspace/setup_dashboard.sh`
- **`diagnose_dashboard.sh`** - Comprehensive diagnostics: 3-layer firewall, connectivity, SSL, services
  - Location: `/home/ubuntu/.openclaw/workspace/diagnose_dashboard.sh`
- **`emergency_repair.sh`** - Automatic recovery: restarts, rule fixes, certificate renewal
  - Location: `/home/ubuntu/.openclaw/workspace/emergency_repair.sh`
- **`generate_config.py`** - Configuration generator: templates for review/modification
  - Location: `/home/ubuntu/.openclaw/workspace/generate_config.py`

## Architecture
```
Public HTTPS (443) → NGINX Reverse Proxy → OpenClaw Gateway (18789)
```

## 3-Layer Firewall (All Must Allow)
1. **Cloud Security Group** - Port 443 (0.0.0.0/0)
2. **Network ACL** - STATEFUL: inbound/outbound rules for gateway port + ephemeral ports
3. **Instance Firewall (UFW)** - Explicit allow: 443/tcp, gateway-port/tcp

## Usage
```bash
# Setup
./setup_dashboard.sh yourdomain.com

# Diagnostics  
./diagnose_dashboard.sh yourdomain.com

# Emergency repair
./emergency_repair.sh yourdomain.com

# Generate configs
python3 generate_config.py yourdomain.com
```

## Key Features
- **Domain-agnostic** - Works with any custom domain
- **Automatic SSL** - Let's Encrypt with auto-renewal
- **WebSocket support** - Real-time dashboard updates
- **Secure tokens** - Random authentication tokens
- **Self-healing** - Automatic issue detection and repair
- **Comprehensive diagnostics** - Color-coded status checks

## Common Issues Fixed
- **"disconnected (1006)"** - WebSocket configuration
- **Connection timeouts** - Firewall layer misconfiguration
- **502 Bad Gateway** - Service failures
- **SSL errors** - Certificate issues

## Output
- Dashboard URL: `https://yourdomain.com/#token=SECURE_TOKEN`
- Configuration backup
- DNS instructions with public IP
- Setup summary with next steps

## Maintenance
- **Daily**: Accessibility check, error log monitoring
- **Weekly**: Security updates, configuration review
- **Monthly**: SSL renewal, firewall audit

## Integration
- OpenClaw gateway configuration
- Memory system tracking
- Heartbeat monitoring
- Log aggregation

## Requirements
- Domain name
- Server with public IP
- OpenClaw installation
- Ubuntu/Debian Linux

## Files Created (by generate_config.py)
- `nginx-yourdomain.conf` - NGINX configuration
- `openclaw-yourdomain.sh` - OpenClaw commands
- `firewall-yourdomain.sh` - Firewall rules
- `dns-yourdomain.txt` - DNS instructions
- `setup-summary-yourdomain.md` - Complete guide

## Related Documentation
- **Complete Tool Documentation**: `/home/ubuntu/.openclaw/workspace/DASHBOARD_TOOL_README.md`
- **Technical Reference**: `/home/ubuntu/.openclaw/workspace/dashboard-connection-tool.md`
- **Community Post**: `/home/ubuntu/.openclaw/workspace/DASHBOARD_TOOL_POST.md`
- **Shareable Version**: `/home/ubuntu/.openclaw/workspace/SHAREABLE_POST.md`

## Quick Start
```bash
# 1. Navigate to workspace
cd /home/ubuntu/.openclaw/workspace

# 2. Make tools executable
chmod +x setup_dashboard.sh diagnose_dashboard.sh emergency_repair.sh

# 3. Run setup
./setup_dashboard.sh yourdomain.com

# 4. Update DNS A record → [PUBLIC_IP_SHOWN_IN_OUTPUT]
# 5. Access: `https://yourdomain.com/#token=...`
```

## Notes
- Works with any cloud provider (AWS, GCP, Azure, DigitalOcean)
- Compatible with any Linux distribution
- Open source, modifiable for specific needs
- Includes emergency repair for common outages

## File System Location
All tools and documentation are located in: `/home/ubuntu/.openclaw/workspace/`

To list all dashboard-related files:
```bash
ls -la /home/ubuntu/.openclaw/workspace/*dashboard* /home/ubuntu/.openclaw/workspace/*DASHBOARD*
```