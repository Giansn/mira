# TelClaw Technical Overview

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TelClaw Bridge                           │
├───────────────┬───────────────┬─────────────────────────────┤
│ PolicyEngine  │     Gate      │        Executor             │
│ • Risk 0-10   │ • Y/N approval│ • Sandboxed execution      │
│ • Contextual  │ • Inline      │ • Mock mode                │
│ • Cached      │   buttons     │ • Real/simulated           │
└───────────────┴───────────────┴─────────────────────────────┘
         │               │                       │
         ▼               ▼                       ▼
┌───────────────┬───────────────┬─────────────────────────────┐
│  Telegram Bot │   FastAPI     │    Command Registry         │
│ • Inline Y/N  │ • REST API    │ • 20+ async handlers       │
│ • Chat ID     │ • API key auth│ • Risk overrides           │
│   whitelist   │ • JSON I/O    │ • Descriptions             │
└───────────────┴───────────────┴─────────────────────────────┘
```

## Core Code Examples

### 1. **Bridge Routing Logic** (`bridge.py`)
```python
class TelClawBridge:
    async def handle_command(self, user, command, args):
        risk = self.policy_engine.classify(command, args)
        if risk <= 3:  # Safe: auto-execute
            result = self.executor.execute(command, args, simulated=True)
            return {"status": "executed", "risk": risk, "result": result}
        else:  # Gate required
            options = ["Y", "N"]
            decision = self.gate.request_approval(user, command, args, risk, options)
            if decision and decision != "N":
                result = self.executor.execute(command, args, simulated=True)
                return {"status": "executed", "risk": risk, "decision": decision, "result": result}
            return {"status": "blocked", "risk": risk, "decision": decision}
```

### 2. **Risk Classification** (`policy_engine.py`)
```python
class PolicyEngine:
    def classify(self, command, args) -> int:
        # 1. Check cache first
        cached = self._check_cache(command, args)
        if cached is not None:
            return cached
        
        # 2. Contextual risk assessment
        risk = self._classify_contextual(command, args)
        
        # 3. Apply mock_mode risk reduction
        if self.mock_mode and risk > self.safe_max:
            risk = max(0, risk - 3)
        
        # 4. Update cache
        self._update_cache(command, args, risk)
        return risk
    
    def _classify_contextual(self, command: str, args) -> int:
        cmd = command.lower().strip()
        base_risk = OPERATION_WEIGHTS.get(cmd, 5)
        
        # Credential exposure check
        if self._weight_credential:
            for keyword in CREDENTIAL_EXPOSURE_KEYWORDS:
                if keyword in str(args).lower():
                    base_risk = min(10, base_risk + 3)
                    break
        
        # Resource impact check
        if self._weight_impact:
            for scope, keywords in RESOURCE_IMPACT_KEYWORDS.items():
                if any(kw in str(args).lower() for kw in keywords):
                    if scope == "high":
                        base_risk = min(10, base_risk + 2)
                    elif scope == "medium":
                        base_risk = min(10, base_risk + 1)
        
        return base_risk
```

### 3. **Command Registry** (`commands.py`)
```python
# Async command handlers
async def cmd_status(user_id, args):
    return "TelClaw online | mock_mode: active | bridge: healthy"

async def cmd_restart(user_id, args):
    target = args.strip() if args else "telclaw"
    return f"[SIM] Restart issued for: {target}"

async def cmd_shell(user_id, args):
    cmd = args.strip() if args else "(empty)"
    return f"[SIM] Shell exec: {cmd}"

# Command manifest with risk overrides
COMMANDS = {
    "status":   (cmd_status,   "System status", 0),
    "restart":  (cmd_restart,  "Restart service", 6),
    "shell":    (cmd_shell,    "Execute shell", 9),
    "reboot":   (cmd_reboot,   "Reboot system", 10),
}
```

### 4. **FastAPI Endpoints** (`api_server.py`)
```python
@app.post("/api/commands")
async def create_command(cmd: CommandIn, x_api_key: str = Header(...)):
    require_key(x_api_key)  # API key validation
    require_allowed(cmd.command)  # Command whitelist
    
    # Risk classification
    computed_risk = policy.classify(cmd.command, cmd.args)
    if cmd.command in GATED_COMMANDS:
        computed_risk = GATED_COMMANDS[cmd.command]
    
    # AEAP mode handling
    requires_approval = AEAP
    risk = computed_risk
    if requires_approval:
        risk = max(risk, SAFE_MAX + 1)
    elif OFFLINE_FREE_PASS:
        risk = 0
    
    # Route based on risk
    if risk <= SAFE_MAX:
        result = executor.execute(cmd.command, cmd.args, simulated=True)
        return {"status": "executed", "risk": risk, "result": result}
    else:
        # Store pending approval
        command_id = str(uuid.uuid4())
        commands_store[command_id] = {
            "user_id": cmd.user_id,
            "command": cmd.command,
            "args": cmd.args,
            "risk": risk,
            "status": "pending"
        }
        return {"status": "pending_approval", "command_id": command_id, "risk": risk}
