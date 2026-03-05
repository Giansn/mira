#!/bin/bash
# setup_dashboard_ec2.sh - EC2-optimized dashboard setup

set -e

# Configuration
DOMAIN="${1:-your-ec2-domain.com}"
GATEWAY_PORT="${2:-18789}"
EC2_OPTIMIZED="${3:-true}"

echo "🦅 EC2-Optimized OpenClaw Dashboard Setup"
echo "=========================================="
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

# EC2 Metadata functions
get_ec2_metadata() {
    echo -e "${BLUE}🔍 Gathering EC2 metadata...${NC}"
    
    # Try to get EC2 metadata
    if curl -s http://169.254.169.254/latest/meta-data/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running on EC2 instance${NC}"
        
        # Get instance metadata
        INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "unknown")
        INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "unknown")
        AVAILABILITY_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "unknown")
        REGION=$(echo "$AVAILABILITY_ZONE" | sed 's/[a-z]$//')
        PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
        
        echo "   Instance ID: $INSTANCE_ID"
        echo "   Instance Type: $INSTANCE_TYPE"
        echo "   Availability Zone: $AVAILABILITY_ZONE"
        echo "   Region: $REGION"
        echo "   Public IP: $PUBLIC_IP"
        
        return 0
    else
        echo -e "${YELLOW}⚠️  Not running on EC2 (or metadata service unavailable)${NC}"
        PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
        echo "   Detected Public IP: $PUBLIC_IP"
        return 1
    fi
}

# Check AWS CLI availability
check_aws_cli() {
    echo -e "${BLUE}🔍 Checking AWS CLI...${NC}"
    
    if command -v aws &> /dev/null; then
        echo -e "${GREEN}✅ AWS CLI available${NC}"
        
        # Check if configured
        if aws sts get-caller-identity &> /dev/null; then
            echo -e "${GREEN}✅ AWS credentials configured${NC}"
            ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")
            echo "   AWS Account: $ACCOUNT_ID"
            return 0
        else
            echo -e "${YELLOW}⚠️  AWS CLI not configured or no permissions${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  AWS CLI not installed${NC}"
        return 2
    fi
}

# Check Security Group configuration
check_security_group() {
    echo -e "${BLUE}🔍 Checking Security Group configuration...${NC}"
    
    if [ "$EC2_OPTIMIZED" = "true" ] && get_ec2_metadata && check_aws_cli; then
        # Try to get Security Group info
        SG_INFO=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
            --query 'Reservations[0].Instances[0].SecurityGroups' \
            --output json 2>/dev/null || echo "[]")
        
        if [ "$SG_INFO" != "[]" ]; then
            echo -e "${GREEN}✅ Security Group information retrieved${NC}"
            
            # Check for port 443
            if echo "$SG_INFO" | jq -e '.[].IpPermissions[] | select(.FromPort==443)' > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Port 443 is allowed in Security Group${NC}"
            else
                echo -e "${YELLOW}⚠️  Port 443 may not be allowed in Security Group${NC}"
                echo "   You may need to add an inbound rule for HTTPS (port 443)"
            fi
            
            # Display Security Group IDs
            SG_IDS=$(echo "$SG_INFO" | jq -r '.[].GroupId' | tr '\n' ' ')
            echo "   Security Group IDs: $SG_IDS"
        fi
    else
        echo -e "${YELLOW}⚠️  Skipping Security Group check${NC}"
        echo "   Manual check recommended:"
        echo "   1. Go to AWS Console → EC2 → Security Groups"
        echo "   2. Find your instance's Security Group"
        echo "   3. Add inbound rule: HTTPS (port 443) from 0.0.0.0/0"
    fi
}

# Check Network ACL configuration
check_network_acl() {
    echo -e "${BLUE}🔍 Checking Network ACL configuration...${NC}"
    
    if [ "$EC2_OPTIMIZED" = "true" ] && get_ec2_metadata && check_aws_cli; then
        echo -e "${YELLOW}⚠️  Network ACL check requires VPC permissions${NC}"
        echo "   Manual check recommended:"
        echo "   1. Go to AWS Console → VPC → Network ACLs"
        echo "   2. Find NACL associated with your subnet"
        echo "   3. Ensure rules allow:"
        echo "      - INBOUND: Destination port (after NGINX proxy)"
        echo "      - OUTBOUND: Ephemeral ports (1024-65535)"
    else
        echo -e "${YELLOW}⚠️  Network ACL check skipped${NC}"
        echo "   Common NACL issues:"
        echo "   1. NACLs are STATEFUL (need inbound AND outbound rules)"
        echo "   2. Must allow ephemeral ports for responses"
        echo "   3. Rule 100 often blocks everything after port 443"
    fi
}

