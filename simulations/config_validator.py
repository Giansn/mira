#!/usr/bin/env python3
"""
Config Sim Tool - Enhanced Config Validator with Simulation Principles
Based on formal simulation theory (DEVS, sensitivity analysis, pattern validation)

Before any config change: run this to simulate and validate.
"""

import json
import subprocess
import sys
import random
import copy
from pathlib import Path
from datetime import datetime

CONFIG_PATH = "/home/ubuntu/.openclaw/openclaw.json"
BACKUP_PATH = "/home/ubuntu/.openclaw/openclaw.json.bak"

# Known patterns that have caused issues (from historical data)
DANGEROUS_PATTERNS = {
    "gateway.bind": {
        "0.0.0.0": "WARNING: Exposes gateway to all interfaces - security risk",
    },
    "gateway.mode": {
        "remote": "WARNING: Remote mode may cause connection issues",
    },
    "channels": {
        "add_webchat": "Adding webchat has caused gateway crashes - verify first",
    }
}

# Sensitivity analysis: fields that affect gateway stability
SENSITIVE_FIELDS = [
    "gateway.bind",
    "gateway.port",
    "gateway.mode",
    "channels",
    "models.providers",
    "agents.defaults.model.primary",
]

# Known valid value ranges
VALID_RANGES = {
    "gateway.port": (1, 65535),
    "gateway.mode": ["local", "remote"],
    "gateway.auth.mode": ["token", "password", "none"],
    "gateway.bind": ["127.0.0.1", "0.0.0.0", "loopback", "lan", "tailnet"],
}


