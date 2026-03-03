#!/bin/bash
# setup_dashboard.sh - Complete dashboard setup script

set -e  # Exit on error

# Configuration
DOMAIN="${1:-entrosana.com}"
GATEWAY_PORT="18789"
GATEWAY_TOKEN=$(openssl rand -hex 24)
EMAIL="${2:-admin@$DOMAIN}"

echo "🚀 Setting up OpenClaw Dashboard for $DOMAIN"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Check prerequisites
info "Checking prerequisites..."
command -v nginx >/dev/null 2>&1 || { error "NGINX not installed. Run: sudo apt install nginx"; }
command -v certbot >/dev/null 2>&1 || { error "Certbot not installed. Run: sudo apt install certbot python3-certbot-nginx"; }
command -v openclaw >/dev/null 2>&1 || { error "OpenClaw not installed"; }

# 1. Configure OpenClaw Gateway
info "Configuring OpenClaw gateway..."
openclaw config set gateway.bind "0.0.0.0:$GATEWAY_PORT" || error "Failed to set gateway bind"
openclaw config set gateway.auth.token "$GATEWAY_TOKEN" || error "Failed to set gateway token"
openclaw config set gateway.controlUi.allowedOrigins "https://$DOMAIN" || error "Failed to set allowed origins"

success "OpenClaw configured"

# 2. Create NGINX configuration
info "Creating NGINX configuration..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
# OpenClaw Dashboard - $DOMAIN
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL certificates (will be added by Certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL optimization
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    
    # Timeouts
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_connect_timeout 10s;
    
    # Main dashboard
    location / {
        proxy_pass http://127.0.0.1:$GATEWAY_PORT;
        
        # Rate limiting
        limit_req zone=openclaw burst=20 nodelay;
    }
    
    # Health endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Static assets cache
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Rate limiting zone
limit_req_zone \$binary_remote_addr zone=openclaw:10m rate=10r/s;
EOF

success "NGINX configuration created"

# 3. Enable site
info "Enabling NGINX site..."
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t || error "NGINX configuration test failed"
success "NGINX site enabled"

# 4. Obtain SSL certificate
info "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL || {
    info "Certbot failed, trying alternative method..."
    sudo certbot certonly --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL
}

success "SSL certificate obtained"

# 5. Configure firewall
info "Configuring firewall..."
sudo ufw allow 22/tcp comment "SSH" || info "SSH rule already exists"
sudo ufw allow 443/tcp comment "HTTPS" || info "HTTPS rule already exists"
sudo ufw allow $GATEWAY_PORT/tcp comment "OpenClaw Gateway" || info "Gateway rule already exists"
sudo ufw --force enable || info "UFW already enabled"

success "Firewall configured"

# 6. Restart services
info "Restarting services..."
openclaw gateway restart || error "Failed to restart OpenClaw gateway"
sudo systemctl restart nginx || error "Failed to restart NGINX"

success "Services restarted"

# 7. Test configuration
info "Testing configuration..."
sleep 2  # Give services time to start

echo -n "Testing local gateway... "
if curl -s http://localhost:$GATEWAY_PORT/ > /dev/null; then
    success "OK"
else
    error "Failed - check 'openclaw gateway status'"
fi

echo -n "Testing NGINX proxy... "
if curl -s -k -H "Host: $DOMAIN" https://localhost/ > /dev/null; then
    success "OK"
else
    error "Failed - check 'sudo systemctl status nginx'"
fi

echo -n "Testing public access (this may take a moment)... "
if curl -s -I https://$DOMAIN/ 2>/dev/null | grep -q "200\|301\|302"; then
    success "OK"
else
    info "Public access test failed - this may be normal if DNS hasn't propagated"
fi

# 8. Create dashboard URL
DASHBOARD_URL="https://$DOMAIN/#token=$GATEWAY_TOKEN"

