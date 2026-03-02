#!/usr/bin/env python3
"""TelClaw sim env test runner -- no external deps, no side effects."""

import asyncio
import sys
import os

# Ensure telclaw package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telclaw.policy_engine import PolicyEngine
from telclaw.gate import Gate
from telclaw.executor import Executor
from telclaw.bridge import TelClawBridge
from telclaw.models import CommandRequest, Approval, ExecutionResult

passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}")

# ---- PolicyEngine tests ----
print("\n== PolicyEngine ==")
pe = PolicyEngine(safe_max=3)

# Deterministic: classify returns 0-10 based on hash
r1 = pe.classify("status", "")
check("classify returns int", isinstance(r1, int))
check("classify in range 0-10", 0 <= r1 <= 10)

# Verify safe threshold boundary
for i in range(20):
    cmd = f"cmd{i}"
    risk = pe.classify(cmd, "")
    check(f"classify({cmd}) in [0,10]", 0 <= risk <= 10)

# ---- Gate tests ----
print("\n== Gate ==")
g = Gate()

# Risk 4-5: auto-approve in sim
check("gate approves risk=4", g.request_approval("user1", "restart", "", 4) == True)
check("gate approves risk=5", g.request_approval("user1", "modify", "", 5) == True)

# Risk 6+: blocked
check("gate blocks risk=6", g.request_approval("user1", "rm", "", 6) == False)
check("gate blocks risk=9", g.request_approval("user1", "drop", "", 9) == False)

# ---- Executor tests ----
print("\n== Executor ==")
ex = Executor()
result = ex.execute("status", "", simulated=True)
check("executor returns sim string", "simulated" in result)
check("executor includes command", "status" in result)

# ---- Bridge integration tests ----
print("\n== Bridge (integration) ==")

async def test_bridge():
    pe2 = PolicyEngine(safe_max=3)
    g2 = Gate()
    ex2 = Executor()
    bridge = TelClawBridge(pe2, g2, ex2)

    # Test with a command that hashes to safe (0-3)
    # We'll brute-force find one
    safe_cmd = None
    gated_cmd = None
    blocked_cmd = None
    for i in range(100):
        cmd = f"test{i}"
        risk = pe2.classify(cmd, "")
        if risk <= 3 and safe_cmd is None:
            safe_cmd = cmd
        elif 4 <= risk <= 5 and gated_cmd is None:
            gated_cmd = cmd
        elif risk >= 6 and blocked_cmd is None:
            blocked_cmd = cmd
        if safe_cmd and gated_cmd and blocked_cmd:
            break

    if safe_cmd:
        r = await bridge.handle_command("user1", safe_cmd, "")
        check(f"safe cmd '{safe_cmd}' auto-executes", r["status"] == "executed")
        check(f"safe cmd risk <= 3", r["risk"] <= 3)
    else:
        check("found a safe cmd", False)

    if gated_cmd:
        r = await bridge.handle_command("user1", gated_cmd, "")
        check(f"gated cmd '{gated_cmd}' executes after approval", r["status"] == "executed")
        check(f"gated cmd risk 4-5", 4 <= r["risk"] <= 5)
    else:
        check("found a gated cmd", False)

    if blocked_cmd:
        r = await bridge.handle_command("user1", blocked_cmd, "")
        check(f"blocked cmd '{blocked_cmd}' is blocked", r["status"] == "blocked")
        check(f"blocked cmd risk >= 6", r["risk"] >= 6)
    else:
        check("found a blocked cmd", False)

asyncio.run(test_bridge())

# ---- Models tests ----
print("\n== Models ==")
cr = CommandRequest(id="1", user_id="u1", command="status", args={}, risk=1, status="pending", timestamp="now")
check("CommandRequest fields", cr.command == "status" and cr.risk == 1)

ap = Approval(id="1", command_id="1", approver_id="admin", timestamp="now", decision="Y", rationale="test")
check("Approval fields", ap.decision == "Y")

er = ExecutionResult(command_id="1", success=True, output="ok", error="", timestamp="now")
check("ExecutionResult fields", er.success == True)

# ---- Summary ----
print(f"\n{'='*40}")
print(f"  PASSED: {passed}  |  FAILED: {failed}")
if failed > 0:
    print("  SOME TESTS FAILED")
    sys.exit(1)
else:
    print("  ALL TESTS PASSED")
    sys.exit(0)
