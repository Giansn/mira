# Adaptive Speed Skill

Use this skill when you want to optimize your responses based on task type and network conditions.

## What It Does

Automatically detects the task profile and applies:
- **Token density** — how much filler to strip
- **Cache aggressiveness** — TTL and similarity threshold  
- **Ask threshold** — when to clarify vs. auto-answer
- **Latency adaptation** — tune based on known network latency

## Task Profiles

| Profile | Token Density | Cache | Ask Threshold | Use Case |
|---------|---------------|-------|---------------|----------|
| ghostwriting | 0.2 | 0.3 | 0.7 | Academic writing, thesis, essays |
| factual | 0.6 | 0.9 | 0.9 | Facts, definitions, data |
| research | 0.5 | 0.5 | 0.6 | Analysis, comparison, synthesis |
| casual | 0.7 | 0.4 | 0.95 | Quick chat, thanks, simple replies |

## Latency Adaptive Mode

When you know your network latency, the optimizer adjusts automatically:

```python
from simulations.adaptive_framework import get_optimizer, LATENCY_TIERS

# Local network (<50ms) = more aggressive caching
opt = get_optimizer(TaskProfile.RESEARCH, latency_ms=30)

# Slow network (>500ms) = less aggressive  
opt = get_optimizer(TaskProfile.RESEARCH, latency_ms=600)

# Check tier
tier = opt.get_latency_tier()  # "local", "fast", "moderate", "slow", "very_slow"
```

| Tier | Max Latency | Cache Boost | Density Boost |
|------|-------------|-------------|---------------|
| local | 50ms | +0.2 | +0.1 |
| fast | 150ms | +0.1 | +0.05 |
| moderate | 300ms | 0 | 0 |
| slow | 500ms | -0.1 | -0.1 |
| very_slow | >500ms | -0.2 | -0.2 |

## Subcontract Routing

Route complex tasks to specialist agents instead of self-simulating:

```python
from simulations.adaptive_framework import Subcontractor, TaskProfile

# Set up specialists
sub = Subcontractor()
sub.register_agent("ghostwriter", TaskProfile.GHOSTWRITING, latency_ms=300, trust_level=0.9)
sub.register_agent("retriever", TaskProfile.FACTUAL, latency_ms=150, trust_level=0.95)
sub.register_agent("researcher", TaskProfile.RESEARCH, latency_ms=400, trust_level=0.85)

# Decide: handle locally or subcontract?
decision = sub.should_subcontract(
    profile=TaskProfile.GHOSTWRITING,
    task_tokens=500,
    local_latency_ms=100,
)

if decision["subcontract"]:
    agent = decision["agent"]
    print(f"Routing to {agent.name}, ~{decision['estimated_remote_ms']}ms")
else:
    print(f"Handling locally: {decision['reason']}")
```

### Subcontract Decision Logic

- **Subcontract** if: remote agent is faster (accounting for quality bonus) AND trust >= 0.5
- **Local** if: no specialist available, or no time improvement, or low trust
- **Coordination overhead**: defaults to 200ms (configurable)
- **Quality bonus**: defaults to 500ms (specialist quality improvement)

## Usage

```python
from simulations.adaptive_framework import get_optimizer, TaskProfile

# Auto-detect with latency
opt = get_optimizer(context="...", question="...", latency_ms=250)

# Or specify profile
opt = get_optimizer(TaskProfile.GHOSTWRITING, latency_ms=100)

# Apply optimization
should_ask = opt.should_ask(confidence=0.5)
stripped = opt.strip_filler("Great question! Here's the answer...")
cache_ttl = opt.get_cache_ttl()

# Quality monitoring
result = opt.record_quality(quality_score=0.8)  # returns {action: "backoff"} if needed
```

## Integration Hook

For quick use at the start of any response:

```python
from simulations.adaptive_framework import get_optimizer

opt = get_optimizer(context=context, question=user_message, latency_ms=250)
profile = opt.profile.value
should_ask = opt.should_ask(confidence=my_confidence)
optimized_response = opt.strip_filler(draft_response)
```

## Quality Safeguards

The framework includes automatic quality monitoring:
- If quality drops below 0.5 with density > 0.8, it auto-backs off to 0.5
- Prevents the "optimization at cost of quality" failure mode

## Files

- `adaptive_framework.py` — main optimizer class + subcontractor
- `quick.py` — quick integration hook