echo ""
echo "=============================================="
echo "🎉 OPENCLAW DASHBOARD SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "📊 Dashboard URL:"
echo "   $DASHBOARD_URL"
echo ""
echo "🔑 Access Token:"
echo "   $GATEWAY_TOKEN"
echo ""
echo "📋 Configuration Summary:"
echo "   • Domain: $DOMAIN"
echo "   • Gateway Port: $GATEWAY_PORT"
echo "   • SSL: Enabled (Let's Encrypt)"
echo "   • Firewall: Ports 22, 443, $GATEWAY_PORT open"
echo "   • Rate Limiting: 10 requests/second"
echo ""
echo "🚨 IMPORTANT SECURITY NOTES:"
echo "   1. Keep the token secure - it provides full access"
echo "   2. Monitor logs: sudo tail -f /var/log/nginx/access.log"
echo "   3. SSL auto-renews: sudo certbot renew"
echo "   4. Test regularly: curl -I https://$DOMAIN/health"
echo ""
echo "🔧 Maintenance Commands:"
echo "   • Check status: ./diagnose_dashboard.sh"
echo "   • View logs: sudo journalctl -u nginx -f"
echo "   • Restart: sudo systemctl restart nginx"
echo "   • Update: sudo apt update && sudo apt upgrade"
echo ""
echo "=============================================="

# Save configuration
mkdir -p ~/.openclaw/dashboard
cat > ~/.openclaw/dashboard/$DOMAIN.conf << EOF
# Dashboard Configuration - $DOMAIN
DOMAIN="$DOMAIN"
GATEWAY_PORT="$GATEWAY_PORT"
GATEWAY_TOKEN="$GATEWAY_TOKEN"
DASHBOARD_URL="$DASHBOARD_URL"
SETUP_DATE="$(date)"
EOF

success "Configuration saved to ~/.openclaw/dashboard/$DOMAIN.conf"

# Create diagnostic script
cat > ~/.openclaw/dashboard/diagnose_$DOMAIN.sh << 'EOF'
#!/bin/bash
# Diagnostic script for $DOMAIN dashboard

echo "🔍 Dashboard Diagnostic - $DOMAIN"
echo "================================="

check() {
    echo -n "$1... "
    if eval "$2"; then
        echo "✅"
        return 0
    else
        echo "❌"
        return 1
    fi
}

check "OpenClaw Gateway" "openclaw gateway status"
check "NGINX Service" "systemctl is-active --quiet nginx"
check "Port 443" "netstat -tln | grep -q ':443 '"
check "Port $GATEWAY_PORT" "netstat -tln | grep -q ':$GATEWAY_PORT '"
check "SSL Certificate" "sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -checkend 86400 > /dev/null"
check "Local Gateway" "curl -s http://localhost:$GATEWAY_PORT/ > /dev/null"
check "NGINX Proxy" "curl -s -k -H 'Host: $DOMAIN' https://localhost/ > /dev/null"

echo ""
echo "📊 Quick Tests:"
echo "1. Local gateway: curl http://localhost:$GATEWAY_PORT/"
echo "2. NGINX proxy: curl -k -H 'Host: $DOMAIN' https://localhost/"
echo "3. Public access: curl -I https://$DOMAIN/"
echo ""
echo "📋 Configuration:"
echo "• Token: $(openclaw config get gateway.auth.token 2>/dev/null || echo 'Not set')"
echo "• Allowed Origins: $(openclaw config get gateway.controlUi.allowedOrigins 2>/dev/null || echo 'Not set')"
EOF

chmod +x ~/.openclaw/dashboard/diagnose_$DOMAIN.sh
success "Diagnostic script created: ~/.openclaw/dashboard/diagnose_$DOMAIN.sh"

echo ""
info "Next steps:"
echo "   1. Update DNS if not already done"
echo "   2. Test the dashboard URL in browser"
echo "   3. Set up monitoring (see SKILL.md)"
echo "   4. Regular security updates"