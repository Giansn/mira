#!/bin/bash
# diagnose_dashboard.sh - Comprehensive dashboard diagnostic tool

set -e

# Configuration
DOMAIN="${1:-entrosana.com}"
GATEWAY_PORT="18789"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

header() { echo -e "\n${BLUE}=== $1 ===${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

check() {
    local name="$1"
    local command="$2"
    local fix="$3"
    
    echo -n "$name... "
    if eval "$command" 2>/dev/null; then
        success "PASS"
        return 0
    else
        error "FAIL"
        if [ -n "$fix" ]; then
            info "   Fix: $fix"
        fi
        return 1
    fi
}

test_endpoint() {
    local url="$1"
    local name="$2"
    
    echo -n "$name ($url)... "
    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")
    
    case $status in
        200|301|302) success "HTTP $status" ;;
        000) error "TIMEOUT/ERROR" ;;
        *) warning "HTTP $status" ;;
    esac
}

echo "🔍 OpenClaw Dashboard Diagnostic Tool"
echo "====================================="
echo "Domain: $DOMAIN"
echo "Gateway Port: $GATEWAY_PORT"
echo "Date: $(date)"
echo ""

# Section 1: Service Status
header "1. Service Status"

check "OpenClaw Gateway" \
    "openclaw gateway status > /dev/null" \
    "Run: openclaw gateway restart"

check "NGINX Service" \
    "systemctl is-active --quiet nginx" \
    "Run: sudo systemctl restart nginx"

check "Certbot Timer" \
    "systemctl is-active --quiet certbot.timer" \
    "Run: sudo systemctl enable --now certbot.timer"

# Section 2: Network & Ports
header "2. Network & Ports"

check "Port 443 (HTTPS)" \
    "sudo netstat -tln | grep -q ':443 '" \
    "Check firewall: sudo ufw allow 443/tcp"

check "Port $GATEWAY_PORT (Gateway)" \
    "sudo netstat -tln | grep -q ':$GATEWAY_PORT '" \
    "Check OpenClaw config: openclaw config get gateway.bind"

check "UFW Status" \
    "sudo ufw status | grep -q 'Status: active'" \
    "Enable: sudo ufw --force enable"

check "UFW Port 443" \
    "sudo ufw status | grep -q '443/tcp'" \
    "Add: sudo ufw allow 443/tcp"

check "UFW Port $GATEWAY_PORT" \
    "sudo ufw status | grep -q '$GATEWAY_PORT/tcp'" \
    "Add: sudo ufw allow $GATEWAY_PORT/tcp"

# Section 3: SSL & Certificates
header "3. SSL Certificates"

check "SSL Certificate Exists" \
    "sudo test -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem" \
    "Run: sudo certbot --nginx -d $DOMAIN"

check "SSL Certificate Valid" \
    "sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -checkend 86400 > /dev/null" \
    "Renew: sudo certbot renew"

check "Private Key Exists" \
    "sudo test -f /etc/letsencrypt/live/$DOMAIN/privkey.pem" \
    "Reissue certificate: sudo certbot --nginx -d $DOMAIN"

# Section 4: Connectivity Tests
header "4. Connectivity Tests"

test_endpoint "http://localhost:$GATEWAY_PORT/" "Local Gateway"
test_endpoint "https://localhost/ -H 'Host: $DOMAIN' -k" "NGINX Local Proxy"
test_endpoint "https://$DOMAIN/" "Public Access"

# Section 5: Configuration Checks
header "5. Configuration"

check "NGINX Config Syntax" \
    "sudo nginx -t > /dev/null" \
    "Fix NGINX config: sudo nginx -t"

check "OpenClaw Token Set" \
    "openclaw config get gateway.auth.token > /dev/null 2>&1" \
    "Set token: openclaw config set gateway.auth.token 'your_token'"

