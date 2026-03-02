#!/usr/bin/env python3
"""
Adaptive Integration Hook
Use this at the start of each response to optimize behavior
"""

import sys
sys.path.insert(0, "/home/ubuntu/.openclaw/workspace")

from simulations.adaptive_framework import AdaptiveOptimizer, TaskProfile, get_optimizer

def adapt_response(context: str, question: str, draft_response: str = None) -> dict:
    """
    Main adaptation function - call at start of response processing.
    
    Returns dict with:
    - profile: detected task profile
    - should_ask: whether to clarify before answering
    - filler_stripped: response with filler removed (if draft provided)
    - cache_ttl: recommended cache TTL
    """
    optimizer = get_optimizer(context=context, question=question)
    
    result = {
        "profile": optimizer.profile.value,
        "token_density": optimizer.config.token_density,
        "cache_aggressiveness": optimizer.config.cache_aggressiveness,
        "ask_threshold": optimizer.config.ask_threshold,
        "cache_ttl": optimizer.get_cache_ttl(),
        "should_ask": None,
        "filler_stripped": None,
    }
    
    # If we have a draft response, apply token density
    if draft_response:
        result["filler_stripped"] = optimizer.strip_filler(draft_response)
    
    return result

# CLI for testing
if __name__ == "__main__":
    if len(sys.argv) > 1:
        context = sys.argv[1] if len(sys.argv) > 1 else ""
        question = sys.argv[2] if len(sys.argv) > 2 else "hello"
        
        result = adapt_response(context, question)
        print(f"Profile: {result['profile']}")
        print(f"Token density: {result['token_density']}")
        print(f"Ask threshold: {result['ask_threshold']}")
        print(f"Cache TTL: {result['cache_ttl']}s")
