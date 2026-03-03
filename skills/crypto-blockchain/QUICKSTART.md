# Crypto Skill Quick Start

## Installation
```bash
cd ~/.openclaw/workspace/skills/crypto-blockchain
pip install -r requirements.txt
```

## Basic Usage

### 1. Import and Initialize
```python
from crypto_skill import CryptoSkill
skill = CryptoSkill()
```

### 2. Create a Token
```python
result = await skill.create_token("Create ERC-20 token")
print(result)
```

### 3. Create Secure Wallet
```python
result = await skill.create_wallet("Create Ethereum wallet")
print(result)
```

### 4. Audit Contract
```python
result = await skill.audit_contract("Audit this smart contract")
print(result)
```

## Running Examples
```bash
cd examples
python3 create_token.py
python3 secure_wallet.py
```

## Testing
```bash
python3 test_crypto_skill.py
```

## Next Steps
1. Get testnet ETH/SOL from faucets
2. Deploy real contracts on testnet
3. Implement actual blockchain interaction
4. Add security features

## Security Warning
⚠️ **NEVER USE REAL PRIVATE KEYS OR MAINNET IN DEVELOPMENT**
