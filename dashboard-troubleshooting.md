# Entrosana.com Dashboard Troubleshooting Guide

## Quick Diagnostic Script

```bash
#!/bin/bash
echo "=== Dashboard Connectivity Check ==="

# 1. Check local services
echo "1. Local Services:"
echo "   Gateway: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:18789/ && echo "✅ Running" || echo "❌ Down")"
echo "   NGINX: $(sudo systemctl is-active nginx 2>/dev/null && echo "✅ Active" || echo "❌ Inactive")"

# 2. Check UFW
echo "2. UFW Firewall:"
sudo ufw status | grep -E "(443|18789)" || echo "   ❌ Ports not allowed"

# 3. Check listening ports
echo "3. Listening Ports:"
sudo netstat -tlnp | grep -E ":443|:18789" | awk '{print "   " $4 " -> " $7}'

# 4. Test NGINX proxy
echo "4. NGINX Proxy Test:"
curl -s -o /dev/null -w "   Local: %{http_code}\n" -H "Host: entrosana.com" https://localhost/ 2>/dev/null || echo "   ❌ Local test failed"

echo "=== Summary ==="
echo "If external access fails, check:"
echo "1. AWS Security Group: Port 443 allows 0.0.0.0/0"
echo "2. AWS NACL: Inbound allows destination port, Outbound allows ephemeral ports"
echo "3. UFW: sudo ufw allow 443/tcp"
echo "4. NGINX: sudo systemctl restart nginx"
```

## Common Issues & Fixes

### Issue 1: "net::ERR_CONNECTION_TIMED_OUT"
**Cause**: Firewall blocking at some layer
**Fix**: Check all 3 firewalls:
1. AWS Security Group (port 443)
2. AWS Network ACL (inbound/outbound)
3. Instance UFW (`sudo ufw allow 443/tcp`)

### Issue 2: "disconnected (1006): no reason"
**Cause**: WebSocket connection failing
**Fix**: Check NGINX WebSocket headers:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### Issue 3: Page loads but WebSocket fails
**Cause**: NACL blocking ephemeral ports
**Fix**: Add outbound rule for ports 1024-65535

## AWS Configuration Reference

### Security Group (Must Have):
- Type: HTTPS (443)
- Source: 0.0.0.0/0

### Network ACL (Common Mistakes):
- INBOUND: Rule too restrictive (only port 443, blocks proxied port 18789)
- OUTBOUND: Missing ephemeral port rule (1024-65535)

### Quick Commands:
```bash
# Fix UFW
sudo ufw allow 443/tcp
sudo ufw allow 18789/tcp

# Restart services
sudo systemctl restart nginx
openclaw gateway restart

# Test
curl -I https://entrosana.com/
```

**Dashboard URL**: `https://entrosana.com/#token=1f3c0559f9362ff5ff458c69eed348f6df5a7ec55bbc1287`