# Generate EC2-specific instructions
generate_ec2_instructions() {
    echo ""
    echo -e "${BLUE}📋 EC2-Specific Instructions${NC}"
    echo "================================="
    
    if get_ec2_metadata; then
        echo "1. DNS Configuration:"
        echo "   Add A record in your DNS provider:"
        echo "   $DOMAIN → $PUBLIC_IP"
        echo ""
        
        echo "2. Security Group (if not auto-configured):"
        echo "   Inbound rule needed:"
        echo "   - Type: HTTPS"
        echo "   - Protocol: TCP"
        echo "   - Port: 443"
        echo "   - Source: 0.0.0.0/0"
        echo ""
        
        echo "3. Network ACL (critical for EC2):"
        echo "   Check both INBOUND and OUTBOUND rules"
        echo "   OUTBOUND must allow ephemeral ports (1024-65535)"
        echo ""
        
        echo "4. Elastic IP (recommended):"
        echo "   Associate Elastic IP for consistent DNS"
        echo "   Command: aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id eipalloc-xxx"
    else
        echo "1. Get your public IP:"
        echo "   Public IP: $PUBLIC_IP"
        echo ""
        echo "2. Configure DNS:"
        echo "   Add A record: $DOMAIN → $PUBLIC_IP"
        echo ""
        echo "3. Configure firewall/security group:"
        echo "   Allow inbound traffic on port 443 (HTTPS)"
    fi
    
    echo "5. Test connection:"
    echo "   curl -I https://$DOMAIN/"
    echo ""
    echo "6. Dashboard URL will be:"
    echo "   https://$DOMAIN/#token=GENERATED_TOKEN"
}

# Main setup function
setup_dashboard() {
    echo ""
    echo -e "${BLUE}🚀 Starting dashboard setup...${NC}"
    
    # Run the standard setup
    if [ -f "/home/ubuntu/.openclaw/workspace/setup_dashboard.sh" ]; then
        echo "Running standard setup script..."
        /home/ubuntu/.openclaw/workspace/setup_dashboard.sh "$DOMAIN" "$GATEWAY_PORT"
    else
        echo -e "${RED}❌ Standard setup script not found${NC}"
        echo "Please ensure setup_dashboard.sh exists in the workspace"
        return 1
    fi
}

# Main execution
main() {
    echo "🦅 EC2 Dashboard Setup Tool"
    echo "==========================="
    
    # Check if domain is provided
    if [ "$DOMAIN" = "your-ec2-domain.com" ]; then
        echo -e "${YELLOW}⚠️  Using default domain: your-ec2-domain.com${NC}"
        echo "   Please replace with your actual domain"
        echo "   Usage: $0 yourdomain.com [port]"
        echo ""
    fi
    
    # Run checks
    get_ec2_metadata
    echo ""
    
    if [ "$EC2_OPTIMIZED" = "true" ]; then
        check_security_group
        echo ""
        check_network_acl
        echo ""
    fi
    
    # Generate instructions
    generate_ec2_instructions
    
    # Ask for confirmation
    echo ""
    read -p "Continue with setup? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_dashboard
        
        # Final EC2-specific notes
        echo ""
        echo -e "${GREEN}✅ EC2 Dashboard Setup Complete!${NC}"
        echo ""
        echo "EC2-Specific Next Steps:"
        echo "1. Wait for DNS propagation (5-30 minutes)"
        echo "2. Test from different locations:"
        echo "   curl -I https://$DOMAIN/"
        echo "3. Monitor CloudWatch logs for issues"
        echo "4. Set up billing alerts in AWS Console"
        echo ""
        echo "For EC2 issues, run:"
        echo "./diagnose_dashboard.sh $DOMAIN $GATEWAY_PORT"
        echo ""
        echo "Emergency repair:"
        echo "./emergency_repair.sh $DOMAIN $GATEWAY_PORT"
    else
        echo -e "${YELLOW}⚠️  Setup cancelled${NC}"
        echo ""
        echo "You can run these checks manually:"
        echo "1. Security Group: AWS Console → EC2 → Security Groups"
        echo "2. Network ACL: AWS Console → VPC → Network ACLs"
        echo "3. DNS: dig $DOMAIN +short"
        echo ""
        echo "Or run the standard setup:"
        echo "./setup_dashboard.sh $DOMAIN $GATEWAY_PORT"
    fi
}

# Run main function
main "$@"