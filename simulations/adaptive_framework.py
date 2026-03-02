#!/usr/bin/env python3
"""
Adaptive Optimization Framework
Based on simulation results from Hyperion/Socrates/Judge swarm

Variables:
- token_density (0.0-1.0): filler stripping aggressiveness
- cache_aggressiveness (0.0-1.0): TTL and similarity threshold
- ask_threshold (0.0-1.0): auto-answer vs ask
- latency_ms: network latency for optimization tuning

Profiles:
- ghostwriting: preserve quality, voice
- factual: max speed
- research: balanced
- casual: fast, minimal

Subcontract: Route to specialist agents based on task type
"""

import time
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class TaskProfile(Enum):
    GHOSTWRITING = "ghostwriting"
    FACTUAL = "factual"
    RESEARCH = "research"
    CASUAL = "casual"
    LATENCY_ADAPTIVE = "latency_adaptive"

# Profile configurations (from simulation results)
PROFILES = {
    TaskProfile.GHOSTWRITING: {
        "token_density": 0.2,
        "cache_aggressiveness": 0.3,
        "ask_threshold": 0.7,
    },
    TaskProfile.FACTUAL: {
        "token_density": 0.6,
        "cache_aggressiveness": 0.9,
        "ask_threshold": 0.9,
    },
    TaskProfile.RESEARCH: {
        "token_density": 0.5,
        "cache_aggressiveness": 0.5,
        "ask_threshold": 0.6,
    },
    TaskProfile.CASUAL: {
        "token_density": 0.7,
        "cache_aggressiveness": 0.4,
        "ask_threshold": 0.95,
    },
    TaskProfile.LATENCY_ADAPTIVE: {
        "token_density": 0.5,
        "cache_aggressiveness": 0.5,
        "ask_threshold": 0.6,
    },
}

# Latency-based optimization tiers
LATENCY_TIERS = {
    "local": {"max_ms": 50, "cache_boost": 0.2, "density_boost": 0.1},
    "fast": {"max_ms": 150, "cache_boost": 0.1, "density_boost": 0.05},
    "moderate": {"max_ms": 300, "cache_boost": 0.0, "density_boost": 0.0},
    "slow": {"max_ms": 500, "cache_boost": -0.1, "density_boost": -0.1},
    "very_slow": {"max_ms": float("inf"), "cache_boost": -0.2, "density_boost": -0.2},
}

# Quality warning thresholds (from Hyperion-Cautious)
QUALITY_WARNING_DENSITY = 0.8
QUALITY_BACKOFF_DENSITY = 0.5

@dataclass
class AdaptiveConfig:
    token_density: float
    cache_aggressiveness: float
    ask_threshold: float
    latency_ms: int = 0  # Network latency for tuning
    
    @classmethod
    def for_profile(cls, profile: TaskProfile, latency_ms: int = 0) -> "AdaptiveConfig":
        p = PROFILES[profile]
        config = cls(
            token_density=p["token_density"],
            cache_aggressiveness=p["cache_aggressiveness"],
            ask_threshold=p["ask_threshold"],
            latency_ms=latency_ms,
        )
        
        # Apply latency adjustments if specified
        if latency_ms > 0 and profile != TaskProfile.GHOSTWRITING:
            config = cls._apply_latency_adjustment(config, latency_ms)
        
        return config
    
    @classmethod
    def _apply_latency_adjustment(cls, config: "AdaptiveConfig", latency_ms: int) -> "AdaptiveConfig":
        """Adjust config based on known network latency."""
        tier = "local"
        for t, info in LATENCY_TIERS.items():
            if latency_ms <= info["max_ms"]:
                tier = t
                break
        
        adjustments = LATENCY_TIERS[tier]
        
        # Higher latency = less caching, less aggressive optimization
        new_cache = max(0, min(1, config.cache_aggressiveness + adjustments["cache_boost"]))
        new_density = max(0, min(1, config.token_density + adjustments["density_boost"]))
        
        return cls(
            token_density=new_density,
            cache_aggressiveness=new_cache,
            ask_threshold=config.ask_threshold,
            latency_ms=latency_ms,
        )

