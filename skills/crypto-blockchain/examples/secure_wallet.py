#!/usr/bin/env python3
"""
Example 2: Create Secure Wallet
"""

import asyncio
import sys
sys.path.insert(0, '..')

from crypto_skill import CryptoSkill


async def main():
    print(""Creating Secure Wallet Example")
    print(""="*50)
    
    skill = CryptoSkill()
    
    # Create wallet
    result = await skill.create_wallet("Create secure Ethereum wallet")
    
    print("f"Result: {result}")
    
    # Security notes
    print(""\n🔒 Security Best Practices:")
    print(""1. Use hardware wallets for large amounts")
    print(""2. Never share private keys")
    print(""3. Use multi-signature for important wallets")
    print(""4. Regular security audits")
    print(""5. Keep software updated")


if __name__ == "__main__":
    asyncio.run(main())