class ConfigSimulator:
    """DEVS-style state machine for gateway config states."""
    
    STATES = ["valid", "invalid", "uncertain", "dangerous"]
    
    def __init__(self):
        self.state = "valid"
        self.state_history = []
        self.issues = []
        self.warnings = []
        self.risk_score = 0.0
    
    def transition(self, new_state, reason):
        """State transition with logging."""
        self.state_history.append({
            "from": self.state,
            "to": new_state,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        self.state = new_state
    
    def add_issue(self, issue, severity=1.0):
        """Add issue with severity (0-1)."""
        self.issues.append(issue)
        self.risk_score += severity
    
    def add_warning(self, warning):
        """Add warning without severity impact."""
        self.warnings.append(warning)


def load_config(path=CONFIG_PATH):
    """Load and parse config file."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {e}"}


def backup_config(config):
    """Create backup before any changes."""
    try:
        with open(BACKUP_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        return False


def validate_syntax(config):
    """Check JSON syntax (formal verification)."""
    if config is None:
        return False, "File not found"
    if "error" in config:
        return False, config["error"]
    return True, "Valid JSON"


def validate_structure(simulator, config):
    """Check required fields exist (structural validation)."""
    required = {
        "gateway": ["port", "mode", "auth"],
        "channels": None,  # Just check existence
        "models": ["mode", "providers"],
        "agents": ["defaults"],
    }
    
    for section, fields in required.items():
        if section not in config:
            simulator.add_issue(f"Missing '{section}' section", 1.0)
        elif fields:
            for field in fields:
                if field not in config[section]:
                    simulator.add_issue(f"Missing '{section}.{field}'", 0.8)
    
    return len(simulator.issues) == 0


def validate_values(simulator, config):
    """Validate values against known ranges (range validation)."""
    # Port validation
    gw = config.get("gateway", {})
    port = gw.get("port")
    if port:
        if not isinstance(port, int) or not (1 <= port <= 65535):
            simulator.add_issue(f"Invalid port: {port} (must be 1-65535)", 1.0)
    
    # Mode validation
    mode = gw.get("mode")
    if mode and mode not in VALID_RANGES["gateway.mode"]:
        simulator.add_issue(f"Invalid gateway mode: {mode}", 0.7)
    
    # Auth mode validation
    auth = gw.get("auth", {}).get("mode")
    if auth and auth not in VALID_RANGES["gateway.auth.mode"]:
        simulator.add_issue(f"Invalid auth mode: {auth}", 0.5)
    
    # Bind validation
    bind = gw.get("bind")
    if bind and bind not in VALID_RANGES["gateway.bind"]:
        simulator.add_issue(f"Unknown bind value: {bind} (may cause issues)", 0.6)
    
    return len(simulator.issues) == 0


def check_dangerous_patterns(simulator, config):
    """Pattern-oriented validation - detect known dangerous patterns."""
    gw = config.get("gateway", {})
    
    # Check gateway.bind
    bind = gw.get("bind")
    if bind in DANGEROUS_PATTERNS.get("gateway.bind", {}):
        simulator.add_warning(DANGEROUS_PATTERNS["gateway.bind"][bind])
        simulator.risk_score += 0.3
    
    # Check for webchat channel addition
    channels = config.get("channels", {})
    if "webchat" in channels:
        simulator.add_warning(DANGEROUS_PATTERNS["channels"]["add_webchat"])
        simulator.risk_score += 0.5
    
    # Check for token in auth
    auth = gw.get("auth", {})
    if auth.get("mode") == "token" and not auth.get("token"):
        simulator.add_issue("Auth mode is 'token' but no token provided", 0.9)


def sensitivity_analysis(config, field_path):
    """Sensitivity analysis - test how changes to a field affect the system."""
    # Get current value
    parts = field_path.split(".")
    current = config
    for p in parts:
        current = current.get(p, {})
    
    # Generate test variations
    test_values = []
    
    if field_path == "gateway.port":
        # Test common ports
        test_values = [80, 443, 8080, 18789, 3000, 8000]
    elif field_path == "gateway.bind":
        test_values = ["127.0.0.1", "0.0.0.0", "loopback", "lan"]
    elif field_path == "gateway.mode":
        test_values = ["local", "remote"]
    
    results = []
    for test_val in test_values:
        test_config = copy.deepcopy(config)
        
        # Apply test value
        parts = field_path.split(".")
        obj = test_config
        for p in parts[:-1]:
            obj = obj.setdefault(p, {})
        obj[parts[-1]] = test_val
        
        # Validate
        test_sim = ConfigSimulator()
        validate_structure(test_sim, test_config)
        validate_values(test_sim, test_config)
        
        results.append({
            "value": test_val,
            "issues": len(test_sim.issues),
            "risk": test_sim.risk_score
        })
    
    return results


def monte_carlo_validation(config, n_iterations=10):
    """Monte Carlo-style validation - test random valid configurations."""
    results = []
    
    for _ in range(n_iterations):
        test_config = copy.deepcopy(config)
        
        # Randomly modify sensitive fields
        field = random.choice(SENSITIVE_FIELDS)
        
        if field == "gateway.port":
            test_config.setdefault("gateway", {}).setdefault("port", 18789)
            test_config["gateway"]["port"] = random.randint(1024, 65535)
        elif field == "gateway.bind":
            test_config.setdefault("gateway", {}).setdefault("bind", "loopback")
            test_config["gateway"]["bind"] = random.choice(["127.0.0.1", "0.0.0.0", "loopback"])
        
        # Validate
        test_sim = ConfigSimulator()
        validate_structure(test_sim, test_config)
        validate_values(test_sim, test_config)
        
        results.append({
            "field": field,
            "issues": len(test_sim.issues),
            "risk": test_sim.risk_score
        })
    
    return results


def check_gateway_health():
    """Check if gateway is currently running."""
    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ":18789" in result.stdout:
            # Extract bind address
            for line in result.stdout.split("\n"):
                if "18789" in line:
                    if "127.0.0.1:18789" in line:
                        return True, "Gateway running on localhost (127.0.0.1)"
                    elif "0.0.0.0:18789" in line:
                        return True, "Gateway running on all interfaces (0.0.0.0)"
                    else:
                        return True, f"Gateway running: {line.strip()}"
        return False, "Gateway not running on port 18789"
    except Exception as e:
        return None, f"Could not check: {e}"


def test_gateway_restart():
    """Test if gateway CLI is available."""
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "start", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, "Gateway CLI available"
    except Exception as e:
        return False, f"Gateway CLI error: {e}"


def simulate_change(old_config, new_config):
    """Compare old and new config, predict issues."""
    changes = []
    warnings = []
    
    # Gateway bind change
    old_bind = old_config.get("gateway", {}).get("bind", "loopback")
    new_bind = new_config.get("gateway", {}).get("bind", "loopback")
    if old_bind != new_bind:
        changes.append(f"gateway.bind: {old_bind} → {new_bind}")
        if new_bind == "0.0.0.0":
            warnings.append("⚠️  SECURITY: Gateway will be exposed to all interfaces")
        elif new_bind == "127.0.0.1":
            warnings.append("ℹ️  Gateway will be local-only")
    
    # Channel changes
    old_channels = set(old_config.get("channels", {}).keys())
    new_channels = set(new_config.get("channels", {}).keys())
    for ch in new_channels - old_channels:
        changes.append(f"+channel: {ch}")
        if ch == "webchat":
            warnings.append("⚠️  WARNING: Adding webchat has caused gateway crashes in past")
    for ch in old_channels - new_channels:
        changes.append(f"-channel: {ch}")
    
    # Model changes
    old_model = old_config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
    new_model = new_config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
    if old_model != new_model:
        changes.append(f"model: {old_model} → {new_model}")
    
    return changes, warnings


def run_validation(simulator=None, show_sensitivity=False):
    """Run full validation with simulation principles."""
    if simulator is None:
        simulator = ConfigSimulator()
    
    print("=" * 60)
    print("CONFIG SIM TOOL - OpenClaw")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Load config
    print("\n📂 [1] Loading config...")
    config = load_config()
    valid, msg = validate_syntax(config)
    print(f"    Syntax: {'✓' if valid else '✗'} {msg}")
    if not valid:
        print(f"    ERROR: Cannot proceed without valid config")
        return False, simulator
    
    # Backup current config
    print("\n💾 [2] Creating backup...")
    if backup_config(config):
        print(f"    ✓ Backup saved to {BACKUP_PATH}")
    else:
        print(f"    ✗ Backup failed")
    
    # Structural validation
    print("\n🏗️  [3] Structural validation...")
    validate_structure(simulator, config)
    if simulator.issues:
        for issue in simulator.issues:
            print(f"    ✗ {issue}")
    else:
        print(f"    ✓ All required fields present")
    
    # Value validation
    print("\n🔢 [4] Value validation...")
    validate_values(simulator, config)
    if simulator.issues:
        for issue in simulator.issues:
            print(f"    ✗ {issue}")
    else:
        print(f"    ✓ Values within valid ranges")
    
    # Pattern validation
    print("\n🔍 [5] Pattern validation...")
    check_dangerous_patterns(simulator, config)
    if simulator.warnings:
        for warning in simulator.warnings:
            print(f"    ⚠️  {warning}")
    else:
        print(f"    ✓ No dangerous patterns detected")
    
    # Gateway health
    print("\n🌐 [6] Gateway health check...")
    running, msg = check_gateway_health()
    print(f"    {'✓' if running else '✗'} {msg}")
    
    # CLI test
    print("\n⚡ [7] Gateway CLI test...")
    available, msg = test_gateway_restart()
    print(f"    {'✓' if available else '✗'} {msg}")
    
    # Sensitivity analysis (optional)
    if show_sensitivity:
        print("\n📊 [8] Sensitivity Analysis...")
        for field in SENSITIVE_FIELDS[:3]:  # Limit to 3 fields
            results = sensitivity_analysis(config, field)
            if results:
                print(f"    {field}:")
                for r in results[:3]:
                    status = "✓" if r["issues"] == 0 else "✗"
                    print(f"      {status} {r['value']} → {r['issues']} issues, risk: {r['risk']:.2f}")
    
    # Risk assessment
    print("\n" + "=" * 60)
    print(f"RISK SCORE: {simulator.risk_score:.2f} / 3.0")
    
    if simulator.risk_score > 2.0:
        print("🔴 HIGH RISK - Do not apply without manual testing")
    elif simulator.risk_score > 1.0:
        print("🟡 MEDIUM RISK - Proceed with caution")
    else:
        print("🟢 LOW RISK - Config appears safe")
    
    if simulator.warnings:
        print("\nWARNINGS:")
        for w in simulator.warnings:
            print(f"  • {w}")
    
    print("=" * 60)
    
    return simulator.risk_score < 2.0, simulator


def simulate_change_interactive():
    """Interactive change simulation."""
    print("\n" + "=" * 60)
    print("CHANGE SIMULATOR")
    print("=" * 60)
    
    # Load current and backup
    current = load_config()
    backup = load_config(BACKUP_PATH)
    
    if backup is None:
        print("✗ No backup found - cannot simulate changes")
        return
    
    changes, warnings = simulate_change(backup, current)
    
    if changes:
        print("\nDetected changes:")
        for c in changes:
            print(f"  • {c}")
    else:
        print("\nNo changes detected")
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    return changes, warnings


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Config Sim Tool")
    parser.add_argument("--sensitivity", action="store_true", help="Run sensitivity analysis")
    parser.add_argument("--simulate-change", action="store_true", help="Simulate last change")
    args = parser.parse_args()
    
    if args.simulate_change:
        simulate_change_interactive()
    else:
        run_validation(show_sensitivity=args.sensitivity)
