#!/usr/bin/env python3
import sys
# Add the parent directory of telclaw to sys.path
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/skills') 
# Now the import should work
import asyncio
import json
from pathlib import Path

from telclaw.policy_engine import PolicyEngine
from telclaw.gate import Gate
from telclaw.executor import Executor
from telclaw.bridge import TelClawBridge

SIM_ENV_PATH = Path('/home/ubuntu/.openclaw/workspace/sim_env.json')

async def main():
    pe = PolicyEngine(safe_max=3, mock_mode=True)
    g = Gate()
    ex = Executor()
    bridge = TelClawBridge(pe, g, ex)

    user = "dryrun-user"

    # Load sim env commands if present
    if SIM_ENV_PATH.exists():
        with SIM_ENV_PATH.open('r') as f:
            try:
                env_cmds = json.load(f)
            except Exception:
                env_cmds = []
    else:
        env_cmds = []

    commands = [(c.get('command',''), c.get('args','')) for c in env_cmds] or [
        ("status", ""),
        ("restart", ""),
    ]

    for cmd, arg in commands:
        res = await bridge.handle_command(user, cmd, arg)
        print("CMD=", cmd, "ARG=", arg, "=> RESULT=", res)

if __name__ == '__main__':
    asyncio.run(main())
