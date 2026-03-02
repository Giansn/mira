"""
Adaptive Speed Skill

Quick access:
    from skills.adaptive_speed import quick_optimize, should_i_ask
    
    result = quick_optimize(context="...", question="...", draft="...")
    should_ask = should_i_ask(context, question, confidence)
"""

from .quick import quick_optimize, should_i_ask
from ..simulations.adaptive_framework import AdaptiveOptimizer, TaskProfile, PROFILES, Subcontractor, LATENCY_TIERS

__all__ = [
    "quick_optimize",
    "should_i_ask", 
    "AdaptiveOptimizer",
    "TaskProfile",
    "PROFILES",
    "Subcontractor",
    "LATENCY_TIERS",
]
