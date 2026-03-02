#!/usr/bin/env python3
"""
Check ACP (Agent Control Protocol) status and configuration.
"""

import subprocess
import json
import os
import sys

def run_command(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_acp_status():
    """Check ACP installation and configuration status."""
    print("🔍 Checking ACP (Agent Control Protocol) Status")
    print("=" * 50)
    
    # 1. Check if openclaw acp command exists
    print("\n1. Checking OpenClaw ACP command...")
    code, out, err = run_command("openclaw acp --help")
    if code == 0:
        print("   ✅ OpenClaw ACP command available")
        # Extract version info
        if "Usage: openclaw acp" in out:
            print("   📋 ACP CLI is functional")
    else:
        print("   ❌ OpenClaw ACP command not available")
        print(f"   Error: {err}")
    
    # 2. Check for acpx plugin
    print("\n2. Checking for acpx runtime plugin...")
    code, out, err = run_command("npm list -g | grep -i acpx")
    if code == 0 and "acpx" in out.lower():
        print("   ✅ acpx plugin found")
        print(f"   Output: {out.strip()}")
    else:
        print("   ❌ acpx plugin not found")
        print("   Note: Error message suggests 'Install and enable the acpx runtime plugin'")
    
    # 3. Check OpenClaw config for ACP settings
    print("\n3. Checking OpenClaw configuration...")
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "acp" in config:
                print("   ✅ ACP configuration found")
                acp_config = config.get("acp", {})
                print(f"   Enabled: {acp_config.get('enabled', 'not set')}")
                
                providers = acp_config.get("providers", {})
                if providers:
                    print(f"   Providers configured: {', '.join(providers.keys())}")
                else:
                    print("   ⚠️ No ACP providers configured")
            else:
                print("   ⚠️ No ACP section in configuration")
        except json.JSONDecodeError:
            print("   ❌ Could not parse configuration file")
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
    else:
        print("   ⚠️ OpenClaw configuration file not found")
    
    # 4. Test ACP client (if available)
    print("\n4. Testing ACP client...")
    code, out, err = run_command("timeout 5 openclaw acp client --help 2>&1")
    if code == 0:
        print("   ✅ ACP client available")
    else:
        print("   ⚠️ ACP client test failed or timed out")
        if "not configured" in err or "not configured" in out:
            print("   💡 ACP runtime backend not configured")
    
    # 5. Check environment variables for API keys
    print("\n5. Checking for AI provider API keys...")
    api_keys = {
        "ANTHROPIC_API_KEY": "Claude/Anthropic",
        "OPENAI_API_KEY": "OpenAI/Codex",
        "GOOGLE_API_KEY": "Google/Gemini"
    }
    
    found_keys = []
    for env_var, provider in api_keys.items():
        if os.getenv(env_var):
            found_keys.append(f"{provider} ({env_var})")
    
    if found_keys:
        print(f"   ✅ Found API keys: {', '.join(found_keys)}")
    else:
        print("   ⚠️ No AI provider API keys found in environment")
        print("   💡 Set environment variables for ACP providers:")
        for env_var, provider in api_keys.items():
            print(f"     export {env_var}=your-key-here  # {provider}")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("- ACP CLI command: Available" if code == 0 else "- ACP CLI command: Not available")
    print("- acpx plugin: Not found (needs installation)")
    print("- Configuration: Basic check complete")
    print("- API keys: Check environment variables")
    print("\n🔧 Next steps:")
    print("1. Install acpx runtime plugin")
    print("2. Configure ACP providers in OpenClaw config")
    print("3. Set API key environment variables")
    print("4. Test with: openclaw acp client")

if __name__ == "__main__":
    check_acp_status()