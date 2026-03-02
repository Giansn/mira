#!/usr/bin/env python3
"""
Hot-Workspace Swarm Simulator v2
77 branches with multi-agent reflective bouncing (Atlas + Judge + Socrates)

Mirror Engine: Agents bounce ideas between each other, accelerating branching.
"""

import json
import os
import random
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
import threading
import queue

SIM_DIR = Path("/home/ubuntu/.openclaw/workspace/simulations/hot_workspace_v2")
BRANCHES_DIR = SIM_DIR / "branches"
MIRROR_LOG = SIM_DIR / "mirror_reflections.jsonl"

SIM_DIR.mkdir(exist_ok=True)
BRANCHES_DIR.mkdir(exist_ok=True)

# Global state
branch_counter = 0
lock = threading.Lock()

@dataclass
class AgentReflection:
    """A reflection bounce between agents."""
    from_agent: str
    to_agent: str
    branch_id: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Branch:
    branch_id: str
    name: str
    depth: int
    parent_id: Optional[str]
    config: dict
    evaluations: dict = field(default_factory=dict)
    reflections: List[AgentReflection] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# === AGENT PROMPTS ===

ATLAS_PROMPTS = {
    "expert": "You are Atlas, the expert architect. Evaluate this design for technical completeness.",
    "creative": "You are Atlas, the creative inventor. Suggest unconventional improvements.",
    "cautious": "You are Atlas, the cautious guardian. Identify all failure modes and risks.",
    "devil_advocate": "You are Atlas, the devil's advocate. Argue against this design.",
}

JUDGE_PROMPTS = {
    "safety": "You are Judge, the fairness evaluator. Score this on safety (0-1).",
    "practicality": "You are Judge, the practical scorer. Score this on practicality (0-1).",
    "overall": "You are Judge, the final arbiter. Give an overall score (0-1).",
}

SOCRATES_PROMPTS = {
    "question": "You are Socrates, the wise questioner. Ask probing questions about this.",
    "wisdom": "You are Socrates, the wisdom seeker. What deeper truth does this reveal?",
    "challenge": "You are Socrates, the challenger. Question the assumptions.",
}

# === BRANCH CONFIGURATIONS ===

BASE_CONFIGS = [
    {"name": "prewarm-cat", "prewarm": "cat", "scratch": "none", "risk": "none"},
    {"name": "prewarm-fadvise", "prewarm": "fadvise", "scratch": "none", "risk": "none"},
    {"name": "prewarm-mlock", "prewarm": "mlock", "scratch": "none", "risk": "low"},
    {"name": "scratch-tmp", "prewarm": "none", "scratch": "/tmp", "risk": "medium"},
    {"name": "scratch-devshm", "prewarm": "none", "scratch": "/dev/shm", "risk": "high"},
    {"name": "full-tmp", "prewarm": "cat", "scratch": "/tmp", "risk": "medium"},
    {"name": "full-devshm", "prewarm": "cat", "scratch": "/dev/shm", "risk": "high"},
    {"name": "monitor-only", "prewarm": "none", "scratch": "none", "risk": "none"},
]

# Generate variations
def generate_variations(base_configs: List[dict], target: int) -> List[dict]:
    """Generate variations to reach target branch count."""
    variations = []
    sizes = [256, 512, 1024]
    monitors = [True, False]
    
    while len(variations) < target:
        base = random.choice(base_configs)
        var = base.copy()
        var["name"] = f"{base['name']}-v{len(variations)}"
        var["scratch_size"] = random.choice(sizes)
        var["monitor"] = random.choice(monitors)
        
        # Add specific tweaks
        if "prewarm" in var["name"] and var["prewarm"] != "none":
            var["prewarm_files"] = random.choice([
                "*.md", "thesis*.md", "memory/*.md", "*.md,*.py"
            ])
        
        variations.append(var)
    
    return variations[:target]

# === AGENT EVALUATIONS (simulated) ===

def evaluate_atlas(config: dict, depth: int) -> dict:
    """Atlas evaluation - technical expert."""
    base_score = 0.75
    depth_bonus = min(depth * 0.02, 0.1)
    
    # Technical scoring
    scores = {
        "technical_completeness": min(base_score + depth_bonus + random.uniform(0, 0.1), 1.0),
        "innovation": random.uniform(0.6, 0.9),
        "risk_awareness": 1.0 - ({"none": 0, "low": 0.2, "medium": 0.5, "high": 0.8}.get(config.get("risk", "none"), 0.5)),
    }
    scores["overall"] = sum(scores.values()) / len(scores)
    return scores

