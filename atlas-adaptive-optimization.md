# Adaptive Optimization System Design

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Task Classifier                          │
│  (detects: ghostwriting | factual_query | research | casual)│
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Profile Resolver                               │
│  maps task_type → { token_density, cache_aggressiveness,   │
│                    ask_threshold, [override_params] }      │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┼───────────┬───────────┐
          ▼           ▼           ▼           ▼
    ┌──────────┐┌──────────┐┌──────────┐┌──────────┐
    │ Ghost    ││ Factual   ││ Research ││  Casual  │
    │ Writing  ││ Query     ││          ││          │
    └────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
         │           │           │           │
         ▼           ▼           ▼           ▼
    ┌─────────────────────────────────────────────────────┐
    │              Optimization Pipeline                  │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
    │  │ Token       │  │ Cache       │  │ Confidence  │  │
    │  │ Density     │  │ Manager     │  │ Evaluator   │  │
    │  │ Controller  │  │             │  │             │  │
    │  └─────────────┘  └─────────────┘  └─────────────┘  │
    └─────────────────────────────────────────────────────┘
```

---

## Variable Definitions

### 1. token_density (0.0 → 1.0)

Controls verbosity and filler removal:

| Value | Behavior | Example Output |
|-------|----------|----------------|
| 0.0 | No stripping - preserve all redundancy, fillers, natural speech patterns | "So basically, what I think is that, you know, the thing is..." |
| 0.3 | Light editing - remove obvious fillers only | "What I think is that the thing is..." |
| 0.5 | Moderate - strip filler words, tighten prose | "I think the issue is..." |
| 0.8 | Aggressive - remove all redundancy, maximize information per token | "The issue is..." |
| 1.0 | Maximum compression - only core content remains | "Issue: X. Cause: Y." |

### 2. cache_aggressiveness (0.0 → 1.0)

Controls caching TTL and hit threshold:

| Value | TTL | Hit Threshold | Use Case |
|-------|-----|---------------|----------|
| 0.0 | 0 (off) | N/A | Nothing cached |
| 0.2 | 5 min | 95% similarity | Conservative |
| 0.5 | 30 min | 80% similarity | Moderate |
| 0.8 | 2 hours | 60% similarity | Aggressive |
| 1.0 | 24 hours | 40% similarity | Maximum reuse |

### 3. ask_threshold (0.0 → 1.0)

Controls when to ask vs auto-answer:

| Value | Behavior |
|-------|----------|
| 0.0 | Always ask for clarification (0% confidence = ask) |
| 0.3 | Ask if confidence < 30% |
| 0.5 | Ask if confidence < 50% (balanced) |
| 0.8 | Ask if confidence < 20% |
| 1.0 | Always auto-answer (never ask) |

---

## Task Type Profiles

### Profile: ghostwriting

**Objective:** High quality, preserve author's voice, literary merit

```python
ghostwriting_profile = {
    "token_density": 0.2,        # Light touch - preserve voice, natural cadence
    "cache_aggressiveness": 0.1, # Low - each piece is unique, cache off
    "ask_threshold": 0.7,        # Higher - author voice is paramount, clarify intent
    "max_tokens": "unlimited",   # Quality over brevity
    "temperature": 0.8,          # Creative, varied output
    "preserve_style_markers": True,
    "respect_first_person": True,
}
```

**Outcome example:**
> Input: "Write about loss"
> 
> Output (0.2): "The morning coffee tastes like absence. Her chair sits empty at the table, the newspaper still folded the way she left it three days ago. I trace the grain of the wood where her hand rested when she laughed."
> 
> Output (0.8): "Her chair is empty. The coffee tastes like absence."

---

### Profile: factual_query

**Objective:** Speed, accuracy, cached answers

```python
factual_query_profile = {
    "token_density": 0.6,        # Moderate - concise but complete
    "cache_aggressiveness": 0.9, # High - cache aggressively for speed
    "ask_threshold": 0.9,        # High - answer directly, don't interrupt
    "max_tokens": 150,           # Answer only
    "temperature": 0.1,         # Factual, minimal hallucination
    "source_citation": True,
    "staleness_check": True,     # Verify cache isn't outdated
}
```

**Outcome example:**
> Input: "What is the capital of Mongolia?"
> 
> Output (cache miss): "Ulaanbaatar. Population ~1.4 million. Timezone: UTC+8."
> 
> Output (cache hit, < 2hr): "Ulaanbaatar" [from cache, 0.3ms]

---

### Profile: research

**Objective:** Balanced depth, moderate caching, synthesis

```python
research_profile = {
    "token_density": 0.5,        # Moderate - balanced density
    "cache_aggressiveness": 0.5, # Moderate - cache findings, verify freshness
    "ask_threshold": 0.6,       # Balanced - ask for clarification on ambiguous queries
    "max_tokens": 800,           # Substantial but bounded
    "temperature": 0.3,         # Analytical, not overly creative
    "multi_sourceSynthesis": True,
    "include_uncertainties": True,
}
```

**Outcome example:**
> Input: "What are the effects of sleep deprivation on cognitive performance?"
> 
> Output (0.5): "Sleep deprivation degrades cognitive function across multiple domains. Meta-analysis of 27 studies shows:
> 
> - Attention: 37% reduction in sustained attention after 24h without sleep
> - Memory: 40% decrease in working memory capacity
> - Decision-making: Risk assessment impaired, similar to BAC 0.05%
> 
> Note: Individual variance high. Some ' isshort sleepers' show resilience."

---

### Profile: casual

**Objective:** Fast, minimal depth, conversational

```python
casual_profile = {
    "token_density": 0.7,        # High - quick, punchy responses
    "cache_aggressiveness": 0.4, # Low-moderate - some caching for speed
    "ask_threshold": 0.95,      # Very high - just answer, minimal interruption
    "max_tokens": 50,            # Short
    "temperature": 0.5,          # Friendly, conversational
    "emoji_allowed": True,       # If platform supports
    "use_slang": True,
}
```

**Outcome example:**
> Input: "what time is it in tokyo"
> 
> Output (0.7): "Tokyo is currently 9:42 PM JST (UTC+9). You're 8 hours behind if you're in NYC."

---

## Comparative Outcomes Matrix

### Same Input: "Explain quantum entanglement"

| Variable | ghostwriting (0.2/0.1/0.7) | factual (0.6/0.9/0.9) | research (0.5/0.5/0.6) | casual (0.7/0.4/0.95) |
|----------|---------------------------|------------------------|------------------------|----------------------|
| Length | 280 tokens | 85 tokens | 180 tokens | 45 tokens |
| Style | Poetic, metaphorical | Bullet facts | Structured analysis | Quick summary |
| Cache | No | Yes (2hr TTL) | Partial | Minimal |
| Asks clarification? | Sometimes | Rarely | Maybe | Almost never |
| Tone | "Spooky action at a distance..." | "Entangled particles share state..." | "Quantum entanglement is..." | "Basically, linked particles" |

---

## Dynamic Adjustment Rules

### Real-time Tuning

```python
def adjust_profile(base_profile, context):
    # If user repeats query → increase cache
    if context.get("repeated_query"):
        base_profile["cache_aggressiveness"] = min(1.0, 
            base_profile["cache_aggressiveness"] + 0.2)
    
    # If conversation is long → decrease verbosity
    if context.get("turn_count", 0) > 10:
        base_profile["token_density"] = min(1.0,
            base_profile["token_density"] + 0.1)
    
    # If user expresses confusion → ask more
    if context.get("user_expressed_confusion"):
        base_profile["ask_threshold"] = max(0.0,
            base_profile["ask_threshold"] - 0.2)
    
    return base_profile
```

### Example: Ghostwriting with Revision History

```
Session 1 (0.2 density):
  "The sunset bled orange across the water, and she stood alone..."

Session 2 (user: "make it shorter"):
  density → 0.4
  "The sunset bled orange. She stood alone..."

Session 3 (user: "more concise"):
  density → 0.7  
  "Orange sunset. Alone."
```

---

## Implementation Notes

1. **Default fallback:** If task type detection fails → use `research` profile
2. **User override:** Allow explicit profile selection: `!casual What is...`
3. **Gradual transitions:** Animate between profiles, don't snap
4. **Logging:** Track which profiles produce best user satisfaction scores per task type
5. **A/B testing:** Rotate profiles for same input, measure completion time + satisfaction

---

## Summary Table

| Task Type | token_density | cache_aggro | ask_threshold | Result |
|-----------|---------------|-------------|---------------|--------|
| ghostwriting | 0.2 | 0.1 | 0.7 | Voice-preserved, unique |
| factual_query | 0.6 | 0.9 | 0.9 | Fast, cached, accurate |
| research | 0.5 | 0.5 | 0.6 | Balanced depth |
| casual | 0.7 | 0.4 | 0.95 | Quick, minimal |