```

### 5. **Telegram Bot Integration** (`telegram_bot.py`)
```python
class TelClawBot:
    def handle_command(self, update, context):
        user_id = update.effective_user.id
        command = update.message.text.lstrip('/')
        
        if not self._is_allowed(user_id):
            update.message.reply_text("Access denied.")
            return
        
        # Get command handler
        cmd_info = self.registry.get(command)
        if not cmd_info:
            update.message.reply_text(f"Unknown command: {command}")
            return
        
        # Check risk
        risk = cmd_info["risk_override"] or self.policy_engine.classify(command, "")
        
        if risk <= 3:  # Safe: auto-execute
            result = await cmd_info["handler"](user_id, "")
            update.message.reply_text(result)
        else:  # Requires approval
            # Create inline keyboard with Y/N buttons
            keyboard = [[
                InlineKeyboardButton("✅ Approve", callback_data=f"approve:{command_id}"),
                InlineKeyboardButton("❌ Deny", callback_data=f"deny:{command_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f"⚠️ Risk {risk} command: {command}\nApprove?",
                reply_markup=reply_markup
            )
```

## Configuration Structure

### **API Config** (`config/api_config.json`)
```json
{
  "api_key": "changeme-please-set",
  "mock_mode": true,
  "offline_load": true,
  "aeap": false,
  "metrics_enabled": false,
  "speed_fine_tuning": {
    "cache_enabled": true,
    "cache_ttl_seconds": 300,
    "batch_safe_commands": true,
    "batch_window_ms": 100,
    "short_circuit_whitelist": ["status", "ping", "time"],
    "max_reasoning_depth": 2
  },
  "risk_calibration": {
    "use_contextual_risk": true,
    "weight_intent": true,
    "weight_credential_exposure": true,
    "weight_resource_impact": true
  },
  "allowed_commands": ["status", "restart", "reboot", "shell"],
  "thresholds": { "safe_max": 3 },
  "gated_commands": {
    "restart": 6,
    "reboot": 10,
    "shell": 9
  }
}
```

### **TelClaw Config** (`skills/telclaw/config.json`)
```json
{
  "approvers": ["admin"],
  "risk_threshold_moderate": 4,
  "risk_threshold_high": 6,
  "mock_mode": true
}
```

## Data Models

### **Command Request** (`models.py`)
```python
class CommandRequest:
    user_id: str
    command: str
    args: Dict[str, Any] = {}
    source: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)
```

### **Approval** (`models.py`)
```python
class Approval:
    command_id: str
    approver_id: str
    decision: str  # "Y", "N"
    rationale: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)
```

### **Execution Result** (`models.py`)
```python
class ExecutionResult:
    command_id: str
    status: str  # "executed", "blocked", "error"
    output: str
    risk: int
    execution_time_ms: float
    timestamp: datetime = datetime.now(timezone.utc)
```

## Performance Optimizations

### **Caching Strategy**
```python
def _check_cache(self, command: str, args: str) -> Optional[int]:
    if command not in self._whitelist:
        return None
    key = f"{command}:{args}"
    if key in self._cache:
        risk, cached_time = self._cache[key]
        if time.time() - cached_time < self._cache_ttl:
            return risk
    return None
```

### **Batch Processing**
```python
def batch_execute_safe_commands(self, commands: List[Tuple[str, str]]):
    """Batch execute multiple safe commands for performance."""
    if not self.config.get("speed_fine_tuning", {}).get("batch_safe_commands", True):
        return [self.execute(cmd, args) for cmd, args in commands]
    
    # Group by command type for optimization
    grouped = {}
    for cmd, args in commands:
        if cmd not in grouped:
            grouped[cmd] = []
        grouped[cmd].append(args)
    
    results = []
    for cmd, args_list in grouped.items():
        # Execute in batch if supported
        batch_result = self._execute_batch(cmd, args_list)
        results.extend(batch_result)
    
    return results
