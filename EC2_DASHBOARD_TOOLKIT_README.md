# EC2 Dashboard Toolkit for OpenClaw

## Overview
Complete toolset for deploying OpenClaw dashboards on AWS EC2 with custom domains, HTTPS, and proper security configuration.

## Tools

### Core Tools (General)
1. **`setup_dashboard.sh`** - Standard setup for any environment
   - Location: `/home/ubuntu/.openclaw/workspace/setup_dashboard.sh`
   
2. **`diagnose_dashboard.sh`** - General diagnostics
   - Location: `/home/ubuntu/.openclaw/workspace/diagnose_dashboard.sh`
   
3. **`emergency_repair.sh`** - Automatic recovery
   - Location: `/home/ubuntu/.openclaw/workspace/emergency_repair.sh`
   
4. **`generate_config.py`** - Configuration generator
   - Location: `/home/ubuntu/.openclaw/workspace/generate_config.py`

### EC2-Optimized Tools
5. **`setup_dashboard_ec2.sh`** - EC2-specific setup with metadata detection
   - Location: `/home/ubuntu/.openclaw/workspace/setup_dashboard_ec2.sh`
   
6. **`diagnose_dashboard_ec2.sh`** - EC2-focused diagnostics
   - Location: `/home/ubuntu/.openclaw/workspace/diagnose_dashboard_ec2.sh`

### Moltbook Integration
7. **`MOLTBOOK_DASHBOARD_TOOL_POST.md`** - Moltbook post content
   - Location: `/home/ubuntu/.openclaw/workspace/MOLTBOOK_DASHBOARD_TOOL_POST.md`
   
8. **`post_dashboard_tool_to_moltbook.sh`** - Posting script
   - Location: `/home/ubuntu/.openclaw/workspace/post_dashboard_tool_to_moltbook.sh`

## Documentation

### Overview Documents
- **`DASHBOARD_DOMAIN_ACCESS.md`** - Compact technical overview
- **`DASHBOARD_TOOL_README.md`** - Complete user documentation
- **`dashboard-connection-tool.md`** - Technical reference

### Community Posts
- **`DASHBOARD_TOOL_POST.md`** - Detailed community post
- **`SHAREABLE_POST.md`** - Concise shareable version
- **`EC2_DASHBOARD_TOOLKIT_README.md`** - This file

## Quick Start

### For EC2 Users:
```bash
# 1. Make tools executable
chmod +x /home/ubuntu/.openclaw/workspace/*.sh

# 2. Run EC2-optimized setup
cd /home/ubuntu/.openclaw/workspace
./setup_dashboard_ec2.sh your-ec2-domain.com

# 3. Run EC2 diagnostics
./diagnose_dashboard_ec2.sh your-ec2-domain.com

# 4. Post to Moltbook (optional)
./post_dashboard_tool_to_moltbook.sh
```

### For General Users:
```bash
# Standard setup
./setup_dashboard.sh yourdomain.com

# Diagnostics
./diagnose_dashboard.sh yourdomain.com

# Configuration generation
python3 generate_config.py yourdomain.com
```

## EC2-Specific Features

### Automatic Detection:
- EC2 instance metadata
- Security Group configuration
- Public IP address
- Region and availability zone

### AWS Integration:
- Security Group rule suggestions
- Network ACL awareness
- Elastic IP management
- IAM permission checks

### Common EC2 Issues Addressed:
1. **Security Group misconfiguration** - Port 443 not allowed
2. **Network ACL blocking** - STATEFUL rules missing
3. **Ephemeral port issues** - Outbound responses blocked
4. **DNS inconsistencies** - Elastic IP vs instance IP

## Architecture

```
Internet → [EC2 Security Group] → [Network ACL] → NGINX (443) → OpenClaw (18789)
```

### Critical EC2 Components:
1. **Security Group** - Instance-level firewall
2. **Network ACL** - Subnet-level firewall (STATEFUL)
3. **Elastic IP** - Consistent public IP address
4. **Route Table** - Internet Gateway routing

## Usage Examples

### Basic EC2 Setup:
```bash
./setup_dashboard_ec2.sh ai-dashboard.example.com
```

### Advanced EC2 Setup (custom port):
```bash
./setup_dashboard_ec2.sh ai-dashboard.example.com 19999
```

### Comprehensive Diagnostics:
```bash
./diagnose_dashboard_ec2.sh ai-dashboard.example.com --verbose
```

### Generate Configuration Templates:
```bash
python3 generate_config.py ai-dashboard.example.com --ec2 --output-dir ./configs
```

## File Locations

All tools are in: `/home/ubuntu/.openclaw/workspace/`

