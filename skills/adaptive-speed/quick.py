#!/usr/bin/env python3
"""
Quick Adaptive Speed - One-liner for any agent

Usage:
    from skills.adaptive_speed import quick_optimize
    result = quick_optimize(context, question, draft)
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace"))

from simulations.adaptive_framework import AdaptiveOptimizer, TaskProfile

def quick_optimize(
    context: str = "",
    question: str = "",
    draft: str = None,
    profile: str = None,
    latency_ms: int = 0,
) -> dict:
    """
    One-liner adaptive optimization.
    
    Args:
        context: Conversation context
        question: User's question
        draft: Optional draft response to optimize
        profile: Optional manual profile ("ghostwriting", "factual", "research", "casual")
        latency_ms: Known network latency for tuning (0 = unknown)
    
    Returns:
        dict with profile, should_ask, optimized_response, cache_ttl
    """
    # Detect or use specified profile
    if profile:
        task_profile = TaskProfile(profile.lower())
    else:
        optimizer = AdaptiveOptimizer(TaskProfile.RESEARCH, latency_ms=latency_ms)
        task_profile = optimizer.detect_profile(context, question)
    
    opt = AdaptiveOptimizer(task_profile, latency_ms=latency_ms)
    
    result = {
        "profile": task_profile.value,
        "latency_tier": opt.get_latency_tier(),
        "token_density": opt.config.token_density,
        "ask_threshold": opt.config.ask_threshold,
        "cache_ttl": opt.get_cache_ttl(),
        "should_ask": None,
        "optimized_response": None,
    }
    
    if draft:
        result["optimized_response"] = opt.strip_filler(draft)
    
    return result

def should_i_ask(context: str, question: str, my_confidence: float, latency_ms: int = 0) -> bool:
    """Quick helper: should I ask for clarification or just answer?"""
    opt = AdaptiveOptimizer(latency_ms=latency_ms)
    opt.profile = opt.detect_profile(context, question)
    return opt.should_ask(my_confidence)

# Example:
# from skills.adaptive_speed import quick_optimize
# result = quick_optimize("working on thesis", "write my intro", latency_ms=200)
# print(result["profile"])  # "ghostwriting"
