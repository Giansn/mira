#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace')
import asyncio

from telclaw.policy_engine import PolicyEngine
from telclaw.gate import Gate
from telclaw.executor import Executor
from telclaw.bridge import TelClawBridge

async def main():
    pe = PolicyEngine(safe_max=3, mock_mode=True)
    g = Gate()
    ex = Executor()
    bridge = TelClawBridge(pe, g, ex)

    user = "dryrun-user"
    commands = [
        ("status", ""),
        ("restart-service", ""),
        ("dangerous-action", "--force"),
    ]

    for cmd, arg in commands:
        res = await bridge.handle_command(user, cmd, arg)
        print("CMD=", cmd, "ARG=", arg, "=> RESULT=", res)

if __name__ == '__main__':
    asyncio.run(main())