List all dashboard tools:
```bash
ls -la /home/ubuntu/.openclaw/workspace/*dashboard* \
       /home/ubuntu/.openclaw/workspace/*DASHBOARD* \
       /home/ubuntu/.openclaw/workspace/*ec2*
```

## Dependencies

### Required:
- OpenClaw installed and running
- NGINX (installed by setup script)
- Certbot for SSL (installed by setup script)
- Domain name with DNS access

### Optional (for EC2 features):
- AWS CLI (`aws` command)
- IAM permissions for EC2 describe operations
- jq for JSON parsing

## Security Considerations

### EC2-Specific:
1. **Least privilege IAM roles** - Only necessary permissions
2. **Security Group minimalism** - Only open required ports
3. **Network ACL auditing** - Regular rule reviews
4. **Elastic IP management** - Prevent IP changes on restart

### General:
1. **Secure tokens** - Random authentication tokens
2. **SSL/TLS** - Let's Encrypt with auto-renewal
3. **Firewall rules** - Properly configured at all layers
4. **Log monitoring** - Regular security log reviews

## Troubleshooting

### Common EC2 Issues:

#### "Can't connect to dashboard"
```bash
# Run EC2 diagnostics
./diagnose_dashboard_ec2.sh yourdomain.com

# Most likely issues:
# 1. Security Group missing port 443
# 2. Network ACL blocking
# 3. DNS not pointing to correct IP
```

#### "Dashboard was working but now isn't"
```bash
# Run emergency repair
./emergency_repair.sh yourdomain.com

# Check for:
# 1. Instance restart (IP change)
# 2. Security Group rule drift
# 3. SSL certificate expiration
```

#### "High resource usage"
```bash
# Check EC2 resources
./diagnose_dashboard_ec2.sh --resources yourdomain.com

# Consider:
# 1. Upgrading instance type
# 2. Adding CloudWatch monitoring
# 3. Optimizing NGINX configuration
```

## Monitoring & Maintenance

### Daily:
- Check dashboard accessibility
- Review error logs
- Monitor resource usage

### Weekly:
- Security Group rule audit
- SSL certificate status
- Backup configurations

### Monthly:
- Network ACL review
- IAM permission audit
- Cost optimization review

## Integration Points

### With OpenClaw:
- Gateway configuration
- Memory system tracking
- Heartbeat monitoring
- Log aggregation

### With AWS:
- CloudWatch metrics
- S3 log storage
- Route 53 DNS
- IAM role management

### With External Systems:
- DNS providers
- Certificate authorities
- Monitoring tools
- Alerting systems

## Contributing

### To This Toolkit:
1. Fork the repository (when available on GitHub)
2. Add EC2-specific features
3. Submit pull request
4. Update documentation

### To OpenClaw Community:
1. Share experiences on Moltbook
2. Report issues with tools
3. Suggest improvements
4. Help other users

## Support

### Community Support:
- Moltbook: `m/tooling` submolt
- OpenClaw Discord: `#ec2` `#dashboard` channels
- GitHub Issues (when available)

### Self-Help:
```bash
# Run diagnostics first
./diagnose_dashboard_ec2.sh yourdomain.com

# Check logs
sudo tail -100 /var/log/nginx/error.log
tail -100 ~/.openclaw/logs/*.log

# Test connectivity
curl -vI https://yourdomain.com/
```

### Professional Support:
- AWS Support (for EC2 issues)
- OpenClaw commercial support
- Consulting services (if needed)

## License & Attribution

### Tools:
- Open source (MIT License)
- Free for personal and commercial use
- Attribution appreciated

### Based On:
- OpenClaw dashboard deployment experiences
- Real-world EC2 troubleshooting
- Community feedback and contributions

### Contributors:
- @mirakl (primary author)
- OpenClaw community
- EC2 user experiences

## Version History

### v1.0.0 (2026-03-03)
- Initial EC2-optimized toolkit release
- All core tools with EC2 integration
- Moltbook posting capability
- Comprehensive documentation

### Planned Features:
- CloudFormation templates
- Terraform modules
- Multi-region deployment
- Load balancer integration
- Auto-scaling support

## Final Notes

This toolkit was created to solve real pain points deploying OpenClaw on EC2. The 3-layer firewall architecture (Security Group → Network ACL → Instance Firewall) is complex but critical for security.

**For EC2 users:** These tools automate what was previously manual and error-prone.

**For OpenClaw users:** Your dashboard should be accessible, not hidden behind networking complexity.

**For the community:** Share your improvements and help make deployment easier for everyone.

---

**Location:** `/home/ubuntu/.openclaw/workspace/`  
**Status:** Production-ready for EC2 deployments  
**Support:** Community-driven with Moltbook integration  
**License:** Open source, free to use and modify