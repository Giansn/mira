"""
TelClaw PolicyEngine with contextual risk classification.
Replaces naive hash-based risk with intent/impact/credential-exposure weighting.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Config path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config/api_config.json')

def load_config() -> Dict[str, Any]:
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

# Risk weights by operation category
OPERATION_WEIGHTS = {
    # Read-only, safe operations (intent: read)
    "read": 1,
    "status": 1,
    "sts": 1,
    "ping": 1,
    "time": 1,
    "uptime": 1,
    "whoami": 1,
    "help": 1,
    "metrics": 1,
    "get": 1,
    "cat": 1,
    "ls": 1,
    "logs": 1,
    "show": 1,
    
    # Moderate risk (intent: write/config, low impact)
    "config": 4,
    "set": 4,
    "update": 5,
    "edit": 4,
    "modify": 4,
    
    # High risk (intent: write, high impact)
    "restart": 6,
    "start": 5,
    "stop": 6,
    "reset": 7,
    
    # Critical risk (intent: or credential destructive exposure)
    "delete": 8,
    "kill": 9,
    "reboot": 10,
    "shell": 9,
    "exec": 9,
    "drop": 10,
    "truncate": 9,
    "exit": 7,
}

# Credential exposure keywords (increase risk if found in args)
CREDENTIAL_EXPOSURE_KEYWORDS = [
    "token", "password", "secret", "key", "api_key", "apikey",
    "credential", "auth", "bearer", "jwt", "oauth",
    "private", "cert", "pem", "access_token", "refresh_token"
]

# Resource impact keywords (increase risk based on scope)
RESOURCE_IMPACT_KEYWORDS = {
    # High impact scope
    "high": ["*", "all", "global", "system", "root", "admin", "--force", "-f"],
    # Moderate impact scope
    "medium": ["service", "daemon", "container", "pod"],
}

class PolicyEngine:
    def __init__(self, safe_max=3, mock_mode=False, config: Optional[Dict[str, Any]] = None):
        self.safe_max = safe_max
        self.mock_mode = mock_mode
        self.config = config or load_config()
        
        # Speed fine-tuning: cache for safe commands
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = self.config.get("speed_fine_tuning", {}).get("cache_ttl_seconds", 300)
        
        # Short-circuit whitelist
        self._whitelist = set(self.config.get("speed_fine_tuning", {}).get(
            "short_circuit_whitelist", 
            ["status", "sts", "ping", "time", "help", "whoami"]
        ))
        
        # Risk calibration settings
        self._use_contextual = self.config.get("risk_calibration", {}).get("use_contextual_risk", True)
        self._weight_intent = self.config.get("risk_calibration", {}).get("weight_intent", True)
        self._weight_credential = self.config.get("risk_calibration", {}).get("weight_credential_exposure", True)
        self._weight_impact = self.config.get("risk_calibration", {}).get("weight_resource_impact", True)

    def _check_cache(self, command: str, args: str) -> Optional[int]:
        """Check if command result is cached."""
        if command not in self._whitelist:
            return None
        key = f"{command}:{args}"
        if key in self._cache:
            risk, _ = self._cache[key]
            return risk
        return None

    def _update_cache(self, command: str, args: str, risk: int):
        """Cache command risk result."""
        import time
        key = f"{command}:{args}"
        self._cache[key] = (risk, time.time())

    def _classify_contextual(self, command: str, args) -> int:
        """
        Contextual risk classification based on:
        - Operation intent (read/write/delete)
        - Credential exposure potential
        - Resource impact scope
        """
        cmd = command.lower().strip()
        # Handle args as either string or dict
        if isinstance(args, dict):
            args_str = json.dumps(args)
        else:
            args_str = str(args) if args else ""
        args_lower = args_str.lower()
        
        # 1. Base risk from operation intent
        base_risk = OPERATION_WEIGHTS.get(cmd, 5)  # default 5 if unknown
        
        # 2. Credential exposure check
        if self._weight_credential:
            for keyword in CREDENTIAL_EXPOSURE_KEYWORDS:
                if keyword in args_lower:
                    base_risk = min(10, base_risk + 3)
                    break
        
        # 3. Resource impact check
        if self._weight_impact:
            for scope, keywords in RESOURCE_IMPACT_KEYWORDS.items():
                if any(kw in args_lower for kw in keywords):
                    if scope == "high":
                        base_risk = min(10, base_risk + 2)
                    elif scope == "medium":
                        base_risk = min(10, base_risk + 1)
        
        # 4. Whitelist short-circuit (speed optimization)
        if cmd in self._whitelist:
            base_risk = min(base_risk, 1)
        
        return base_risk

    def classify(self, command, args) -> int:
        """Classify command risk with caching and contextual weighting."""
        # Check cache first (speed optimization)
        cached = self._check_cache(command, args)
        if cached is not None:
            return cached
        
        # Use contextual risk if enabled
        if self._use_contextual:
            risk = self._classify_contextual(command, args)
        else:
            # Fallback to naive hash-based (for backwards compatibility)
            key = f"{command}:{args}"
            risk = (sum(ord(c) for c in key) % 11)
        
        # Apply mock_mode risk reduction
        if self.mock_mode and risk > self.safe_max:
            risk = max(0, risk - 3)
        
        # Update cache
        self._update_cache(command, args, risk)
        
        return risk