class AdaptiveOptimizer:
    """
    Main adaptive optimizer class.
    Adjusts behavior based on task type and network latency.
    
    Usage:
        opt = AdaptiveOptimizer(TaskProfile.RESEARCH, latency_ms=250)
        opt.should_ask(confidence=0.7)
        opt.strip_filler(draft_response)
        opt.get_cache_ttl()
    """
    
    def __init__(self, profile: TaskProfile = TaskProfile.RESEARCH, latency_ms: int = 0):
        self.profile = profile
        self.config = AdaptiveConfig.for_profile(profile, latency_ms)
        self._quality_history = []
        self._latency_ms = latency_ms
    
    def should_ask(self, confidence: float) -> bool:
        """Decide whether to ask user or auto-answer."""
        return confidence < self.config.ask_threshold
    
    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds based on aggressiveness."""
        # 0.0 -> 5min, 1.0 -> 24hr
        base = 300  # 5 min
        max_ttl = 86400  # 24 hr
        return int(base + (max_ttl - base) * self.config.cache_aggressiveness)
    
    def get_similarity_threshold(self) -> float:
        """Get similarity threshold for cache hits."""
        # 0.0 -> 40%, 1.0 -> 95%
        return 0.40 + 0.55 * self.config.cache_aggressiveness
    
    def strip_filler(self, text: str) -> str:
        """
        Strip filler based on token_density.
        Higher density = more aggressive stripping.
        """
        if self.config.token_density < 0.1:
            return text
        
        filler_phrases = [
            "Great question!",
            "I'd be happy to help",
            "Here's the analysis",
            "Let me think about that",
            "As you can see",
            "Basically,",
            "Actually,",
            "So,",
            "Anyway,",
            "I would like to",
            "It is important to note",
        ]
        
        result = text
        for phrase in filler_phrases:
            # Higher density = more aggressive (replace with shorter forms)
            if self.config.token_density > 0.6:
                result = result.replace(phrase, "")
            elif self.config.token_density > 0.3:
                result = result.replace(phrase, phrase.split()[0])
        
        # Collapse whitespace
        import re
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def record_quality(self, quality_score: float):
        """Record quality metric for adaptive adjustment."""
        self._quality_history.append({
            "score": quality_score,
            "timestamp": time.time(),
            "density": self.config.token_density,
        })
        
        # Check for quality degradation (Hyperion-Cautious warning)
        if len(self._quality_history) >= 5:
            recent = self._quality_history[-5:]
            if all(q["score"] < 0.5 for q in recent) and self.config.token_density > QUALITY_WARNING_DENSITY:
                # Quality drop + high density = back off
                self.config.token_density = QUALITY_BACKOFF_DENSITY
                return {"action": "backoff", "new_density": QUALITY_BACKOFF_DENSITY}
        
        return {"action": "stable"}
    
    def detect_profile(self, context: str, question: str) -> TaskProfile:
        """
        Auto-detect task profile from context/question.
        Simple heuristic - can be enhanced with classifier.
        """
        q_lower = question.lower()
        c_lower = context.lower()
        
        # Ghostwriting indicators
        ghostwriting_kw = ["write", "essay", "thesis", "paper", "academic", "draft", "chapter"]
        if any(kw in q_lower for kw in ghostwriting_kw):
            return TaskProfile.GHOSTWRITING
        
        # Factual indicators
        factual_kw = ["what is", "when did", "who was", "define", "fact", "number", "date"]
        if any(kw in q_lower for kw in factual_kw):
            return TaskProfile.FACTUAL
        
        # Research indicators
        research_kw = ["analyze", "compare", "research", "study", "implications", "evidence"]
        if any(kw in q_lower for kw in research_kw):
            return TaskProfile.RESEARCH
        
        # Casual indicators
        casual_kw = ["hey", "hi", "thanks", "cool", "nice", "what do you think"]
        if any(kw in q_lower for kw in casual_kw):
            return TaskProfile.CASUAL
        
        # Default
        return TaskProfile.RESEARCH
    
    def get_latency_tier(self) -> str:
        """Get the latency tier name based on configured latency."""
        if self._latency_ms <= 0:
            return "unknown"
        for tier, info in LATENCY_TIERS.items():
            if self._latency_ms <= info["max_ms"]:
                return tier
        return "very_slow"


class SubcontractAgent:
    """
    Represents a specialist agent for subcontracting.
    
    Attributes:
        name: Agent identifier
        profile: TaskProfile this agent specializes in
        latency_ms: Startup + response latency
        trust_level: 0-1 trust rating
        capabilities: List of capability tags
    """
    
    def __init__(
        self,
        name: str,
        profile: TaskProfile,
        latency_ms: int = 200,
        trust_level: float = 0.8,
        capabilities: List[str] = None,
    ):
        self.name = name
        self.profile = profile
        self.latency_ms = latency_ms
        self.trust_level = trust_level
        self.capabilities = capabilities or []
    
    def can_handle(self, profile: TaskProfile) -> bool:
        """Check if this agent can handle the given profile."""
        return self.profile == profile
    
    def estimate_total_time(self, task_tokens: int) -> int:
        """Estimate total time in ms for a task of given size."""
        # Rough estimate: ~10ms per token for processing
        processing_ms = task_tokens * 10
        return self.latency_ms + processing_ms


class Subcontractor:
    """
    Routes tasks to specialist agents based on profile and requirements.
    
    Usage:
        sub = Subcontractor()
        sub.register_agent("ghostwriter", TaskProfile.GHOSTWRITING, latency_ms=300)
        sub.register_agent("retriever", TaskProfile.FACTUAL, latency_ms=150)
        
        # Decide whether to subcontract
        decision = sub.should_subcontract(
            profile=TaskProfile.GHOSTWRITING,
            task_tokens=500,
            local_latency_ms=100
        )
    """
    
    def __init__(self):
        self._agents: Dict[TaskProfile, List[SubcontractAgent]] = {
            TaskProfile.GHOSTWRITING: [],
            TaskProfile.FACTUAL: [],
            TaskProfile.RESEARCH: [],
            TaskProfile.CASUAL: [],
        }
        self._default_agents = []  # Agents that can handle any task
    
    def register_agent(
        self,
        name: str,
        profile: TaskProfile,
        latency_ms: int = 200,
        trust_level: float = 0.8,
        capabilities: List[str] = None,
        default: bool = False,
    ):
        """Register a specialist agent."""
        agent = SubcontractAgent(name, profile, latency_ms, trust_level, capabilities)
        
        if default:
            self._default_agents.append(agent)
        else:
            self._agents[profile].append(agent)
    
    def should_subcontract(
        self,
        profile: TaskProfile,
        task_tokens: int,
        local_latency_ms: int = 0,
        coordination_overhead_ms: int = 200,
        quality_bonus_ms: int = 500,
    ) -> Dict[str, Any]:
        """
        Decide whether to handle locally or subcontract.
        
        Args:
            profile: TaskProfile to route
            task_tokens: Estimated token count for the task
            local_latency_ms: Your local processing latency
            coordination_overhead_ms: Overhead for coordinating with remote agent
            quality_bonus_ms: Estimated time savings from specialist quality
        
        Returns:
            {
                "subcontract": bool,
                "reason": str,
                "agent": SubcontractAgent or None,
                "estimated_local_ms": int,
                "estimated_remote_ms": int,
            }
        """
        # Get available agents for this profile
        agents = self._agents.get(profile, []) + self._default_agents
        
        if not agents:
            return {
                "subcontract": False,
                "reason": "no_specialist_available",
                "agent": None,
                "estimated_local_ms": task_tokens * 10 + local_latency_ms,
                "estimated_remote_ms": None,
            }
        
        # Find best agent (lowest total time)
        best_agent = None
        best_time = float("inf")
        
        for agent in agents:
            remote_time = agent.estimate_total_time(task_tokens) + coordination_overhead_ms
            if remote_time < best_time:
                best_time = remote_time
                best_agent = agent
        
        # Local processing estimate
        local_time = task_tokens * 10 + local_latency_ms
        
        # Specialist agents have quality benefits (0.85/1 vs 0.7/1 self-simulated)
        # This translates to fewer revision cycles = time savings
        effective_remote_time = best_time - quality_bonus_ms
        
        # Decision: subcontract if agent is faster (accounting for quality bonus) AND trust is acceptable
        subcontract = (
            best_agent and
            effective_remote_time < local_time and
            best_agent.trust_level >= 0.5
        )
        
        if subcontract:
            reason = "faster_trusted"
        elif not best_agent:
            reason = "no_specialist"
        elif best_agent.trust_level < 0.5:
            reason = "low_trust"
        else:
            reason = "no_improvement"
        
        return {
            "subcontract": subcontract,
            "reason": reason,
            "agent": best_agent,
            "estimated_local_ms": local_time,
            "estimated_remote_ms": best_time,
        }
    
    def get_specialist(self, profile: TaskProfile) -> Optional[SubcontractAgent]:
        """Get the best specialist for a profile."""
        agents = self._agents.get(profile, []) + self._default_agents
        if not agents:
            return None
        # Return lowest latency agent
        return min(agents, key=lambda a: a.latency_ms)


# Convenience function
def get_optimizer(
    profile: TaskProfile = None,
    context: str = "",
    question: str = "",
    latency_ms: int = 0,
) -> AdaptiveOptimizer:
    """Get optimizer for task profile.
    
    Args:
        profile: TaskProfile enum or None for auto-detect
        context: Context string for profile detection
        question: Question string for profile detection
        latency_ms: Known network latency for optimization tuning
    """
    if profile is None:
        # Auto-detect
        optimizer = AdaptiveOptimizer(latency_ms=latency_ms)
        profile = optimizer.detect_profile(context, question)
        return AdaptiveOptimizer(profile, latency_ms=latency_ms)
    return AdaptiveOptimizer(profile, latency_ms=latency_ms)


if __name__ == "__main__":
    # Demo
    for profile in TaskProfile:
        opt = AdaptiveOptimizer(profile)
        print(f"\n{profile.value}:")
        print(f"  token_density: {opt.config.token_density}")
        print(f"  cache_aggressiveness: {opt.config.cache_aggressiveness}")
        print(f"  ask_threshold: {opt.config.ask_threshold}")
        print(f"  cache_ttl: {opt.get_cache_ttl()}s")