check "OpenClaw Allowed Origins" \
    "openclaw config get gateway.controlUi.allowedOrigins | grep -q '$DOMAIN'" \
    "Add domain: openclaw config set gateway.controlUi.allowedOrigins 'https://$DOMAIN'"

# Section 6: Log Checks
header "6. Log Analysis"

echo -n "Recent NGINX errors... "
ERROR_COUNT=$(sudo tail -100 /var/log/nginx/error.log 2>/dev/null | grep -c "error\|failed")
if [ "$ERROR_COUNT" -eq 0 ]; then
    success "None"
else
    warning "$ERROR_COUNT errors found"
    info "   View: sudo tail -20 /var/log/nginx/error.log"
fi

echo -n "Recent gateway activity... "
if tail -20 ~/.openclaw/logs/*.log 2>/dev/null | grep -q "gateway\|connection"; then
    success "Active"
else
    warning "No recent activity"
fi

# Section 7: Performance & Resources
header "7. System Resources"

echo -n "Memory usage... "
MEM_FREE=$(free -m | awk '/^Mem:/ {print $4}')
if [ "$MEM_FREE" -gt 100 ]; then
    success "${MEM_FREE}MB free"
else
    warning "${MEM_FREE}MB free - low memory"
fi

echo -n "Disk space... "
DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')
success "$DISK_FREE free"

echo -n "Load average... "
LOAD=$(uptime | awk -F'load average:' '{print $2}')
success "$LOAD"

# Section 8: Security Checks
header "8. Security"

check "SSH only from known IPs" \
    "sudo ufw status | grep '22/tcp' | grep -q 'ALLOW'" \
    "Restrict SSH: sudo ufw allow from YOUR_IP to any port 22"

check "No open database ports" \
    "! sudo netstat -tln | grep -q ':3306\|:5432\|:27017'" \
    "Close unnecessary ports"

check "Fail2ban installed" \
    "dpkg -l | grep -q fail2ban" \
    "Install: sudo apt install fail2ban"

# Summary
header "DIAGNOSTIC SUMMARY"

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Count from previous output (simplified)
echo ""
info "Quick Fix Commands:"
echo "  • Restart everything: openclaw gateway restart && sudo systemctl restart nginx"
echo "  • Check firewall: sudo ufw status verbose"
echo "  • Test SSL: sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -text -noout"
echo "  • View logs: sudo tail -f /var/log/nginx/error.log"
echo "  • Test WebSocket: curl -i -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' https://$DOMAIN/"

echo ""
info "Common Issues & Solutions:"
echo "  1. 502 Bad Gateway → OpenClaw gateway not running"
echo "  2. Connection timeout → Firewall blocking (check all 3 layers)"
echo "  3. SSL errors → Certificate expired or misconfigured"
echo "  4. WebSocket disconnect → NGINX headers missing"
echo "  5. Can't connect externally → AWS NACL outbound rules"

echo ""
info "Emergency Repair:"
cat << 'EOF'
#!/bin/bash
# Emergency repair script
openclaw gateway restart
sudo systemctl restart nginx
sudo ufw allow 443/tcp
sudo certbot renew --force-renewal
curl -I https://$DOMAIN/
EOF

echo ""
echo "====================================="
echo "🔧 For detailed troubleshooting, see:"
echo "   ~/.openclaw/workspace/skills/dashboard-website-connection/SKILL.md"
echo ""
echo "📊 Dashboard URL (if configured):"
echo "   https://$DOMAIN/#token=$(openclaw config get gateway.auth.token 2>/dev/null || echo 'TOKEN_NOT_SET')"
echo "====================================="

# Create report file
REPORT_FILE="/tmp/dashboard_diagnostic_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "Dashboard Diagnostic Report"
    echo "==========================="
    echo "Domain: $DOMAIN"
    echo "Date: $(date)"
    echo ""
    echo "Full output saved for reference"
} > "$REPORT_FILE"

info "Full report saved to: $REPORT_FILE"

exit 0