#!/usr/bin/env python3
"""
Test dashboard website connection
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and return success/failure."""
    print(f"{description}... ", end="")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ PASS")
            return True, result.stdout
        else:
            print("❌ FAIL")
            print(f"   Error: {result.stderr[:100]}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("⏱️  TIMEOUT")
        return False, "Timeout"
    except Exception as e:
        print(f"⚠️  ERROR: {e}")
        return False, str(e)


def test_dashboard_connection(domain="entrosana.com", port="18789"):
    """Test dashboard connection comprehensively."""
    
    print("="*60)
    print("Dashboard Connection Test")
    print(f"Domain: {domain}")
    print(f"Gateway Port: {port}")
    print("="*60)
    
    tests = []
    
    # Test 1: Local gateway
    success, output = run_command(
        f"curl -s http://localhost:{port}/",
        "1. Local OpenClaw gateway"
    )
    tests.append(("Local Gateway", success))
    
    # Test 2: NGINX local proxy
    success, output = run_command(
        f"curl -s -k -H 'Host: {domain}' https://localhost/",
        "2. NGINX local proxy"
    )
    tests.append(("NGINX Proxy", success))
    
    # Test 3: Public access
    success, output = run_command(
        f"curl -s -I https://{domain}/ 2>/dev/null | head -1",
        "3. Public HTTPS access"
    )
    tests.append(("Public HTTPS", success))
    
    # Test 4: Service status
    success, output = run_command(
        "systemctl is-active nginx",
        "4. NGINX service status"
    )
    tests.append(("NGINX Service", success))
    
    # Test 5: OpenClaw status
    success, output = run_command(
        "openclaw gateway status",
        "5. OpenClaw gateway status"
    )
    tests.append(("OpenClaw Gateway", success))
    
    # Test 6: Port listening
    success, output = run_command(
        f"netstat -tln | grep ':{port} '",
        f"6. Port {port} listening"
    )
    tests.append((f"Port {port}", success))
    
    # Test 7: SSL certificate
    success, output = run_command(
        f"sudo openssl x509 -in /etc/letsencrypt/live/{domain}/fullchain.pem -checkend 86400 2>/dev/null",
        "7. SSL certificate validity"
    )
    tests.append(("SSL Certificate", success))
    
    # Test 8: Firewall (UFW)
    success, output = run_command(
        "sudo ufw status | grep '443/tcp.*ALLOW'",
        "8. Firewall port 443"
    )
    tests.append(("Firewall 443", success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("✅ All tests passed - Dashboard is fully operational!")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed - Dashboard is mostly operational")
    else:
        print("❌ Multiple tests failed - Dashboard needs attention")
    
    # Show failed tests
    failed_tests = [name for name, success in tests if not success]
    if failed_tests:
        print("\nFailed tests:")
        for test in failed_tests:
            print(f"  • {test}")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if "Local Gateway" in failed_tests:
        print("• Start OpenClaw gateway: openclaw gateway restart")
    
    if "NGINX Proxy" in failed_tests or "NGINX Service" in failed_tests:
        print("• Restart NGINX: sudo systemctl restart nginx")
        print("• Check NGINX config: sudo nginx -t")
    
    if "Public HTTPS" in failed_tests:
        print("• Check DNS resolution: dig " + domain)
        print("• Check firewall (all 3 layers)")
        print("• Verify SSL certificate")
    
    if "SSL Certificate" in failed_tests:
        print("• Renew SSL: sudo certbot renew")
        print("• Or obtain new: sudo certbot --nginx -d " + domain)
    
    if "Firewall 443" in failed_tests:
        print("• Allow port 443: sudo ufw allow 443/tcp")
    
    print("\nFor detailed troubleshooting, run:")
    print("  ./diagnose_dashboard.sh")
    print("  ./emergency_repair.sh")
    
    return passed == total


if __name__ == "__main__":
    # Get domain from command line or use default
    domain = sys.argv[1] if len(sys.argv) > 1 else "entrosana.com"
    
    try:
        success = test_dashboard_connection(domain)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during test: {e}")
        sys.exit(1)