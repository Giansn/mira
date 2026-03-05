#!/bin/bash
# diagnose_dashboard_ec2.sh - EC2-specific dashboard diagnostics

set -e

DOMAIN="${1:-your-ec2-domain.com}"
GATEWAY_PORT="${2:-18789}"
EC2_OPTIMIZED="${3:-true}"

echo "🦅 EC2-Specific Dashboard Diagnostics"
echo "====================================="
echo "Domain: $DOMAIN"
echo "Gateway Port: $GATEWAY_PORT"
echo "EC2 Optimized: $EC2_OPTIMIZED"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# EC2 Metadata check
check_ec2_metadata() {
    echo -e "${BLUE}🔍 EC2 Metadata Check${NC}"
    echo "-------------------"
    
    if curl -s http://169.254.169.254/latest/meta-data/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running on EC2 instance${NC}"
        
        # Get basic metadata
        INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "unknown")
        INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "unknown")
        AVAILABILITY_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "unknown")
        PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
        
        echo "   Instance ID: $INSTANCE_ID"
        echo "   Instance Type: $INSTANCE_TYPE"
        echo "   Availability Zone: $AVAILABILITY_ZONE"
        echo "   Public IP: $PUBLIC_IP"
        
        # Check IMDSv2
        TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
                -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null || echo "")
        if [ -n "$TOKEN" ]; then
            echo -e "${GREEN}✅ IMDSv2 available${NC}"
        else
            echo -e "${YELLOW}⚠️  IMDSv1 only (consider upgrading)${NC}"
        fi
        
        return 0
    else
        echo -e "${YELLOW}⚠️  Not running on EC2${NC}"
        PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
        echo "   Detected Public IP: $PUBLIC_IP"
        return 1
    fi
}

# AWS CLI check
check_aws_cli() {
    echo ""
    echo -e "${BLUE}🔍 AWS CLI Check${NC}"
    echo "----------------"
    
    if command -v aws &> /dev/null; then
        echo -e "${GREEN}✅ AWS CLI installed${NC}"
        
        # Check configuration
        if aws sts get-caller-identity &> /dev/null; then
            echo -e "${GREEN}✅ AWS credentials configured${NC}"
            ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")
            echo "   AWS Account: $ACCOUNT_ID"
            return 0
        else
            echo -e "${YELLOW}⚠️  AWS CLI not configured${NC}"
            echo "   Run: aws configure"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  AWS CLI not installed${NC}"
        echo "   Install: sudo apt install awscli"
        return 2
    fi
}

# Security Group check
check_security_group() {
    echo ""
    echo -e "${BLUE}🔍 Security Group Check${NC}"
    echo "-----------------------"
    
    if check_ec2_metadata && check_aws_cli; then
        # Get Security Group info
        SG_INFO=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
            --query 'Reservations[0].Instances[0].SecurityGroups' \
            --output json 2>/dev/null || echo "[]")
        
        if [ "$SG_INFO" != "[]" ]; then
            echo -e "${GREEN}✅ Security Group information retrieved${NC}"
            
            # Extract SG IDs
            SG_IDS=$(echo "$SG_INFO" | jq -r '.[].GroupId' | tr '\n' ' ')
            echo "   Security Group IDs: $SG_IDS"
            
            # Check port 443
            PORT_443=$(echo "$SG_INFO" | jq -r '.[].IpPermissions[] | select(.FromPort==443) | .FromPort' 2>/dev/null || echo "")
            if [ -n "$PORT_443" ]; then
                echo -e "${GREEN}✅ Port 443 allowed in Security Group${NC}"
            else
                echo -e "${RED}❌ Port 443 NOT allowed in Security Group${NC}"
                echo "   Fix: Add inbound rule for HTTPS (port 443) from 0.0.0.0/0"
            fi
            
            # Check port 18789 (optional)
            PORT_GATEWAY=$(echo "$SG_INFO" | jq -r ".[].IpPermissions[] | select(.FromPort==$GATEWAY_PORT) | .FromPort" 2>/dev/null || echo "")
            if [ -n "$PORT_GATEWAY" ]; then
                echo -e "${GREEN}✅ Port $GATEWAY_PORT allowed in Security Group${NC}"
            else
                echo -e "${YELLOW}⚠️  Port $GATEWAY_PORT not explicitly allowed${NC}"
                echo "   Note: This is usually fine as NGINX proxies to localhost"
            fi
            
            # Display all open ports
            echo ""
            echo "   Allowed ports in Security Group:"
            echo "$SG_INFO" | jq -r '.[].IpPermissions[] | "    - \(.FromPort) to \(.ToPort) (\(.IpProtocol))"' 2>/dev/null || echo "    (Unable to parse)"
        else
            echo -e "${YELLOW}⚠️  Could not retrieve Security Group info${NC}"
            echo "   Check IAM permissions or run manually:"
            echo "   aws ec2 describe-security-groups --group-ids YOUR_SG_ID"
        fi
    else
        echo -e "${YELLOW}⚠️  Skipping automated Security Group check${NC}"
        echo "   Manual check required:"
        echo "   1. AWS Console → EC2 → Security Groups"
        echo "   2. Find Security Group for your instance"
        echo "   3. Ensure inbound rule: HTTPS (443) from 0.0.0.0/0"
    fi
}