def evaluate_judge(config: dict, depth: int) -> dict:
    """Judge evaluation - fairness scorer."""
    risk_map = {"none": 1.0, "low": 0.8, "medium": 0.5, "high": 0.2}
    risk = config.get("risk", "none")
    
    scores = {
        "safety": 1.0,
        "practicality": 0.9 if config.get("scratch") != "none" else 0.7,
        "persistence_risk": risk_map.get(risk, 0.5),
        "fairness": random.uniform(0.7, 0.95),
    }
    scores["overall"] = sum(scores.values()) / len(scores)
    return scores

def evaluate_socrates(config: dict, depth: int) -> dict:
    """Socrates evaluation - wisdom seeker."""
    questions = [
        f"Does {config.get('prewarm', 'none')} prewarm actually help?",
        f"What happens when {config.get('scratch', 'none')} fills up?",
        f"Is the complexity worth the speedup?",
        f"Does this work across all platforms?",
    ]
    
    return {
        "wisdom_questions": random.sample(questions, 2),
        "depth_insight": min(depth * 0.1, 0.5),
        "philosophical_score": random.uniform(0.6, 0.9),
    }

# === MIRROR ENGINE - REFLECTIVE BOUNCING ===

def generate_mirror_reflection(from_agent: str, to_agent: str, branch: Branch) -> AgentReflection:
    """Generate a reflection bounce between agents."""
    
    reflections = {
        ("Atlas", "Judge"): f"Atlas questions whether Judge's {branch.config.get('risk', 'none')} risk score accounts for data loss scenarios.",
        ("Atlas", "Socrates"): f"Atlas wonders: {random.choice(['What is the true cost of speed?', 'Is optimization always good?'])}",
        ("Judge", "Atlas"): f"Judge asks Atlas to clarify the technical tradeoffs of {branch.config.get('prewarm', 'none')} approach.",
        ("Judge", "Socrates"): f"Judge ponders with Socrates: Is a 0.1s speedup worth the complexity?",
        ("Socrates", "Atlas"): f"Socrates asks Atlas: What assumptions does this design make about kernel behavior?",
        ("Socrates", "Judge"): f"Socrates challenges Judge: Is {branch.config.get('risk', 'none')} risk the right metric?",
    }
    
    key = (from_agent, to_agent)
    content = reflections.get(key, f"{from_agent} reflects to {to_agent} on {branch.name}")
    
    return AgentReflection(
        from_agent=from_agent,
        to_agent=to_agent,
        branch_id=branch.branch_id,
        content=content
    )

def run_mirror_round(branches: List[Branch], round_num: int) -> List[AgentReflection]:
    """Run a mirror reflection round - agents bounce ideas."""
    reflections = []
    
    for branch in branches:
        # Each branch gets 1-3 reflections
        num_reflections = random.randint(1, 3)
        
        agent_pairs = [
            ("Atlas", "Judge"),
            ("Atlas", "Socrates"), 
            ("Judge", "Atlas"),
            ("Judge", "Socrates"),
            ("Socrates", "Atlas"),
            ("Socrates", "Judge"),
        ]
        
        for _ in range(num_reflections):
            from_a, to_a = random.choice(agent_pairs)
            refl = generate_mirror_reflection(from_a, to_a, branch)
            reflections.append(refl)
            branch.reflections.append(refl)
    
    # Log reflections
    with open(MIRROR_LOG, "a") as f:
        for r in reflections:
            f.write(json.dumps(asdict(r)) + "\n")
    
    return reflections

# === MAIN SIMULATION ===

def create_branch(config: dict, depth: int, parent_id: Optional[str]) -> Branch:
    global branch_counter
    with lock:
        branch_counter += 1
        bid = f"branch-{branch_counter:03d}"
    
    branch = Branch(
        branch_id=bid,
        name=config.get("name", bid),
        depth=depth,
        parent_id=parent_id,
        config=config,
    )
    
    # Run evaluations
    branch.evaluations["atlas"] = evaluate_atlas(config, depth)
    branch.evaluations["judge"] = evaluate_judge(config, depth)
    branch.evaluations["socrates"] = evaluate_socrates(config, depth)
    
    # Save branch
    with open(BRANCHES_DIR / f"{bid}.json", "w") as f:
        json.dump(asdict(branch), f, indent=2)
    
    return branch

