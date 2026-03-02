# AEAP - Efficient API Economy Protocol

A local optimization layer that reduces API usage through caching, lazy evaluation, batching, context pruning, and offline fallbacks.

**Core principle:** AEAP is designed to REDUCE API calls, not increase them.

## Installation

```bash
# AEAP is already installed in your workspace
# Just import it:
from aeap import Cache, CostTracker, ContextManager, LazyExecutor, Batcher, OfflineFallback, AuditLog
```

## Components

### 1. Cache - Reduces redundant API calls

```python
from aeap import Cache

cache = Cache(default_ttl=3600)  # 1 hour TTL

# Store value
cache.set("user_profile_123", {"name": "Alice", "age": 30})

# Retrieve value (no API call if cached)
profile = cache.get("user_profile_123")
# Returns: {"name": "Alice", "age": 30}

# Check cache stats
stats = cache.get_stats()
# Returns: {"total_entries": 1, "total_hits": 1, "total_misses": 0}
```

### 2. CostTracker - Tracks API costs

```python
from aeap import CostTracker

tracker = CostTracker(budget=1.0)  # $1.00 budget

# Record an API call
tracker.record_call(
    model="gpt-4",
    tokens_in=100,
    tokens_out=50,
    cost=0.01
)

# Get total cost
total = tracker.get_total()
# CostRecord(total_cost=0.01, total_calls=1, ...)

# Get per-model stats
model_stats = tracker.get_record("gpt-4")
```

### 3. ContextManager - Prunes irrelevant history

```python
from aeap import ContextManager

cm = ContextManager(max_tokens=10000, relevance_threshold=0.5)

# Add context entries
cm.add("User asked about X", relevance_score=0.9)
cm.add("User asked about Y", relevance_score=0.3)
cm.add("User asked about Z", relevance_score=1.0)

# Prune to fit within max_tokens
pruned = cm.prune()
# Returns only high-relevance entries

# Get stats
stats = cm.get_stats()
# {"total_entries": 3, "estimated_tokens": 1500, "max_tokens": 10000}
```

### 4. LazyExecutor - Defers API calls until needed

```python
from aeap import LazyExecutor

executor = LazyExecutor()

# Define expensive function
def fetch_user_profile(user_id):
    print(f"API CALL: fetching user {user_id}")
    return {"user_id": user_id, "name": f"User {user_id}"}

# Execute function (no API call yet)
profile_lazy = executor.execute(
    func=fetch_user_profile,
    args=(123,),
    cache_key="user_profile_123"
)

# API call happens NOW
profile = executor.get(profile_lazy)
# Output: API CALL: fetching user 123
# Returns: {"user_id": 123, "name": "User 123"}

# Subsequent calls use cache
profile2 = executor.get(profile_lazy)
# No API call - uses cached value
```

### 5. Batcher - Combines multiple requests

```python
from aeap import Batcher

batcher = Batcher(batch_delay=0.1)

# Define API functions
def fetch_user(user_id):
    print(f"API CALL: fetching user {user_id}")
    return {"user_id": user_id, "name": f"User {user_id}"}

# Add requests
batcher.add(fetch_user, args=(1,))
batcher.add(fetch_user, args=(2,))
batcher.add(fetch_user, args=(3,))

# Flush executes all requests
results = batcher.flush()
# Output: API CALL: fetching user 1
#         API CALL: fetching user 2
#         API CALL: fetching user 3
# Returns: {0: {...}, 1: {...}, 2: {...}}
```

### 6. OfflineFallback - Local-first execution

```python
from aeap import OfflineFallback

fallback = OfflineFallback()

# Define local and API functions
def local_greeting(name):
    print("LOCAL: greeting", name)
    return f"Hello {name}!"

def api_greeting(name):
    print("API: greeting", name)
    return f"Hello {name} (from API)!"

# Register fallback
fallback.register(
    name="greeting",
    local_func=local_greeting,
    api_func=api_greeting,
    ttl=300  # Cache local result for 5 minutes
)

# Execute - uses local first
result = fallback.execute("greeting", "Alice")
# Output: LOCAL: greeting Alice
# Returns: "Hello Alice!"

# After TTL, API is called
result = fallback.execute("greeting", "Bob")
# Output: API: greeting Bob
```

### 7. AuditLog - Tracks all API calls

```python
from aeap import AuditLog

audit = AuditLog(log_file="api_calls.json")

# Log an API call
audit.log_call(
    model="gpt-4",
    tokens_in=100,
    tokens_out=50,
    cost=0.01,
    purpose="user_query",
    success=True,
    cache_hit=False
)

# Get audit stats
stats = audit.get_stats()
# {
#     "total_calls": 1,
#     "total_cost": 0.01,
#     "total_tokens_in": 100,
#     "total_tokens_out": 50,
#     "success_rate": 1.0,
#     "cache_hit_rate": 0.0
# }

# Export to CSV
audit.export_csv("audit.csv")
```

## Example: End-to-End Usage

```python
from aeap import Cache, CostTracker, LazyExecutor, AuditLog

# Initialize
cache = Cache(default_ttl=3600)
tracker = CostTracker()
audit = AuditLog()

executor = LazyExecutor()

# Define expensive API function
@aeap_lazy(cache_key="weather_city")
def fetch_weather(city):
    # This is where actual API call would happen
    print(f"API CALL: fetching weather for {city}")
    return {"city": city, "temp": 72, "condition": "sunny"}

# Use AEAP to reduce API calls
for city in ["New York", "London", "Paris", "Tokyo", "New York"]:
    # First call - API call happens
    weather = executor.execute(fetch_weather, args=(city,))
    temp = executor.get(weather)

    # Second call to same city - uses cache (NO API CALL)
    weather2 = executor.execute(fetch_weather, args=(city,))
    temp2 = executor.get(weather2)

    print(f"{city}: {temp['temp']}°F (cached: {temp2['temp']}°F)")

    # Record cost
    tracker.record_call(
        model="weather_api",
        tokens_in=50,
        tokens_out=20,
        cost=0.005
    )

    # Log to audit
    audit.log_call(
        model="weather_api",
        tokens_in=50,
        tokens_out=20,
        cost=0.005,
        purpose="weather_query"
    )

# Check efficiency
print("\n=== AEAP Stats ===")
print("Cache hits:", cache.get_stats()["total_hits"])
print("Total cost:", tracker.get_total().total_cost)
print("Audit entries:", audit.get_stats()["total_calls"])
```

## Principles

1. **Maximum efficiency:** Every API call must be justified, optimized, and necessary
2. **Zero waste:** No redundant calls, no wasted tokens, no unnecessary context
3. **Offline-first:** Use local execution when possible, API only when necessary
4. **Lazy evaluation:** Defer API calls until value is needed
5. **Caching:** Reuse results to avoid redundant calls
6. **Batching:** Combine multiple requests into one

## Safety

AEAP is a local optimization layer. It:
- **Never makes API calls itself**
- **Only logs API calls you make**
- **Reduces API usage, never increases it**
- **Is safe to use in production**

## License

Part of your workspace. Use freely.
