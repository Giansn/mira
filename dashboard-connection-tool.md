# Dashboard Connection Tool - Generalized

## Overview
A comprehensive tool for connecting any OpenClaw dashboard to external websites via HTTPS with full security stack. Removes specific domain references for general use.

## Core Architecture
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

## Installation Script

### `setup_dashboard.sh`
```bash
#!/bin/bash
# setup_dashboard.sh - Generalized dashboard setup

set -e

# Configuration
DOMAIN="${1:-yourdomain.com}"
GATEWAY_PORT="${2:-18789}"
GATEWAY_TOKEN=$(openssl rand -hex 24)

echo "🔧 Setting up OpenClaw dashboard for $DOMAIN"
echo "============================================"

# 1. Install dependencies
echo "1. Installing dependencies..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Configure NGINX
echo "2. Configuring NGINX..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL certificates (will be added by Certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host \$host;
    
    # Headers
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    
    # Timeouts
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_connect_timeout 10s;
    
    # Main location
    location / {
        proxy_pass http://127.0.0.1:$GATEWAY_PORT;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
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
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t

# 3. Get SSL certificate
echo "3. Obtaining SSL certificate..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos

# 4. Configure OpenClaw
echo "4. Configuring OpenClaw gateway..."
openclaw config set gateway.bind "0.0.0.0:$GATEWAY_PORT"
openclaw config set gateway.auth.token "$GATEWAY_TOKEN"
openclaw config set gateway.controlUi.allowedOrigins "https://$DOMAIN"

# 5. Configure firewall
echo "5. Configuring firewall..."
sudo ufw allow 443/tcp
sudo ufw allow $GATEWAY_PORT/tcp

# 6. Restart services
echo "6. Restarting services..."
openclaw gateway restart
sudo systemctl restart nginx

echo "============================================"
echo "✅ Dashboard setup complete!"
echo ""
echo "Dashboard URL: https://$DOMAIN/#token=$GATEWAY_TOKEN"
echo ""
echo "Next steps:"
echo "1. Update DNS: A record for $DOMAIN → $(curl -s ifconfig.me)"
echo "2. Test connection: curl -I https://$DOMAIN/"
echo "3. Bookmark dashboard URL above"
echo ""
echo "Configuration saved to: /tmp/dashboard-config-$DOMAIN.txt"
echo "Token backup: $HOME/.openclaw/dashboard-token-$DOMAIN.txt"
echo "============================================"

# Save configuration
cat > /tmp/dashboard-config-$DOMAIN.txt << EOF
Domain: $DOMAIN
Gateway Port: $GATEWAY_PORT
Gateway Token: $GATEWAY_TOKEN
Dashboard URL: https://$DOMAIN/#token=$GATEWAY_TOKEN
Setup Date: $(date)
Public IP: $(curl -s ifconfig.me)
EOF

# Backup token securely
mkdir -p $HOME/.openclaw
echo "$GATEWAY_TOKEN" > $HOME/.openclaw/dashboard-token-$DOMAIN.txt
chmod 600 $HOME/.openclaw/dashboard-token-$DOMAIN.txt
```

## Diagnostic Tool

