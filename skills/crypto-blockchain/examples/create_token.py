#!/usr/bin/env python3
"""
Example 1: Create an ERC-20 Token
"""

import asyncio
import sys
sys.path.insert(0, '..')

from crypto_skill import CryptoSkill


async def main():
    print(""Creating ERC-20 Token Example")
    print(""="*50)
    
    skill = CryptoSkill()
    
    # Create token
    result = await skill.create_token("Create ERC-20 token called MyToken with symbol MTK")
    
    print("f"Result: {result}")
    
    # Next steps
    print(""\nNext steps for real implementation:")
    print(""1. Install web3.py: pip install web3")
    print(""2. Get testnet ETH from faucet")
    print(""3. Write Solidity contract")
    print(""4. Compile and deploy")
    print(""5. Verify on Etherscan")


if __name__ == "__main__":
    asyncio.run(main())