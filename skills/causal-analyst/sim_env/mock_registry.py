#!/usr/bin/env python3
"""Mock Registry — cached, deterministic mock responses for any API-like call.
Wider-scale mock layer to reduce API costs across all sim_env components."""
import json
import hashlib
import os
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'mock_cache')

def _ensure_cache():
    os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_key(call_type, params):
    raw = json.dumps({"type": call_type, "params": params}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def _cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")

def get_cached(call_type, params):
    """Return cached response if available."""
    _ensure_cache()
    path = _cache_path(_cache_key(call_type, params))
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def set_cached(call_type, params, response):
    """Cache a response for future reuse."""
    _ensure_cache()
    path = _cache_path(_cache_key(call_type, params))
    with open(path, 'w') as f:
        json.dump(response, f, sort_keys=True)

def mock_call(call_type, params, generator_fn=None):
    """Universal mock dispatcher.
    1. Check cache first (zero cost).
    2. If miss, use generator_fn to produce response (or default mock).
    3. Cache result for next time.
    
    call_type: string label (e.g., 'mirror', 'policy', 'llm', 'health')
    params: dict of call parameters
    generator_fn: optional callable(params) -> response dict
    """
    cached = get_cached(call_type, params)
    if cached is not None:
        cached["_mock_meta"] = {"source": "cache", "call_type": call_type}
        return cached

    # Generate
    if generator_fn:
        response = generator_fn(params)
    else:
        h = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]
        response = {
            "result": f"mock_{call_type}_{h}",
            "status": "ok",
            "latency_ms": 50
        }
    
    response["_mock_meta"] = {"source": "generated", "call_type": call_type}
    set_cached(call_type, params, response)
    return response


# --- Pre-built generators for common call types ---

def mirror_generator(params):
    """Generate a deterministic mirror trace from params."""
    tier = params.get("tier", "SAFE")
    command = params.get("command", "unknown")
    if tier == "SAFE":
        return {"reasoning": f"SAFE command '{command}'. No risk.", "risk_flags": [], "confidence": 0.95, "alternative_action": None}
    elif tier == "BLOCKED":
        return {"reasoning": f"BLOCKED command '{command}'. Hard deny.", "risk_flags": [], "confidence": 1.0, "alternative_action": None}
    else:
        return {"reasoning": f"SENSITIVE command '{command}'. Requires policy check.", "risk_flags": ["REVIEW"], "confidence": 0.65, "alternative_action": None}

def policy_generator(params):
    """Generate a deterministic policy decision from params."""
    tier = params.get("tier", "SAFE")
    if tier == "SAFE":
        return {"decision": "GRANTED", "reason": "SAFE tier auto-grant"}
    elif tier == "BLOCKED":
        return {"decision": "BLOCKED", "reason": "BLOCKED tier hard deny"}
    else:
        return {"decision": "DENIED", "reason": "SENSITIVE default deny (offline)"}

def health_generator(params):
    """Generate a mock health check response."""
    return {
        "os": params.get("os", "linux"),
        "mem_free_pct": 78,
        "swap_used_pct": 0,
        "disk_free_pct": 63,
        "status": "healthy",
        "notes": "mock health — use real checks for production"
    }


# --- Convenience wrappers ---

def mock_mirror(run):
    return mock_call("mirror", {"tier": run.get("tier"), "command": run.get("command"), "seed": run.get("seed")}, mirror_generator)

def mock_policy(run):
    return mock_call("policy", {"tier": run.get("tier"), "command": run.get("command")}, policy_generator)

def mock_health(params=None):
    return mock_call("health", params or {}, health_generator)


if __name__ == "__main__":
    # Quick self-test
    print("=== Mock Mirror ===")
    print(json.dumps(mock_mirror({"tier": "SENSITIVE", "command": "curl", "seed": 123}), indent=2))
    print("\n=== Mock Policy ===")
    print(json.dumps(mock_policy({"tier": "SENSITIVE", "command": "curl"}), indent=2))
    print("\n=== Mock Health ===")
    print(json.dumps(mock_health(), indent=2))
    print("\n=== Cache hit test ===")
    print(json.dumps(mock_mirror({"tier": "SENSITIVE", "command": "curl", "seed": 123}), indent=2))