### `diagnose_dashboard.sh`
```bash
#!/bin/bash
# diagnose_dashboard.sh - Generalized dashboard diagnostic

set -e

DOMAIN="${1:-yourdomain.com}"
GATEWAY_PORT="${2:-18789}"

echo "🔍 OpenClaw Dashboard Diagnostic Tool"
echo "====================================="
echo "Domain: $DOMAIN"
echo "Gateway Port: $GATEWAY_PORT"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    echo -n "Checking $1 service... "
    if systemctl is-active --quiet $1; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ STOPPED${NC}"
        return 1
    fi
}

check_port() {
    echo -n "Checking port $1... "
    if sudo netstat -tln | grep -q ":$1 "; then
        echo -e "${GREEN}✅ LISTENING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT LISTENING${NC}"
        return 1
    fi
}

check_connectivity() {
    echo -n "Checking $1... "
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" $1 2>/dev/null || echo "000")
    
    case $STATUS in
        200|301|302)
            echo -e "${GREEN}✅ ACCESSIBLE ($STATUS)${NC}"
            return 0
            ;;
        000)
            echo -e "${RED}❌ CONNECTION FAILED${NC}"
            return 1
            ;;
        *)
            echo -e "${YELLOW}⚠️  UNEXPECTED ($STATUS)${NC}"
            return 2
            ;;
    esac
}

check_ssl() {
    echo -n "Checking SSL certificate... "
    if sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -checkend 86400 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ VALID (>1 day)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  EXPIRING SOON${NC}"
        return 1
    fi
}

check_firewall() {
    echo -n "Checking firewall (UFW)... "
    if sudo ufw status | grep -q "$1/tcp.*ALLOW"; then
        echo -e "${GREEN}✅ ALLOWED${NC}"
        return 0
    else
        echo -e "${RED}❌ BLOCKED${NC}"
        return 1
    fi
}

# Run checks
echo "📊 Service Status"
echo "----------------"
check_service nginx
check_service "openclaw-gateway"

echo ""
echo "🔌 Port Status"
echo "-------------"
check_port 443
check_port $GATEWAY_PORT

echo ""
echo "🌐 Connectivity"
echo "--------------"
check_connectivity "http://localhost:$GATEWAY_PORT"
check_connectivity "https://$DOMAIN"

echo ""
echo "🔒 Security"
echo "----------"
check_ssl
check_firewall 443
check_firewall $GATEWAY_PORT

echo ""
echo "📝 Configuration"
echo "---------------"
echo -n "Gateway token configured... "
if openclaw config get gateway.auth.token > /dev/null 2>&1; then
    echo -e "${GREEN}✅ YES${NC}"
else
    echo -e "${RED}❌ NO${NC}"
fi

echo -n "Domain allowed in origins... "
if openclaw config get gateway.controlUi.allowedOrigins | grep -q "$DOMAIN"; then
    echo -e "${GREEN}✅ YES${NC}"
else
    echo -e "${RED}❌ NO${NC}"
fi

echo ""
echo "====================================="
echo "Diagnostic complete"
echo ""
echo "Common issues:"
echo "1. Firewall: sudo ufw allow 443/tcp"
echo "2. SSL: sudo certbot renew"
echo "3. Gateway: openclaw gateway restart"
echo "4. NGINX: sudo systemctl restart nginx"
echo ""
echo "For AWS issues, check:"
echo "- Security Group: Port 443 allowed (0.0.0.0/0)"
echo "- Network ACL: Inbound/Outbound rules for port $GATEWAY_PORT"
echo "- DNS: A record points to $(curl -s ifconfig.me)"
echo "====================================="
```

## Emergency Repair Tool

