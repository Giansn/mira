#!/bin/bash
# setup_dashboard.sh - Generalized OpenClaw dashboard setup

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