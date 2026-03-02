#!/usr/bin/env python3
"""
Process external terminal links and provide access instructions.
"""

import urllib.parse
import sys

def parse_termius_link(link):
    """Parse Termius multiplayer link."""
    try:
        parsed = urllib.parse.urlparse(link)
        query = urllib.parse.parse_qs(parsed.query)
        
        details = {
            'peer_id': query.get('peerId', [''])[0],
            'terminal_title': query.get('terminalTitle', [''])[0],
            'connection_id': query.get('connectionId', [''])[0],
            'version': query.get('version', [''])[0],
            'pwd': query.get('pwd', [''])[0],
            'host': '172.31.14.61',
            'port': 22,
            'user': 'ubuntu'
        }
        
        return details
    except Exception as e:
        return {'error': str(e)}

def generate_access_instructions(details):
    """Generate access instructions from link details."""
    if 'error' in details:
        return f"Error parsing link: {details['error']}"
    
    instructions = [
        "=" * 60,
        "EXTERNAL TERMINAL ACCESS INSTRUCTIONS",
        "=" * 60,
        "",
        f"Termius Multiplayer Session:",
        f"  • Terminal: {details.get('terminal_title', 'Unknown')}",
        f"  • Peer ID: {details.get('peer_id', 'Unknown')[:8]}...",
        f"  • Version: {details.get('version', 'Unknown')}",
        "",
        "SSH Access:",
        f"  ssh {details['user']}@{details['host']}",
        f"  Port: {details['port']}",
        "",
        "Claude Code Access (after SSH):",
        "  claude",
        "",
        "Direct Claude via SSH:",
        f"  ssh {details['user']}@{details['host']} -t 'claude'",
        "",
        "Web Interfaces:",
        "  • OpenClaw Control: http://172.31.14.61:18789/",
        "  • Memory Visualization: http://172.31.14.61:5000/",
        "",
        "=" * 60
    ]
    
    return "\n".join(instructions)

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 process_link.py <termius_link>")
        print("\nExample:")
        print('python3 process_link.py "https://termius.com/terminal-multiplayer#peerId=..."')
        sys.exit(1)
    
    link = sys.argv[1]
    print(f"Processing link: {link[:50]}...")
    
    details = parse_termius_link(link)
    instructions = generate_access_instructions(details)
    
    print(instructions)
    
    # Also provide quick commands
    print("\n" + "=" * 60)
    print("QUICK COMMANDS:")
    print("=" * 60)
    print(f"# SSH to server")
    print(f"ssh ubuntu@172.31.14.61")
    print()
    print(f"# SSH with Claude directly")
    print(f"ssh ubuntu@172.31.14.61 -t 'claude'")
    print()
    print(f"# Check Claude installation")
    print(f"ssh ubuntu@172.31.14.61 'which claude && claude --help | head -5'")

if __name__ == "__main__":
    main()