### `emergency_repair.sh`
```bash
#!/bin/bash
# emergency_repair.sh - Dashboard emergency repair

set -e

DOMAIN="${1:-yourdomain.com}"
GATEWAY_PORT="${2:-18789}"

echo "🚨 OpenClaw Dashboard Emergency Repair"
echo "======================================"
echo "Domain: $DOMAIN"
echo "Time: $(date)"
echo ""

# 1. Check and restart OpenClaw gateway
echo "1. OpenClaw Gateway"
echo "-------------------"
if openclaw gateway status > /dev/null 2>&1; then
    echo "✅ Gateway is running"
else
    echo "⚠️  Restarting gateway..."
    openclaw gateway restart
    sleep 2
fi

# 2. Check and restart NGINX
echo ""
echo "2. NGINX Service"
echo "----------------"
if sudo systemctl is-active --quiet nginx; then
    echo "✅ NGINX is running"
else
    echo "⚠️  Restarting NGINX..."
    sudo systemctl restart nginx
    sleep 2
fi

# 3. Check firewall
echo ""
echo "3. Firewall Rules"
echo "-----------------"
echo -n "Port 443... "
if sudo ufw status | grep -q "443/tcp.*ALLOW"; then
    echo "✅ ALLOWED"
else
    echo "⚠️  Adding rule..."
    sudo ufw allow 443/tcp
fi

echo -n "Port $GATEWAY_PORT... "
if sudo ufw status | grep -q "$GATEWAY_PORT/tcp.*ALLOW"; then
    echo "✅ ALLOWED"
else
    echo "⚠️  Adding rule..."
    sudo ufw allow $GATEWAY_PORT/tcp
fi

# 4. Check SSL certificate
echo ""
echo "4. SSL Certificate"
echo "------------------"
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ Certificate exists"
    
    # Check expiration
    DAYS_LEFT=$(sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -checkend 864000 2>/dev/null && echo ">10" || echo "<10")
    
    if [ "$DAYS_LEFT" = "<10" ]; then
        echo "⚠️  Certificate expiring soon, renewing..."
        sudo certbot renew --force-renewal
    fi
else
    echo "❌ Certificate missing"
    echo "⚠️  Obtaining new certificate..."
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos
fi

# 5. Test connectivity
echo ""
echo "5. Connectivity Test"
echo "--------------------"
echo -n "Local gateway... "
if curl -s http://localhost:$GATEWAY_PORT > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo -n "Public dashboard... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/ 2>/dev/null || echo "FAILED")
if [[ "$STATUS" =~ ^[23][0-9][0-9]$ ]]; then
    echo "✅ OK ($STATUS)"
else
    echo "❌ FAILED ($STATUS)"
fi

# 6. Check logs for errors
echo ""
echo "6. Error Logs (last 5 lines)"
echo "----------------------------"
echo "NGINX error log:"
sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "No error log found"

echo ""
echo "OpenClaw logs:"
tail -5 ~/.openclaw/logs/*.log 2>/dev/null | head -5 || echo "No OpenClaw logs found"

echo ""
echo "======================================"
echo "✅ Emergency repair complete"
echo ""
echo "If issues persist, check:"
echo "1. DNS configuration for $DOMAIN"
echo "2. AWS Security Group and Network ACL"
echo "3. System resources (memory, disk)"
echo ""
echo "Run detailed diagnostic: ./diagnose_dashboard.sh $DOMAIN $GATEWAY_PORT"
echo "======================================"
```

## Configuration Generator

### `generate_config.py`
```python
#!/usr/bin/env python3
"""
Dashboard Configuration Generator
Generates NGINX and OpenClaw configurations for any domain
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def generate_nginx_config(domain, gateway_port=18789):
    """Generate NGINX configuration for domain"""
    
    config = f"""# OpenClaw Dashboard Configuration for {domain}
# Generated: {subprocess.check_output(['date']).decode().strip()}

server {{
    listen 443 ssl;
    server_name {domain} www.{domain};
    
    # SSL certificates (will be added by Certbot)
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    
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
    location / {{
        proxy_pass http://127.0.0.1:{gateway_port};
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }}
    
    # Health check endpoint
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}

# HTTP to HTTPS redirect
server {{
    listen 80;
    server_name {domain} www.{domain};
    return 301 https://$server_name$request_uri;
}}
"""
    
    return config

def generate_openclaw_commands(domain, gateway_port=18789):
    """Generate OpenClaw configuration commands"""
    
    # Generate secure token
    token = subprocess.check_output(['openssl', 'rand', '-hex', '24']).decode().strip()
    
    commands = f"""# OpenClaw Configuration Commands for {domain}
# Generated: {subprocess.check_output(['date']).decode().strip()}

# Set gateway bind address
openclaw config set gateway.bind "0.0.0.0:{gateway_port}"

# Set authentication token
openclaw