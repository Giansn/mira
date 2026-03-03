#!/usr/bin/env python3
"""
Test Crypto Skill
"""

import asyncio
import sys
sys.path.insert(0, '.')

from crypto_skill import CryptoSkill


async def test_basic():
    """Test basic functionality."""
    skill = CryptoSkill()
    
    tests = [
        ("create token", "create_token"),
        ("create wallet", "create_wallet"),
        ("audit contract", "audit_contract"),
        ("analyze transaction", "analyze_transaction")
    ]
    
    print("Testing Crypto Skill")
    print("="*50)
    
    for request, expected_action in tests:
        result = await skill.handle_request(request)
        if result.get("action") == expected_action:
            print("f"✅ {request}: PASS")
        else:
            print("f"❌ {request}: FAIL - {result}")


async def main():
    await test_basic()
    print("\n✅ All tests completed")


if __name__ == "__main__":
    asyncio.run(main())
