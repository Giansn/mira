---
name: dashboard-website-connection
description: "Connect OpenClaw dashboard to external website - NGINX reverse proxy, SSL, firewall configuration, troubleshooting"
trigger: "dashboard, website, connect, nginx, ssl, firewall, entrosana"
---

# Dashboard Website Connection Skill

## Overview

Connect your OpenClaw dashboard to an external website via HTTPS with proper security, SSL certificates, and firewall configuration. This skill handles the complete setup from local gateway to public website access.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Public Internet                      │
│                     (https://yourdomain.com)            │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS (443)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    NGINX Reverse Proxy                   │
│                  (SSL Termination + Routing)             │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP (18789)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 OpenClaw Gateway                        │
│                  (Port 18789 - Local)                   │
└─────────────────────────────────────────────────────────┘
```

## 3-Layer Firewall Architecture

### 1. AWS Security Group (EC2 Level)
- **Port 443**: Allow `0.0.0.0/0` (HTTPS from anywhere)
- **Port 18789**: Allow specific IPs or `0.0.0.0/0`

### 2. AWS Network ACL (Subnet Level - STATEFUL)
- **INBOUND**: Must allow destination port (18789 after proxy)
- **OUTBOUND**: Must allow ephemeral ports (1024-65535) for responses
- **Critical**: NACLs are stateless - need separate inbound AND outbound rules

### 3. Instance Firewall (UFW)
- **Port 443**: `sudo ufw allow 443/tcp`
- **Port 18789**: `sudo ufw allow 18789/tcp`
- **Default**: `deny (incoming)` - must explicitly allow ports

## Installation

### 1. Install NGINX and Certbot
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install NGINX
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Configure DNS
```bash
# Set up DNS records (example for entrosana.com)
# A record: entrosana.com → [YOUR_EC2_PUBLIC_IP]
# CNAME record: www.entrosana.com → entrosana.com
```

### 3. Obtain SSL Certificate
```bash
# Get Let's Encrypt certificate
sudo certbot --nginx -d entrosana.com -d www.entrosana.com

# Auto-renewal setup
sudo certbot renew --dry-run
```

## Configuration

### NGINX Configuration (`/etc/nginx/sites-available/entrosana.com`)
```nginx
server {
    listen 443 ssl;
    server_name entrosana.com www.entrosana.com;
    
    # SSL certificates (from Certbot)
    ssl_certificate /etc/letsencrypt/live/entrosana.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/entrosana.com/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    
    # Headers
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeouts
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_connect_timeout 10s;
    
    # Main location
    location / {
        proxy_pass http://127.0.0.1:18789;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name entrosana.com www.entrosana.com;
    return 301 https://$server_name$request_uri;
}
```

### OpenClaw Gateway Configuration
```bash
# Ensure gateway is running on port 18789
openclaw gateway status
openclaw gateway restart

# Configure gateway for external access
openclaw config set gateway.bind "0.0.0.0:18789"
openclaw config set gateway.controlUi.allowedOrigins "https://entrosana.com"
openclaw config set gateway.auth.token "YOUR_SECURE_TOKEN"
```

## Firewall Configuration

### AWS Security Group
```bash
# Check current security group
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# Add HTTPS rule (if not present)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

### AWS Network ACL (Critical - Most Common Issue)
```bash
# Check NACL rules
aws ec2 describe-network-acls --network-acl-ids acl-xxxxxxxx

# NACL must have:
# 1. INBOUND: Allow destination port (18789 after proxy)
# 2. OUTBOUND: Allow ephemeral ports (1024-65535)
```

### UFW Configuration
```bash
# Check status
sudo ufw status verbose

# Allow required ports
sudo ufw allow 22/tcp        # SSH
sudo ufw allow 443/tcp       # HTTPS
sudo ufw allow 18789/tcp     # OpenClaw gateway

# Enable UFW
sudo ufw --force enable
```

## Diagnostic Commands

### Connectivity Testing
```bash
# Test local gateway
curl http://localhost:18789/

# Test NGINX locally
curl -k -H "Host: entrosana.com" https://localhost/

# Test public access (from server)
curl -I https://entrosana.com/

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Host: entrosana.com" -H "Origin: https://entrosana.com" \
     https://entrosana.com/
```

### Service Status
```bash
# Check NGINX
sudo systemctl status nginx
sudo nginx -t

# Check OpenClaw gateway
openclaw gateway status
ps aux | grep gateway

# Check listening ports
sudo netstat -tlnp | grep ":443\|:18789"
sudo ss -tlnp | grep ":443\|:18789"
```

### Log Monitoring
```bash
# NGINX logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# OpenClaw logs
tail -f ~/.openclaw/logs/*.log

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u openclaw-gateway -f
```

## Common Issues & Solutions

### 1. "disconnected (1006): no reason" (WebSocket Error)
**Cause**: Firewall blocking WebSocket connection
**Solution**:
```bash
# Check all 3 firewall layers
./diagnose_firewall.sh

# Most likely: NACL outbound or UFW port 443
sudo ufw allow 443/tcp
```

### 2. "net::ERR_CONNECTION_TIMED_OUT"
**Cause**: Firewall blocking at some layer
**Solution**:
```bash
# Diagnostic script
curl -I https://entrosana.com/
sudo ufw status verbose
aws ec2 describe-network-acls --network-acl-ids acl-xxxxxxxx
```

### 3. NGINX 502 Bad Gateway
**Cause**: OpenClaw gateway not running
**Solution**:
```bash
openclaw gateway restart
sudo systemctl restart nginx
```

### 4. SSL Certificate Issues
**Cause**: Certificate expired or misconfigured
**Solution**:
```bash
# Renew certificate
sudo certbot renew

# Check certificate
sudo openssl x509 -in /etc/letsencrypt/live/entrosana.com/fullchain.pem -text -noout
```

## Self-Repair Protocol

### Dashboard Goes Down - Quick Fix Checklist
```bash
#!/bin/bash
# dashboard_emergency_repair.sh

echo "🔧 Dashboard Emergency Repair"
echo "============================="

# 1. Check OpenClaw gateway
echo "1. Checking OpenClaw gateway..."
openclaw gateway status || openclaw gateway restart

# 2. Check NGINX
echo "2. Checking NGINX..."
sudo systemctl status nginx || sudo systemctl restart nginx

# 3. Check UFW
echo "3. Checking firewall..."
sudo ufw status | grep "443/tcp" || sudo ufw allow 443/tcp

# 4. Test connectivity
echo "4. Testing connectivity..."
curl -I https://entrosana.com/ || echo "Connection failed"

# 5. Check logs
echo "5. Checking logs..."
sudo tail -20 /var/log/nginx/error.log

echo "✅ Emergency repair complete"
```

## Security Best Practices

### 1. Token Security
```bash
# Generate secure token
openssl rand -hex 24

# Set in OpenClaw
openclaw config set gateway.auth.token "generated_token_here"

# Set in website dashboard
# entrosana.com/#token=generated_token_here
```

### 2. Rate Limiting
```nginx
# In NGINX configuration
limit_req_zone $binary_remote_addr zone=openclaw:10m rate=10r/s;

location / {
    limit_req zone=openclaw burst=20 nodelay;
    proxy_pass http://127.0.0.1:18789;
}
```

### 3. IP Whitelisting (Optional)
```nginx
# Allow only specific IPs
allow 192.168.1.0/24;
allow 10.0.0.0/8;
deny all;
```

## Monitoring & Alerts

### Health Check Endpoint
```bash
# Create health check script
cat > /usr/local/bin/dashboard_health.sh << 'EOF'
#!/bin/bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://entrosana.com/health)
if [ "$STATUS" = "200" ]; then
    echo "OK"
else
    echo "FAILED: $STATUS"
    # Send alert
    curl -X POST -H "Content-Type: application/json" \
         -d '{"text":"Dashboard down: $STATUS"}' \
         https://hooks.slack.com/services/...
fi
EOF

chmod +x /usr/local/bin/dashboard_health.sh

# Add to cron
echo "*/5 * * * * /usr/local/bin/dashboard_health.sh" | sudo crontab -
```

### Log Rotation
```bash
# NGINX log rotation
sudo nano /etc/logrotate.d/nginx

# OpenClaw log rotation
cat > ~/.openclaw/logrotate.conf << 'EOF'
/home/ubuntu/.openclaw/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
}
EOF
```

## Integration with OpenClaw

### Memory Storage
```bash
# Store dashboard configuration in memory
echo "## Dashboard Configuration
- URL: https://entrosana.com/
- Token: (stored securely)
- Last connection: $(date)
- Status: Operational" >> ~/.openclaw/workspace/memory/dashboard.md
```

### Heartbeat Monitoring
```bash
# Add to HEARTBEAT.md
echo "### Dashboard Health Check
- Check https://entrosana.com/health
- Verify SSL certificate validity
- Monitor connection count
- Check for rate limiting issues" >> ~/.openclaw/workspace/HEARTBEAT.md
```

## Examples

### Example 1: Full Setup Script
```bash
#!/bin/bash
# setup_dashboard.sh

DOMAIN="entrosana.com"
GATEWAY_PORT="18789"
GATEWAY_TOKEN=$(openssl rand -hex 24)

echo "Setting up dashboard for $DOMAIN"

# 1. Install dependencies
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Configure NGINX
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:$GATEWAY_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

# 3. Get SSL certificate
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos

# 4. Configure OpenClaw
openclaw config set gateway.bind "0.0.0.0:$GATEWAY_PORT"
openclaw config set gateway.auth.token "$GATEWAY_TOKEN"
openclaw config set gateway.controlUi.allowedOrigins "https://$DOMAIN"

# 5. Configure firewall
sudo ufw allow 443/tcp
sudo ufw allow $GATEWAY_PORT/tcp

# 6. Restart services
openclaw gateway restart
sudo systemctl restart nginx

echo "✅ Dashboard setup complete"
echo "URL: https://$DOMAIN/#token=$GATEWAY_TOKEN"
```

### Example 2: Diagnostic Script
```bash
#!/bin/bash
# diagnose_dashboard.sh

echo "🔍 Dashboard Diagnostic Tool"
echo "============================"

check_service() {
    echo -n "Checking $1... "
    if systemctl is-active --quiet $1; then
        echo "✅ RUNNING"
    else
        echo "❌ STOPPED"
        return 1
    fi
}

check_port() {
    echo -n "Checking port $1... "
    if sudo netstat -tln | grep -q ":$1 "; then
        echo "✅ LISTENING"
    else
        echo "❌ NOT LISTENING"
        return 1
    fi
}

check_connectivity() {
    echo -n "Checking $1... "
    if curl -s -o /dev/null -w "%{http_code}" $1 | grep -q "200\|301\|302"; then
        echo "✅ ACCESSIBLE"
    else
        echo "❌ INACCESSIBLE"
        return 1
    fi
}

# Run checks
check_service nginx
check_service "openclaw-gateway"
check_port 443
check_port 18789
check_connectivity "http://localhost:18789"
check_connectivity "https://entrosana.com"

echo "============================"
echo "Diagnostic complete"
```

## Troubleshooting Guide

### Quick Reference Table

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| 502 Bad Gateway | Gateway not running | `openclaw gateway restart` |
| 504 Timeout | Firewall blocking | Check all 3 firewall layers |
| SSL errors | Certificate issues | `sudo certbot renew` |
| WebSocket disconnect | Headers missing | Verify NGINX WebSocket config |
| Can't connect externally | NACL blocking | Check AWS Network ACL outbound rules |

### Step-by-Step Debugging
1. **Start local**: `curl http://localhost:18789/`
2. **Check NGINX**: `curl -k https://localhost/ -H "Host: entrosana.com"`
3. **Check public**: `curl -I https://entrosana.com/`
4. **Check firewall**: `sudo ufw status verbose`
5. **Check NACL**: AWS Console → VPC → Network ACLs
6. **Check logs**: `sudo tail -f /var/log/nginx/error.log`

## Maintenance Schedule

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

## Support

### Common Configurations
- **Single domain**: entrosana.com → OpenClaw dashboard
- **Subdomain**: dashboard.entrosana.com → OpenClaw
- **Path-based**: entrosana.com/dashboard → OpenClaw
- **Multiple instances**: Load balancing across multiple OpenClaw gateways

### Getting Help
1.