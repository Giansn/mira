#!/bin/bash
# emergency_repair.sh - Dashboard emergency repair when down

set -e

DOMAIN="${1:-entrosana.com}"
GATEWAY_PORT="18789"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}🚨 DASHBOARD EMERGENCY REPAIR 🚨${NC}"
echo "Domain: $DOMAIN"
echo "Time: $(date)"
echo ""

# Function to run command with status
run_cmd() {
    local name="$1"
    local cmd="$2"
    
    echo -n "$name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

# Step 1: Quick status check
echo "📊 Current Status:"
run_cmd "OpenClaw Gateway" "openclaw gateway status"
run_cmd "NGINX Service" "systemctl is-active nginx"
run_cmd "Port 443" "netstat -tln | grep ':443 '"
run_cmd "Port $GATEWAY_PORT" "netstat -tln | grep ':$GATEWAY_PORT '"

echo ""
echo "🔧 Starting Emergency Repair..."
echo ""

# Step 2: Restart OpenClaw Gateway
echo "1. Restarting OpenClaw Gateway..."
if openclaw gateway restart; then
    echo -e "   ${GREEN}✅ Gateway restarted${NC}"
else
    echo -e "   ${RED}❌ Failed to restart gateway${NC}"
    echo "   Trying manual start..."
    nohup openclaw gateway start > /tmp/openclaw_start.log 2>&1 &
    sleep 2
fi

# Step 3: Restart NGINX
echo "2. Restarting NGINX..."
if sudo systemctl restart nginx; then
    echo -e "   ${GREEN}✅ NGINX restarted${NC}"
else
    echo -e "   ${RED}❌ Failed to restart NGINX${NC}"
    echo "   Checking configuration..."
    sudo nginx -t
    echo "   Trying reload..."
    sudo systemctl reload nginx
fi

# Step 4: Check Firewall
echo "3. Checking Firewall..."
if sudo ufw status | grep -q "443/tcp.*ALLOW"; then
    echo -e "   ${GREEN}✅ Port 443 allowed${NC}"
else
    echo -e "   ${YELLOW}⚠️  Port 443 not in UFW rules${NC}"
    sudo ufw allow 443/tcp
    echo -e "   ${GREEN}✅ Added port 443 rule${NC}"
fi

if sudo ufw status | grep -q "$GATEWAY_PORT/tcp.*ALLOW"; then
    echo -e "   ${GREEN}✅ Port $GATEWAY_PORT allowed${NC}"
else
    echo -e "   ${YELLOW}⚠️  Port $GATEWAY_PORT not in UFW rules${NC}"
    sudo ufw allow $GATEWAY_PORT/tcp
    echo -e "   ${GREEN}✅ Added port $GATEWAY_PORT rule${NC}"
fi

# Step 5: Check SSL Certificate
echo "4. Checking SSL Certificate..."
if sudo test -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem; then
    if sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -checkend 86400 > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ SSL certificate valid${NC}"
    else
        echo -e "   ${RED}❌ SSL certificate expired or expiring soon${NC}"
        echo "   Attempting renewal..."
        sudo certbot renew --force-renewal
    fi
else
    echo -e "   ${RED}❌ SSL certificate not found${NC}"
    echo "   You need to obtain a certificate:"
    echo "   sudo certbot --nginx -d $DOMAIN"
fi

# Step 6: Test Connectivity
echo "5. Testing Connectivity..."
echo -n "   Local gateway (:$GATEWAY_PORT)... "
if curl -s http://localhost:$GATEWAY_PORT/ > /dev/null; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

echo -n "   NGINX proxy (localhost)... "
if curl -s -k -H "Host: $DOMAIN" https://localhost/ > /dev/null; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

echo -n "   Public access ($DOMAIN)... "
if curl -s -I https://$DOMAIN/ 2>/dev/null | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  May be DNS or external issue${NC}"
fi

# Step 7: Check Logs for Errors
echo "6. Checking Error Logs..."
echo -n "   Recent NGINX errors... "
ERRORS=$(sudo tail -20 /var/log/nginx/error.log 2>/dev/null | grep -i "error\|failed" | head -5)
if [ -z "$ERRORS" ]; then
    echo -e "${GREEN}✅ None${NC}"
else
    echo -e "${RED}❌ Found errors:${NC}"
    echo "$ERRORS" | sed 's/^/      /'
fi

# Step 8: Verify Configuration
echo "7. Verifying Configuration..."
echo -n "   OpenClaw token... "
TOKEN=$(openclaw config get gateway.auth.token 2>/dev/null || echo "NOT_SET")
if [ "$TOKEN" != "NOT_SET" ]; then
    echo -e "${GREEN}✅ Set${NC}"
else
    echo -e "${RED}❌ Not set${NC}"
    echo "   Generate: openclaw config set gateway.auth.token \$(openssl rand -hex 24)"
fi

echo -n "   Allowed origins... "
ORIGINS=$(openclaw config get gateway.controlUi.allowedOrigins 2>/dev/null || echo "NOT_SET")
if echo "$ORIGINS" | grep -q "$DOMAIN"; then
    echo -e "${GREEN}✅ $DOMAIN allowed${NC}"
else
    echo -e "${RED}❌ $DOMAIN not in allowed origins${NC}"
    echo "   Fix: openclaw config set gateway.controlUi.allowedOrigins 'https://$DOMAIN'"
fi

# Step 9: AWS Specific Checks (if applicable)
echo "8. AWS Specific Checks..."
echo "   Note: If using AWS EC2, also check:"
echo "   • Security Group inbound rules (port 443)"
echo "   • Network ACL inbound AND outbound rules"
echo "   • Route table (0.0.0.0/0 → Internet Gateway)"

# Step 10: Create Recovery Report
echo ""
echo "📋 RECOVERY REPORT"
echo "=================="
echo "Repair completed at: $(date)"
echo ""

echo "🔗 Dashboard URL (if token is set):"
if [ "$TOKEN" != "NOT_SET" ]; then
    echo "   https://$DOMAIN/#token=$TOKEN"
else
    echo "   https://$DOMAIN/ (token not configured)"
fi

echo ""
echo "✅ Services Status:"
systemctl is-active nginx > /dev/null && echo "   • NGINX: Running" || echo "   • NGINX: Stopped"
openclaw gateway status > /dev/null && echo "   • OpenClaw Gateway: Running" || echo "   • OpenClaw Gateway: Stopped"

echo ""
echo "🔧 Maintenance Commands:"
echo "   • View NGINX logs: sudo tail -f /var/log/nginx/error.log"
echo "   • View gateway logs: tail -f ~/.openclaw/logs/*.log"
echo "   • Test connectivity: curl -I https://$DOMAIN/"
echo "   • Full diagnostic: ./diagnose_dashboard.sh"

echo ""
echo "🚨 If still having issues:"
echo "   1. Check all 3 firewall layers (UFW, Security Group, NACL)"
echo "   2. Verify DNS resolution: dig $DOMAIN"
echo "   3. Check AWS console for NACL outbound rules"
echo "   4. Review SKILL.md for detailed troubleshooting"

echo ""
echo -e "${GREEN}✅ Emergency repair sequence complete${NC}"
echo "Monitor logs for 5 minutes to ensure stability."

# Create timestamp file for last repair
echo "$(date): Emergency repair performed" >> /tmp/dashboard_repair_history.log

exit 0