def run_simulation(target_branches: int = 77):
    global branch_counter
    
    print(f"\n{'#'*70}")
    print(f"# HOT-WORKSPACE SWARM SIMULATION")
    print(f"# Target: {target_branches} branches")
    print(f"# Agents: Atlas (expert), Judge (fairness), Socrates (wisdom)")
    print(f"# Mirror Engine: Reflective bouncing between agents")
    print(f"{'#'*70}")
    
    # Generate configurations
    configs = generate_variations(BASE_CONFIGS, target_branches)
    
    print(f"\nGenerated {len(configs)} branch configurations")
    
    # Phase 1: Create initial branches (first wave)
    print(f"\n--- Phase 1: Initial Branch Creation (20 branches) ---")
    branches = []
    for config in configs[:20]:
        branch = create_branch(config, depth=0, parent_id=None)
        branches.append(branch)
        print(f"  Created: {branch.name}")
    
    # Mirror round 1
    print(f"\n--- Mirror Round 1: Agent Reflections ---")
    reflections1 = run_mirror_round(branches, 1)
    print(f"  Generated {len(reflections1)} reflections")
    
    # Phase 2: Spawn child branches (depth 1)
    print(f"\n--- Phase 2: Spawning Child Branches (25 branches) ---")
    for config in configs[20:45]:
        parent = random.choice(branches[:10])  # Select from first 10
        child = create_branch(config, depth=1, parent_id=parent.branch_id)
        branches.append(child)
        print(f"  Created: {child.name} (child of {parent.name})")
    
    # Mirror round 2
    print(f"\n--- Mirror Round 2: Deeper Reflections ---")
    reflections2 = run_mirror_round(branches[20:], 2)
    print(f"  Generated {len(reflections2)} reflections")
    
    # Phase 3: Continue spawning (remaining branches)
    print(f"\n--- Phase 3: Continued Expansion (32 branches) ---")
    for config in configs[45:]:
        parent = random.choice(branches)
        child = create_branch(config, depth=parent.depth + 1, parent_id=parent.branch_id)
        branches.append(child)
        print(f"  Created: {child.name} (depth {child.depth})")
    
    # Mirror round 3 (final)
    print(f"\n--- Mirror Round 3: Final Synthesis ---")
    reflections3 = run_mirror_round(branches[45:], 3)
    print(f"  Generated {len(reflections3)} reflections")
    
    # Aggregate results
    print(f"\n{'='*70}")
    print(f"FINAL RESULTS: {len(branches)} branches, {len(reflections1)+len(reflections2)+len(reflections3)} reflections")
    print(f"{'='*70}")
    
    # Score aggregation
    scores_by_config = defaultdict(lambda: {"atlas": [], "judge": [], "socrates": []})
    
    for branch in branches:
        name_base = branch.name.rsplit("-v", 1)[0] if "-v" in branch.name else branch.name
        scores_by_config[name_base]["atlas"].append(branch.evaluations["atlas"]["overall"])
        scores_by_config[name_base]["judge"].append(branch.evaluations["judge"]["overall"])
        scores_by_config[name_base]["socrates"].append(branch.evaluations["socrates"].get("philosophical_score", 0.7))
    
    # Print rankings
    print(f"\nRankings by Configuration:")
    print(f"{'Config':<25} {'Atlas':<8} {'Judge':<8} {'Socrates':<8} {'Avg':<8}")
    print("-" * 60)
    
    rankings = []
    for name, scores in scores_by_config.items():
        avg_atlas = sum(scores["atlas"]) / len(scores["atlas"])
        avg_judge = sum(scores["judge"]) / len(scores["judge"])
        avg_socrates = sum(scores["socrates"]) / len(scores["socrates"])
        overall = (avg_atlas + avg_judge + avg_socrates) / 3
        rankings.append((name, avg_atlas, avg_judge, avg_socrates, overall))
    
    rankings.sort(key=lambda x: x[4], reverse=True)
    
    for name, atlas, judge, socrates, overall in rankings[:10]:
        print(f"{name:<25} {atlas:.3f}    {judge:.3f}    {socrates:.3f}    {overall:.3f}")
    
    # Save final results
    final_results = {
        "total_branches": len(branches),
        "total_reflections": len(reflections1) + len(reflections2) + len(reflections3),
        "rankings": [
            {"config": n, "atlas": a, "judge": j, "socrates": s, "overall": o}
            for n, a, j, s, o in rankings
        ],
        "timestamp": datetime.now().isoformat(),
    }
    
    with open(SIM_DIR / "final_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\nResults saved to {SIM_DIR / 'final_results.json'}")
    
    return final_results

if __name__ == "__main__":
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 77
    run_simulation(target)
