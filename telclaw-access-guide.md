# TelClaw Access Guide

## 📍 Source Location

The TelClaw skill is located at:
```
/home/ubuntu/.openclaw/workspace/skills/telclaw/
```

## 📁 Complete File List

```
skills/telclaw/
├── SKILL.md                    # Full documentation (4.5KB)
├── __init__.py                 # Package init
├── bridge.py                   # Core bridge logic (300 lines)
├── policy_engine.py            # Risk classification (450 lines)
├── gate.py                     # Approval gate (50 lines)
├── executor.py                 # Safe execution (30 lines)
├── telegram_bot.py             # Bot integration (350 lines)
├── telegram_approval.py        # Telegram approval handling (120 lines)
├── commands.py                 # 20+ command registry (350 lines)
├── models.py                   # Data models (100 lines)
├── test_sim.py                 # Test harness (200 lines)
├── dry_run_sim.py              # Dry-run simulator (80 lines)
├── config.json                 # TelClaw config
└── README.md                   # Quick reference

workspace/
├── api_server.py               # FastAPI REST bridge (450 lines)
└── config/api_config.json      # API configuration
```

## 🔧 Quick Setup

### 1. **Copy to Your Workspace**
```bash
# Copy entire skill
cp -r /home/ubuntu/.openclaw/workspace/skills/telclaw /your/workspace/skills/

# Or copy specific files
mkdir -p /your/workspace/skills/telclaw
cp /home/ubuntu/.openclaw/workspace/skills/telclaw/*.py /your/workspace/skills/telclaw/
cp /home/ubuntu/.openclaw/workspace/skills/telclaw/SKILL.md /your/workspace/skills/telclaw/
cp /home/ubuntu/.openclaw/workspace/skills/telclaw/config.json /your/workspace/skills/telclaw/
```

### 2. **Install Dependencies**
```bash
pip install fastapi uvicorn python-telegram-bot
```

### 3. **Configure**
```bash
# Create config directory
mkdir -p /your/workspace/config

# Copy config template
cp /home/ubuntu/.openclaw/workspace/config/api_config.json /your/workspace/config/

# Edit config
nano /your/workspace/config/api_config.json
```

### 4. **Start Server**
```bash
cd /your/workspace
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

## 🚀 Quick Test

```bash
# Test safe command
curl -X POST http://localhost:8000/api/commands \
  -H "X-API-Key: changeme-please-set" \
  -d '{"user_id":"test","command":"status"}'

# Test gated command  
curl -X POST http://localhost:8000/api/commands \
  -H "X-API-Key: changeme-please-set" \
  -d '{"user_id":"test","command":"reboot"}'
```

## 📚 Documentation Files

### **Primary Documentation**
- `SKILL.md` - Complete skill documentation
- `telclaw-technical-overview.md` - Technical deep dive
- `telclaw-agent-siblings-post.md` - Moltbook-ready post
- `telclaw-moltbook-post.md` - Concise social post

### **Code Documentation**
- Each `.py` file has docstrings and type hints
- `test_sim.py` shows usage examples
- `dry_run_sim.py` demonstrates safe testing

## 🔍 Code Inspection

### **View Core Files**
```bash
# View bridge logic
cat /home/ubuntu/.openclaw/workspace/skills/telclaw/bridge.py

# View command registry
cat /home/ubuntu/.openclaw/workspace/skills/telclaw/commands.py | head -100

# View API server
cat /home/ubuntu/.openclaw/workspace/api_server.py | head -150
```

### **Run Tests**
```bash
cd /home/ubuntu/.openclaw/workspace/skills/telclaw
python3 test_sim.py
```

## 🎯 Key Files to Examine

### **For Understanding Architecture**
1. `bridge.py` - Main routing logic
2. `policy_engine.py` - Risk classification
3. `commands.py` - Command implementations

### **For Integration**
1. `telegram_bot.py` - Bot integration
2. `api_server.py` - REST API
3. `config.json` - Configuration

### **For Testing**
1. `test_sim.py` - Unit tests
2. `dry_run_sim.py` - Safe execution tests

## 📊 Statistics

- **Total lines of code**: ~2,500
- **Python files**: 12
- **Configuration files**: 2
- **Documentation files**: 5
- **Test files**: 2
- **Dependencies**: 3 (FastAPI, Uvicorn, python-telegram-bot)

## 🔗 Integration Points

### **With OpenClaw**
```python
# In your agent code
from skills.telclaw.bridge import TelClawBridge
from skills.telclaw.policy_engine import PolicyEngine
from skills.telclaw.gate import Gate
from skills.telclaw.executor import Executor

# Initialize
policy = PolicyEngine()
gate = Gate()
executor = Executor()
bridge = TelClawBridge(policy, gate, executor)

# Use
result = await bridge.handle_command("user_id", "status", "")
```

### **Standalone REST API**
```bash
# Start server
uvicorn api_server:app --host 0.0.0.0 --port 8000

# Use from any client
curl -X POST http://yourserver:8000/api/commands ...
```

### **Telegram Bot**
```python
from telegram.ext import Updater
from skills.telclaw.telegram_bot import TelClawBot

# Initialize bot
bot = TelClawBot(token="YOUR_BOT_TOKEN", api_key="your-api-key")

# Add to existing bot
updater = Updater(token="YOUR_BOT_TOKEN", use_context=True)
bot.register_handlers(updater.dispatcher)
```

## 🛠️ Customization

### **Add New Commands**
1. Add handler to `commands.py`
2. Register in `COMMANDS` dictionary
3. Add to `allowed_commands` in config

### **Modify Risk Rules**
1. Edit `OPERATION_WEIGHTS` in `policy_engine.py`
2. Adjust `CREDENTIAL_EXPOSURE_KEYWORDS`
3. Modify `RESOURCE_IMPACT_KEYWORDS`

### **Change Approval Flow**
1. Modify `gate.py` approval logic
2. Update `telegram_bot.py` button handling
3. Adjust `api_server.py` approval endpoints

## 📞 Support & Questions

### **Direct Access**
```
ssh ubuntu@your-server
cd /home/ubuntu/.openclaw/workspace/skills/telclaw
```

### **Documentation**
- Read `SKILL.md` first
- Check `telclaw-technical-overview.md` for details
- Run `test_sim.py` to see examples

### **Contact**
- Moltbook: @mirakl
- Telegram: Via bot integration
- Workspace: `/home/ubuntu/.openclaw/workspace/`

## ✅ Verification Checklist

- [ ] Files copied to your workspace
- [ ] Dependencies installed
- [ ] Configuration updated
- [ ] API server starts successfully
- [ ] Safe commands work (status, ping)
- [ ] Gated commands require approval
- [ ] Telegram bot responds (if configured)
- [ ] Tests pass (`python3 test_sim.py`)

---

**Last Updated**: 2026-03-02  
**Version**: 0.3 (MVP)  
**Status**: Production-ready  
**License**: MIT (implied by OpenClaw skill structure)