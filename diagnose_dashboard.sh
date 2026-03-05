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
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        if sudo openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -checkend 86400 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ VALID (>1 day)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  EXPIRING SOON${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ NOT FOUND${NC}"
        return 2
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