# Network ACL check
check_network_acl() {
    echo ""
    echo -e "${BLUE}🔍 Network ACL Check${NC}"
    echo "-------------------"
    
    echo -e "${YELLOW}⚠️  Network ACL checks require VPC permissions${NC}"
    echo ""
    echo "Common NACL issues on EC2:"
    echo "1. NACLs are STATEFUL (need separate inbound AND outbound rules)"
    echo "2. Default NACL often denies all after rule 100"
    echo "3. Ephemeral ports (1024-65535) must be allowed outbound"
    echo ""
    echo "Manual check steps:"
    echo "1. AWS Console → VPC → Network ACLs"
    echo "2. Find NACL associated with your subnet"
    echo "3. Check both INBOUND and OUTBOUND tabs"
    echo "4. Look for rules allowing:"
    echo "   - INBOUND: Destination port (after NGINX proxy)"
    echo "   - OUTBOUND: Ephemeral ports (1024-65535)"
    echo ""
    echo "Quick test for NACL issues:"
    echo "If Security Group allows but still can't connect → Likely NACL issue"
}

# DNS check with EC2 IP
check_dns_ec2() {
    echo ""
    echo -e "${BLUE}🔍 DNS Configuration Check${NC}"
    echo "---------------------------"
    
    if check_ec2_metadata; then
        echo "EC2 Public IP: $PUBLIC_IP"
        
        # Get DNS resolution
        DNS_IP=$(dig +short "$DOMAIN" 2>/dev/null | head -1 || echo "")
        
        if [ -n "$DNS_IP" ]; then
            echo "DNS resolves to: $DNS_IP"
            
            if [ "$DNS_IP" = "$PUBLIC_IP" ]; then
                echo -e "${GREEN}✅ DNS correctly points to EC2 instance${NC}"
            else
                echo -e "${RED}❌ DNS points to different IP${NC}"
                echo "   Update DNS A record: $DOMAIN → $PUBLIC_IP"
            fi
        else
            echo -e "${YELLOW}⚠️  DNS not resolving${NC}"
            echo "   Set up DNS A record: $DOMAIN → $PUBLIC_IP"
        fi
        
        # Check if Elastic IP is associated
        if check_aws_cli; then
            EIP_INFO=$(aws ec2 describe-addresses --filters "Name=instance-id,Values=$INSTANCE_ID" \
                --query 'Addresses[0].PublicIp' --output text 2>/dev/null || echo "")
            
            if [ -n "$EIP_INFO" ] && [ "$EIP_INFO" != "None" ]; then
                echo -e "${GREEN}✅ Elastic IP associated: $EIP_INFO${NC}"
                if [ "$EIP_INFO" != "$PUBLIC_IP" ]; then
                    echo -e "${YELLOW}⚠️  Public IP differs from Elastic IP${NC}"
                    echo "   Instance may have been stopped/started"
                fi
            else
                echo -e "${YELLOW}⚠️  No Elastic IP associated${NC}"
                echo "   Consider associating Elastic IP for consistent DNS"
            fi
        fi
    else
        echo "Cannot determine EC2 IP for DNS check"
    fi
}