```

## Testing Framework

### **Unit Tests** (`test_sim.py`)
```python
def test_policy_engine():
    pe = PolicyEngine(safe_max=3)
    
    # Test risk classification
    risk = pe.classify("status", "")
    assert 0 <= risk <= 10
    
    # Test caching
    risk1 = pe.classify("test", "args")
    risk2 = pe.classify("test", "args")
    assert risk1 == risk2  # Should be cached
    
    # Test mock mode risk reduction
    pe_mock = PolicyEngine(safe_max=3, mock_mode=True)
    risk_normal = pe.classify("restart", "")
    risk_mock = pe_mock.classify("restart", "")
    assert risk_mock <= max(0, risk_normal - 3)
```

### **Integration Tests**
```python
async def test_bridge_integration():
    pe = PolicyEngine(safe_max=3)
    gate = Gate()
    executor = Executor()
    bridge = TelClawBridge(pe, gate, executor)
    
    # Test safe command
    result = await bridge.handle_command("user1", "status", "")
    assert result["status"] == "executed"
    assert result["risk"] <= 3
    
    # Test gated command
    result = await bridge.handle_command("user1", "restart", "service=test")
    assert result["status"] in ["executed", "blocked"]
    assert result["risk"] >= 4
```

## Security Considerations

### **API Key Validation**
```python
def require_key(x_api_key: Optional[str]) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

### **Command Whitelisting**
```python
def require_allowed(cmd: str) -> None:
    allowed = cfg.get("allowed_commands", [])
    if allowed and cmd not in allowed:
        raise HTTPException(status_code=403, detail=f"Command not allowed: {cmd}")
```

### **User Identity Tracking**
```python
class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.commands_executed: List[str] = []
        self.risk_scores: List[int] = []
        self.last_active: datetime = datetime.now(timezone.utc)
    
    def record_command(self, command: str, risk: int):
        self.commands_executed.append(command)
        self.risk_scores.append(risk)
        self.last_active = datetime.now(timezone.utc)
```

## Deployment Notes

### **Environment Variables**
```bash
export TELCLAW_API_KEY="your-secret-key"
export TELCLAW_MOCK_MODE="true"
export TELCLAW_ALLOWED_COMMANDS="status,restart,reboot"
```

### **Docker Configuration**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY skills/telclaw ./skills/telclaw
COPY api_server.py .
COPY config/ ./config/

ENV TELCLAW_API_KEY=${API_KEY}
ENV TELCLAW_MOCK_MODE=true

EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring & Metrics

### **Prometheus Metrics** (Optional)
```python
if METRICS_ON:
    from prometheus_client import Counter, Histogram
    
    commands_executed = Counter('telclaw_commands_total', 'Total commands executed', ['command', 'risk'])
    approval_decisions = Counter('telclaw_approvals_total', 'Approval decisions', ['decision'])
    execution_time = Histogram('telclaw_execution_seconds', 'Command execution time')
```

### **Health Checks**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "policy_engine": "ok",
            "gate": "ok", 
            "executor": "ok",
            "command_count": len(COMMANDS)
        }
    }
```

## Extension Points

### **Adding New Commands**
```python
# 1. Define handler
async def cmd_custom(user_id, args):
    return f"Custom command executed with args: {args}"

# 2. Register in COMMANDS dict
COMMANDS["custom"] = (cmd_custom, "Custom command description", 3)

# 3. Add to allowed_commands in config
# config/api_config.json: "allowed_commands": ["status", "custom", ...]
```

### **Custom Risk Classifiers**
```python
class CustomPolicyEngine(PolicyEngine):
    def _classify_contextual(self, command: str, args) -> int:
        # Call parent implementation
        base_risk = super()._classify_contextual(command, args)
        
        # Add custom logic
        if "dangerous_pattern" in str(args):
            base_risk = min(10, base_risk + 2)
        
        return base_risk
```

## Troubleshooting

### **Common Issues**
1. **API key rejected**: Check `config/api_config.json` API key matches
2. **Command not allowed**: Add command to `allowed_commands` in config
3. **Mock mode too restrictive**: Set `mock_mode: false` for real execution
4. **Telegram bot not responding**: Verify bot token and webhook URL

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set in config
{
  "debug": true,
  "log_level": "DEBUG"
}
```

---

**Source**: `/home/ubuntu/.openclaw/workspace/skills/telclaw/`  
**Documentation**: `skills/telclaw/SKILL.md`  
**API Reference**: `api_server.py`  
**License**: MIT (implied by OpenClaw skill structure)