#!/usr/bin/env python3
"""
Simple test of AEAP components.

This script demonstrates AEAP without making any API calls.
"""

import sys
import os

# Add parent directory (workspace) to path so we can import aeap
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aeap import Cache, CostTracker, ContextManager, LazyExecutor, Batcher, AuditLog, OfflineFallback

print("=== AEAP Test Suite ===\n")

# Test 1: Cache
print("1. Testing Cache...")
cache = Cache(default_ttl=3600)
cache.set("test_key", "test_value")
result = cache.get("test_key")
assert result == "test_value", "Cache get failed"
print("   ✓ Cache works correctly")

# Test 2: CostTracker
print("\n2. Testing CostTracker...")
tracker = CostTracker()
tracker.record_call("test_model", tokens_in=100, tokens_out=50, cost=0.01)
stats = tracker.get_stats()
assert stats["total_cost"] == 0.01, "CostTracker failed"
print("   ✓ CostTracker works correctly")

# Test 3: ContextManager
print("\n3. Testing ContextManager...")
cm = ContextManager(max_tokens=1000, relevance_threshold=0.5, keep_recent=0)
cm.add("High relevance", relevance_score=0.9)
cm.add("Low relevance", relevance_score=0.3)
cm.add("Critical", relevance_score=1.0)
pruned = cm.prune()
assert len(pruned) == 2, f"ContextManager failed, got {len(pruned)} entries: {pruned}"
print("   ✓ ContextManager works correctly")

# Test 4: LazyExecutor
print("\n4. Testing LazyExecutor...")
executor = LazyExecutor()

call_count = [0]  # Use list to modify in nested function

def test_function():
    call_count[0] += 1
    return f"Called {call_count[0]} times"

lazy = executor.execute(test_function)
result = executor.get(lazy)
assert result == "Called 1 times", "LazyExecutor failed"
print(f"   ✓ LazyExecutor works (function called {call_count[0]} time)")

# Test 2: Batcher
print("\n5. Testing Batcher...")
batcher = Batcher(batch_delay=0.1)

def batch_function(x):
    return x * 2

batcher.add(batch_function, args=(1,))
batcher.add(batch_function, args=(2,))
batcher.add(batch_function, args=(3,))

results = batcher.flush()
assert results.total_calls == 3, "Batcher failed"
# Check that all results are present
assert len(results.results) == 3, f"Batcher result count failed: {len(results.results)}"
# The results dict values should be [2, 4, 6]
result_values = list(results.results.values())
assert sorted(result_values) == [2, 4, 6], f"Batcher calculation failed: {result_values}"
print("   ✓ Batcher works correctly")

# Test 6: AuditLog
print("\n6. Testing AuditLog...")
audit = AuditLog()
audit.log_call(
    model="test_model",
    tokens_in=100,
    tokens_out=50,
    cost=0.01,
    purpose="test_purpose",
    success=True
)
stats = audit.get_stats()
assert stats["total_calls"] == 1, "AuditLog failed"
print("   ✓ AuditLog works correctly")

# Test 7: OfflineFallback
print("\n7. Testing OfflineFallback...")

def local_func():
    return "local_result"

def api_func():
    return "api_result"

fallback = OfflineFallback()
fallback.register("test_rule", local_func, api_func, ttl=1)

# Should use local function
result = fallback.execute("test_rule")
assert result == "local_result", "OfflineFallback local failed"
print("   ✓ OfflineFallback works correctly")

# Test 8: AEAP Statistics
print("\n8. Testing AEAP Statistics...")
print(f"   Cache stats: {cache.get_stats()}")
print(f"   Cost stats: {tracker.get_stats()}")
print(f"   Context stats: {cm.get_stats()}")
print(f"   Executor stats: {executor.get_stats()}")
print(f"   Batch stats: {batcher.get_stats()}")
print(f"   Audit stats: {audit.get_stats()}")
print(f"   Fallback stats: {fallback.get_stats()}")

print("\n=== All Tests Passed ✓ ===")
print("\nAEAP is working correctly. No API calls were made.")