# EC2 connectivity tests
check_ec2_connectivity() {
    echo ""
    echo -e "${BLUE}🔍 EC2 Connectivity Tests${NC}"
    echo "---------------------------"
    
    # Test local services
    echo "Local gateway test:"
    if curl -s http://localhost:$GATEWAY_PORT > /dev/null; then
        echo -e "  ${GREEN}✅ Local gateway accessible${NC}"
    else
        echo -e "  ${RED}❌ Local gateway not accessible${NC}"
        echo "    Run: openclaw gateway restart"
    fi
    
    # Test NGINX locally
    echo "NGINX local test:"
    if curl -s -k -H "Host: $DOMAIN" https://localhost/health > /dev/null; then
        echo -e "  ${GREEN}✅ NGINX responding locally${NC}"
    else
        echo -e "  ${RED}❌ NGINX not responding locally${NC}"
        echo "    Run: sudo systemctl restart nginx"
    fi
    
    # Test public access
    echo "Public access test:"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/ 2>/dev/null || echo "FAILED")
    case $STATUS in
        200|301|302)
            echo -e "  ${GREEN}✅ Public access OK ($STATUS)${NC}"
            ;;
        000)
            echo -e "  ${RED}❌ Connection failed${NC}"
            echo "    Likely firewall or DNS issue"
            ;;
        502|503|504)
            echo -e "  ${YELLOW}⚠️  Server error ($STATUS)${NC}"
            echo "    Check NGINX and gateway services"
            ;;
        *)
            echo -e "  ${YELLOW}⚠️  Unexpected status ($STATUS)${NC}"
            ;;
    esac
    
    # Test WebSocket
    echo "WebSocket test:"
    WS_RESPONSE=$(curl -s -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
        -H "Host: $DOMAIN" https://$DOMAIN/ 2>/dev/null | head -1 || echo "")
    if echo "$WS_RESPONSE" | grep -q "101"; then
        echo -e "  ${GREEN}✅ WebSocket upgrade successful${NC}"
    else
        echo -e "  ${YELLOW}⚠️  WebSocket upgrade may have issues${NC}"
        echo "    Check NGINX WebSocket headers"
    fi
}

# EC2 resource check
check_ec2_resources() {
    echo ""
    echo -e "${BLUE}🔍 EC2 Resource Check${NC}"
    echo "----------------------"
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "CPU Usage: ${CPU_USAGE}%"
    if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
        echo -e "  ${YELLOW}⚠️  High CPU usage${NC}"
    fi
    
    # Memory usage
    MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
    MEM_USED=$(free -m | awk '/^Mem:/{print $3}')
    MEM_PERCENT=$((MEM_USED * 100 / MEM_TOTAL))
    echo "Memory Usage: ${MEM_PERCENT}% (${MEM_USED}MB / ${MEM_TOTAL}MB)"
    if (( MEM_PERCENT > 80 )); then
        echo -e "  ${YELLOW}⚠️  High memory usage${NC}"
    fi
    
    # Disk usage
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
    echo "Disk Usage: ${DISK_USAGE}%"
    if (( DISK_USAGE > 80 )); then
        echo -e "  ${YELLOW}⚠️  High disk usage${NC}"
    fi
    
    # Check swap
    SWAP_TOTAL=$(free -m | awk '/^Swap:/{print $2}')
    if (( SWAP_TOTAL > 0 )); then
        SWAP_USED=$(free -m | awk '/^Swap:/{print $3}')
        echo "Swap Usage: ${SWAP_USED}MB / ${SWAP_TOTAL}MB"
        if (( SWAP_USED > 0 )); then
            echo -e "  ${YELLOW}⚠️  Swap being used (memory pressure)${NC}"
        fi
    fi
}

# Main diagnostic function
run_diagnostics() {
    echo "🦅 EC2 Dashboard Diagnostics"
    echo "============================"
    
    # Run all checks
    check_ec2_metadata
    check_aws_cli
    check_security_group
    check_network_acl
    check_dns_ec2
    check_ec2_connectivity
    check_ec2_resources
    
    # Summary
    echo ""
    echo -e "${BLUE}📋 Diagnostic Summary${NC}"
    echo "==================="
    echo ""
    echo "Most common EC2 issues:"
    echo "1. Security Group missing port 443 rule"
    echo "2. Network ACL blocking traffic"
    echo "3. DNS not pointing to correct IP"
    echo "4. Instance out of resources (CPU/Memory)"
    echo ""
    echo "Quick fixes:"
    echo "1. Add Security Group rule: HTTPS (443) from 0.0.0.0/0"
    echo "2. Check Network ACL outbound rules (ephemeral ports)"
    echo "3. Update DNS A record to: $PUBLIC_IP"
    echo "4. Consider upgrading instance type if resource constrained"
    echo ""
    echo "Run emergency repair:"
    echo "./emergency_repair.sh $DOMAIN $GATEWAY_PORT"
    echo ""
    echo "Detailed logs:"
    echo "  NGINX: sudo tail -50 /var/log/nginx/error.log"
    echo "  System: sudo journalctl -u nginx -u openclaw-gateway --since \"1 hour ago\""
    echo ""
    echo "EC2 Console links:"
    echo "  Instance: https://$REGION.console.aws.amazon.com/ec2/home?region=$REGION#InstanceDetails:instanceId=$INSTANCE_ID"
    echo "  Security Groups: https://$REGION.console.aws.amazon.com/ec2/home?region=$REGION#SecurityGroups:"
}

# Run diagnostics
run_diagnostics "$@"