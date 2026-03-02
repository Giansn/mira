#!/usr/bin/env python3
"""
Print CLI API information for various tools.
"""

import subprocess
import json
import sys

def print_claude_api():
    """Print Claude CLI API information."""
    print("=" * 60)
    print("CLAUDE CODE CLI API")
    print("=" * 60)
    
    try:
        # Get Claude help
        result = subprocess.run(["claude", "--help"], 
                              capture_output=True, text=True, timeout=5)
        print("Claude CLI Help:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    except Exception as e:
        print(f"Error getting Claude help: {e}")
    
    print("\n" + "-" * 40)
    print("Common Claude Commands:")
    print("-" * 40)
    print("claude                         # Interactive session")
    print("claude --print 'message'       # Non-interactive output")
    print("claude --continue              # Continue last conversation")
    print("claude --add-dir ./src         # Add directory access")
    print("echo 'msg' | claude            # Pipe input (may not work)")

def print_openclaw_api():
    """Print OpenClaw CLI API information."""
    print("\n" + "=" * 60)
    print("OPENCLAW CLI API")
    print("=" * 60)
    
    try:
        # Get OpenClaw help
        result = subprocess.run(["openclaw", "--help"], 
                              capture_output=True, text=True, timeout=5)
        print("OpenClaw CLI Help:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    except Exception as e:
        print(f"Error getting OpenClaw help: {e}")
    
    print("\n" + "-" * 40)
    print("Common OpenClaw Commands:")
    print("-" * 40)
    print("openclaw gateway status        # Check gateway")
    print("openclaw gateway start/stop    # Control gateway")
    print("openclaw devices list          # List paired devices")
    print("openclaw devices approve <id>  # Approve device")
    print("openclaw status                # System status")

def print_mcporter_api():
    """Print MCPorter CLI API information."""
    print("\n" + "=" * 60)
    print("MCPORTER CLI API")
    print("=" * 60)
    
    try:
        # Get mcporter help
        result = subprocess.run(["mcporter", "--help"], 
                              capture_output=True, text=True, timeout=5)
        print("MCPorter CLI Help:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    except Exception as e:
        print(f"Error getting MCPorter help: {e}")
    
    print("\n" + "-" * 40)
    print("Common MCPorter Commands:")
    print("-" * 40)
    print("mcporter list                  # List MCP servers")
    print("mcporter call <server.tool>    # Call MCP tool")
    print("mcporter config list           # List config")
    print("mcporter auth <server>         # Authenticate")
    print("mcporter daemon start          # Start daemon")

def print_ssh_api():
    """Print SSH API information."""
    print("\n" + "=" * 60)
    print("SSH API")
    print("=" * 60)
    
    print("Current Server:")
    print(f"  Host: 172.31.14.61")
    print(f"  Port: 22")
    print(f"  User: ubuntu")
    
    print("\n" + "-" * 40)
    print("SSH Commands:")
    print("-" * 40)
    print("ssh ubuntu@172.31.14.61                    # Basic SSH")
    print("ssh ubuntu@172.31.14.61 -t 'claude'        # SSH with Claude")
    print("ssh ubuntu@172.31.14.61 'ls -la'           # Remote command")
    print("scp file.txt ubuntu@172.31.14.61:~/        # Copy file")

def print_curl_api():
    """Print cURL API for web interfaces."""
    print("\n" + "=" * 60)
    print("CURL API FOR WEB INTERFACES")
    print("=" * 60)
    
    print("OpenClaw Control UI:")
    print("  curl http://172.31.14.61:18789/")
    print("  curl http://172.31.14.61:18789/status")
    
    print("\nMemory Visualization:")
    print("  curl http://172.31.14.61:5000/")
    print("  curl http://172.31.14.61:5000/api/stats")
    
    print("\n" + "-" * 40)
    print("Common cURL Options:")
    print("-" * 40)
    print("curl -s                         # Silent mode")
    print("curl -o file.txt                # Save output")
    print("curl -H 'Header: value'         # Add header")
    print("curl -X POST -d 'data'          # POST request")

def print_git_api():
    """Print Git API information."""
    print("\n" + "=" * 60)
    print("GIT API")
    print("=" * 60)
    
    print("Repository: /home/ubuntu/.openclaw/workspace")
    print("Remote: https://github.com/Giansn/mira.git")
    
    print("\n" + "-" * 40)
    print("Common Git Commands:")
    print("-" * 40)
    print("git status                      # Check status")
    print("git add .                       # Stage all")
    print("git commit -m 'message'         # Commit")
    print("git push origin master          # Push")
    print("git pull                        # Pull updates")
    print("git log --oneline -5            # Recent commits")

def print_termius_api():
    """Print Termius API information."""
    print("\n" + "=" * 60)
    print("TERMIUS MULTIPLAYER API")
    print("=" * 60)
    
    print("Termius Multiplayer Links:")
    print("  Format: https://termius.com/terminal-multiplayer#...")
    print("  Contains: peerId, terminalTitle, connectionId, version, pwd")
    
    print("\n" + "-" * 40)
    print("Current Session:")
    print("-" * 40)
    print("  Peer ID: 132f452f-daa2-41f6-a27a-f4762c512f5a")
    print("  Terminal: Mira (1)")
    print("  Connection: da365542-7765-490e-9c61-1f9dc1f83703")
    print("  Version: 2.0.0")
    
    print("\nNote: Termius CLI not installed. Use Termius app to join.")

def print_all_apis():
    """Print all CLI APIs."""
    print_claude_api()
    print_openclaw_api()
    print_mcporter_api()
    print_ssh_api()
    print_curl_api()
    print_git_api()
    print_termius_api()
    
    print("\n" + "=" * 60)
    print("QUICK REFERENCE")
    print("=" * 60)
    print("Claude:      claude --print 'message'")
    print("OpenClaw:    openclaw gateway status")
    print("SSH:         ssh ubuntu@172.31.14.61")
    print("Git:         git status && git push")
    print("cURL:        curl http://172.31.14.61:18789/")
    print("Termius:     Use app with multiplayer link")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        api = sys.argv[1].lower()
        if api == "claude":
            print_claude_api()
        elif api == "openclaw":
            print_openclaw_api()
        elif api == "mcporter":
            print_mcporter_api()
        elif api == "ssh":
            print_ssh_api()
        elif api == "curl":
            print_curl_api()
        elif api == "git":
            print_git_api()
        elif api == "termius":
            print_termius_api()
        else:
            print(f"Unknown API: {api}")
            print("Available: claude, openclaw, mcporter, ssh, curl, git, termius, all")
    else:
        print_all_apis()

if __name__ == "__main__":
    main()