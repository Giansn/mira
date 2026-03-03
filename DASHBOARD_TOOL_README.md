# OpenClaw Dashboard Connection Tool

A generalized toolset for connecting OpenClaw dashboards to external websites via HTTPS. Removes specific domain references for general use.

## Tools Overview

### 1. `setup_dashboard.sh` - Complete Setup
```bash
# Basic usage
./setup_dashboard.sh yourdomain.com

# Custom port
./setup_dashboard.sh yourdomain.com 19999

# Default (uses yourdomain.com:18789)
./setup_dashboard.sh
```

**Features:**
- Installs NGINX and Certbot
- Configures SSL with Let's Encrypt
- Sets up OpenClaw gateway with secure token
- Configures firewall rules
- Generates dashboard URL with token

### 2. `diagnose_dashboard.sh` - Diagnostic Tool
```bash
# Check dashboard health
./diagnose_dashboard.sh yourdomain.com

# With custom port
./diagnose_dashboard.sh yourdomain.com 19999
```

**Checks performed:**
- Service status (NGINX, OpenClaw gateway)
- Port listening (443, gateway port)
- Connectivity (local and public)
- SSL certificate validity
- Firewall rules
- Configuration consistency

### 3. `emergency_repair.sh` - Emergency Recovery
```bash
# Emergency repair
./emergency_repair.sh yourdomain.com

# With custom port
./emergency_repair.sh yourdomain.com 19999
```

**Automatic repairs:**
- Restarts stopped services
- Adds missing firewall rules
- Renews expiring SSL certificates
- Tests connectivity
- Checks error logs

### 4. `generate_config.py` - Configuration Generator
```bash
# Generate config files
python3 generate_config.py yourdomain.com

# With custom port and output directory
python3 generate_config.py yourdomain.com --port 19999 --output-dir ./configs
```

**Generates:**
- NGINX configuration
- OpenClaw setup commands
- Firewall configuration
- DNS instructions
- Setup summary

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# 1. Make scripts executable
chmod +x *.sh

# 2. Run setup
./setup_dashboard.sh yourdomain.com

# 3. Update DNS (use IP shown in output)
#    A record: yourdomain.com → [PUBLIC_IP]

# 4. Test
./diagnose_dashboard.sh yourdomain.com
```

### Option 2: Manual Configuration
```bash
# 1. Generate configurations
python3 generate_config.py yourdomain.com

# 2. Review generated files
ls -la *.conf *.sh *.txt *.md

# 3. Follow setup summary
cat setup-summary-yourdomain.com.md
```

## Architecture

```
Public Internet → HTTPS (443) → NGINX → HTTP (18789) → OpenClaw Gateway
```

### Firewall Layers (All Must Allow):
1. **Cloud Security Group** (AWS/GCP/Azure)
   - Port 443: Allow 0.0.0.0/0
   - Gateway port: Allow specific IPs or 0.0.0.0/0

2. **Network ACL** (Cloud subnet level - STATEFUL)
   - INBOUND: Allow destination port (gateway port after proxy)
   - OUTBOUND: Allow ephemeral ports (1024-65535)

3. **Instance Firewall** (UFW/iptables)
   - Port 443: `sudo ufw allow 443/tcp`
   - Gateway port: `sudo ufw allow [PORT]/tcp`

## Common Issues & Solutions

### 1. "disconnected (1006): no reason" (WebSocket)
```bash
# Check all firewall layers
./diagnose_dashboard.sh yourdomain.com

# Most likely: NACL outbound or UFW port 443
sudo ufw allow 443/tcp
```

### 2. "net::ERR_CONNECTION_TIMED_OUT"
```bash
# Check each layer
curl -I https://yourdomain.com/
sudo ufw status verbose
# Check cloud console for Security Group and Network ACL
```

### 3. NGINX 502 Bad Gateway
```bash
# Gateway not running
openclaw gateway restart
sudo systemctl restart nginx
```

### 4. SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew

# Check certificate
sudo openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout
```

## Security Best Practices

### Token Security
```bash
# Generate secure token (automatically done by setup_dashboard.sh)
openssl rand -hex 24

# Dashboard URL format
https://yourdomain.com/#token=GENERATED_TOKEN
```

### Rate Limiting (Optional)
Add to NGINX configuration:
```nginx
limit_req_zone $binary_remote_addr zone=openclaw:10m rate=10r/s;

location / {
    limit_req zone=openclaw burst=20 nodelay;
    proxy_pass http://127.0.0.1:18789;
}
```

### IP Whitelisting (Optional)
```nginx
# Allow only specific IPs
allow 192.168.1.0/24;
allow 10.0.0.0/8;
deny all;
```

## Monitoring

### Health Check Endpoint
Dashboard includes `/health` endpoint:
```bash
curl https://yourdomain.com/health
# Returns: healthy
```

### Cron Monitoring
```bash
# Add to crontab
*/5 * * * * /path/to/diagnose_dashboard.sh yourdomain.com >> /var/log/dashboard-monitor.log
```

### Log Monitoring
```bash
# NGINX logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# OpenClaw logs
tail -f ~/.openclaw/logs/*.log
```

## Maintenance

### Daily
- Check dashboard accessibility
- Monitor error logs
- Verify SSL certificate validity

### Weekly
- Review connection statistics
- Check for security updates
- Backup configuration

### Monthly
- Renew SSL certificate (auto)
- Review firewall rules
- Update OpenClaw and NGINX

## Integration with OpenClaw

### Memory Storage
```bash
# Store dashboard configuration
echo "## Dashboard: yourdomain.com
- URL: https://yourdomain.com/#token=...
- Setup: $(date)
- Status: Operational" >> ~/.openclaw/workspace/memory/dashboards.md
```

### Heartbeat Monitoring
Add to `HEARTBEAT.md`:
```markdown
### Dashboard Health Check
- Check https://yourdomain.com/health
- Verify SSL certificate validity
- Monitor connection count
```

## Support

### Getting Help
1. Run diagnostic: `./diagnose_dashboard.sh yourdomain.com`
2. Check logs: `sudo tail -50 /var/log/nginx/error.log`
3. Verify DNS: `dig yourdomain.com +short`
4. Test locally: `curl http://localhost:18789/`

### Common Configurations
- **Single domain**: yourdomain.com → OpenClaw dashboard
- **Subdomain**: dashboard.yourdomain.com → OpenClaw
- **Path-based**: yourdomain.com/control → OpenClaw
- **Multiple instances**: Load balancing across multiple gateways

## License
Open source - use freely for any OpenClaw deployment.

## Version
v1.0.0 - Generalized from entrosana.com implementation
Generated: $(date)