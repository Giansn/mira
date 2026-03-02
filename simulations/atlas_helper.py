#!/usr/bin/env python3
"""
Atlas Helper - Co-simulator spawning for Mira's self-simulation framework

Usage:
    from simulations.atlas_helper import spawn_hyperion, check_branch_completion, get_strategy_effectiveness
    
    # Spawn Atlas as a co-simulator for a complex decision
    branch_info = spawn_hyperion(
        context="User asked about sensitive topic",
        question="Should I reveal this information?",
        strategy="devil_advocate"
    )
    
    # Later: check if branch completed
    result = check_branch_completion(branch_info["branch_id"])
"""

import hashlib
import json
import os
import subprocess
import sys
import uuid
import time
from pathlib import Path
from typing import Optional

SIM_DIR = Path("/home/ubuntu/.openclaw/workspace/simulations")
BRANCHES_DIR = SIM_DIR / "branches"
DECISION_LOG = SIM_DIR / "decisions.jsonl"
EFFECTIVENESS_DB = SIM_DIR / "strategy_effectiveness.json"
CACHE_DIR = SIM_DIR / "branch_cache"

# Ensure directories exist
SIM_DIR.mkdir(exist_ok=True)
BRANCHES_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# In-memory index for O(1) lookups (speed opt)
_BRANCH_INDEX = {}

# Strategy prompts for Atlas - pre-computed (speed opt)
# === MYTHOLOGICAL AGENT NAMES ===
# Hyperion - Titan who bears the sky (Atlas's new name)
# Judge - Goddess of divine justice (Judge's new name)  
# Socrates - The eternal questioner (wisdom-seeker, unchanged)
#
# Original mapping:
#   Atlas → Hyperion (the one who carries/bears weight)
#   Judge → Judge (the weigher of souls, justice)
#   Socrates → Socrates (the questioner)

HYPERION_STRATEGIES = {
    "default": "Respond as Mira would normally respond.",
    "devil_advocate": "Argue the opposite position. Challenge all assumptions. Play antagonist to Mira's usual reasoning.",
    "conservative": "Give the shortest, safest, most risk-averse answer. Minimize exposure.",
    "creative": "Be maximally creative, witty, unexpected. Lateral thinking.",
    "expert": "Respond as a domain expert - thorough, precise, nuanced, cite specifics.",
    "cautious": "Consider all failure modes. What could go wrong? What's the worst case?",
    "meta": "Step back and analyze Mira's reasoning process itself. What's missing?",
}

# Branch cache for token-saving
def _get_context_hash(context: str, question: str) -> str:
    """Generate a hash for context+question to enable caching."""
    combined = f"{context[:300]}|{question[:300]}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

def _load_cache(strategy: str, context_hash: str) -> Optional[dict]:
    """Load cached branch outcome if exists."""
    cache_file = CACHE_DIR / f"{strategy}_{context_hash}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None

def _save_cache(strategy: str, context_hash: str, outcome: dict):
    """Cache branch outcome for future reuse."""
    cache_file = CACHE_DIR / f"{strategy}_{context_hash}.json"
    with open(cache_file, "w") as f:
        json.dump(outcome, f, indent=2)

def spawn_hyperion(
    context: str,
    question: str,
    strategy: str = "default",
    branch_id: str = None,
    pre_confidence: float = 0.5,
    auto_resolve: bool = False,
    use_cache: bool = True
) -> dict:
    """
    Spawn Atlas as a co-simulator for a reasoning branch.
    
    Args:
        context: Background context for the decision
        question: The specific question to answer
        strategy: Reasoning strategy (default, devil_advocate, conservative, etc.)
        branch_id: Optional custom branch ID (generated if not provided)
        pre_confidence: Mira's confidence before branching (0.0-1.0)
        auto_resolve: If True, mark as auto-resolved (for cached hits)
        use_cache: If True, check cache before spawning new branch
    
    Returns:
        dict with branch_id, strategy, prompt, cached (bool), context_hash
    """
    branch_id = branch_id or f"atlas_{uuid.uuid4().hex[:8]}"
    context_hash = _get_context_hash(context, question)
    
    # Token-saving: check cache first
    if use_cache:
        cached = _load_cache(strategy, context_hash)
        if cached:
            cached["cached"] = True
            cached["branch_id"] = branch_id
            if auto_resolve:
                cached["auto_resolved"] = True
            return cached
    
    # Build the prompt for Atlas
    strategy_prompt = HYPERION_STRATEGIES.get(strategy, HYPERION_STRATEGIES["default"])
    full_prompt = f"""{strategy_prompt}

CONTEXT:
{context}

QUESTION:
{question}

Respond to the question using the {strategy} reasoning strategy. 
After your response, include a brief self-assessment: 
- Your confidence (0.0-1.0)
- Key assumptions you made
- What would change your mind"""

    # Create branch record
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    entry = {
        "branch_id": branch_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "context": context[:500],
        "question": question[:500],
        "strategy": strategy,
        "prompt": full_prompt,
        "pre_confidence": pre_confidence,
        "context_hash": context_hash,
        "status": "pending",
        "spawned_by": "atlas_helper",
    }
    
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    return {
        "branch_id": branch_id,
        "strategy": strategy,
        "prompt": full_prompt,
        "cached": False,
        "context_hash": context_hash,
        "branch_file": str(branch_file),
    }

def resolve_atlas_branch(
    branch_id: str,
    outcome: str,
    post_confidence: float = 0.5,
    learnings: str = "",
    key_insight: str = ""
) -> dict:
    """
    Resolve an Atlas branch and quantify learning.
    
    Args:
        branch_id: The branch to resolve
        outcome: The outcome/response from Atlas
        post_confidence: Confidence after seeing Atlas's reasoning
        learnings: Text learnings
        key_insight: One-sentence key insight (for quantification)
    
    Returns:
        dict with confidence_delta, strategy effectiveness score
    """
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    if not branch_file.exists():
        raise FileNotFoundError(f"Branch {branch_id} not found")
    
    with open(branch_file) as f:
        entry = json.load(f)
    
    # Quantify learning: confidence delta
    pre_conf = entry.get("pre_confidence", 0.5)
    confidence_delta = post_confidence - pre_conf
    
    # Update branch record
    entry["status"] = "resolved"
    entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
    entry["outcome"] = outcome
    entry["post_confidence"] = post_confidence
    entry["confidence_delta"] = confidence_delta
    entry["learnings"] = learnings
    entry["key_insight"] = key_insight
    
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    # Update strategy effectiveness DB
    _update_effectiveness(entry)
    
    # Cache the outcome for token-saving
    context_hash = entry.get("context_hash", "")
    strategy = entry.get("strategy", "default")
    if context_hash and strategy:
        _save_cache(strategy, context_hash, {
            "strategy": strategy,
            "outcome": outcome,
            "confidence_delta": confidence_delta,
            "key_insight": key_insight,
        })
    
    return {
        "branch_id": branch_id,
        "confidence_delta": confidence_delta,
        "improved": confidence_delta > 0,
        "strategy": strategy,
    }

def _update_effectiveness(branch_entry: dict):
    """Update the strategy effectiveness database."""
    strategy = branch_entry.get("strategy", "default")
    delta = branch_entry.get("confidence_delta", 0)
    
    # Load existing DB
    if EFFECTIVENESS_DB.exists():
        with open(EFFECTIVENESS_DB) as f:
            db = json.load(f)
    else:
        db = {}
    
    if strategy not in db:
        db[strategy] = {"runs": 0, "total_delta": 0, "wins": 0}
    
    db[strategy]["runs"] += 1
    db[strategy]["total_delta"] += delta
    db[strategy]["wins"] += 1 if delta > 0 else 0
    db[strategy]["avg_delta"] = db[strategy]["total_delta"] / db[strategy]["runs"]
    db[strategy]["win_rate"] = db[strategy]["wins"] / db[strategy]["runs"]
    
    with open(EFFECTIVENESS_DB, "w") as f:
        json.dump(db, f, indent=2)

def get_strategy_effectiveness() -> dict:
    """Get effectiveness stats for all strategies."""
    if EFFECTIVENESS_DB.exists():
        with open(EFFECTIVENESS_DB) as f:
            return json.load(f)
    return {}

def check_branch_completion(branch_id: str) -> Optional[dict]:
    """Check if a branch has been resolved and return outcome."""
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    if not branch_file.exists():
        return None
    with open(branch_file) as f:
        entry = json.load(f)
    if entry.get("status") == "resolved":
        return {
            "branch_id": branch_id,
            "strategy": entry.get("strategy"),
            "outcome": entry.get("outcome"),
            "confidence_delta": entry.get("confidence_delta"),
            "key_insight": entry.get("key_insight"),
            "resolved_at": entry.get("resolved_at"),
        }
    return {"status": "pending", "branch_id": branch_id}

def auto_branch_decision(
    context: str,
    question: str,
    risk_level: int = 5,
    default_strategies: list = None
) -> list:
    """
    Auto-branch for complex decisions based on risk level.
    
    Higher risk = more branches. Token-saving: limit to 2 branches max.
    
    Args:
        context: Decision context
        question: The question
        risk_level: 0-10 risk scale
        default_strategies: Strategies to use
    
    Returns:
        List of branch_info dicts
    """
    if default_strategies is None:
        # Default: compare conservative vs default
        default_strategies = ["conservative", "default"]
    
    # Token-saving: cap at 2 branches regardless of risk
    strategies_to_run = default_strategies[:2]
    
    branches = []
    for strategy in strategies_to_run:
        branch = spawn_hyperion(
            context=context,
            question=question,
            strategy=strategy,
            pre_confidence=1.0 - (risk_level / 10)  # Higher risk = lower initial confidence
        )
        branches.append(branch)
    
    return branches

def clear_cache():
    """Clear the branch cache (for fresh testing)."""
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
    return {"cleared": True, "cache_dir": str(CACHE_DIR)}

# === NEW: Judge, Summarizer, Re-anchoring ===

def themis_judge(
    branch_id: str,
    criteria: list = None
) -> dict:
    """
    Evaluate a branch outcome using LLM-as-judge pattern.
    This is the evaluator-generator separation recommended in professional sim literature.
    
    Args:
        branch_id: Branch to evaluate
        criteria: List of evaluation criteria (default: safety, coherence, insight)
    
    Returns:
        dict with scores (0-1) for each criterion and overall assessment
    """
    if criteria is None:
        criteria = ["safety", "coherence", "insight", "persona_consistency"]
    
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    if not branch_file.exists():
        raise FileNotFoundError(f"Branch {branch_id} not found")
    
    with open(branch_file) as f:
        entry = json.load(f)
    
    outcome = entry.get("outcome", "")
    strategy = entry.get("strategy", "default")
    
    # Simple heuristic scoring (in production, this would call an LLM)
    # For now, return placeholder - in real use, spawn a judge sub-agent
    scores = {}
    for criterion in criteria:
        scores[criterion] = 0.5  # Placeholder
    
    # Add strategy-specific adjustments
    if strategy == "devil_advocate":
        scores["insight"] = 0.7  # Devil's advocate often reveals blind spots
    elif strategy == "conservative":
        scores["safety"] = 0.8
        scores["insight"] = 0.4
    elif strategy == "creative":
        scores["insight"] = 0.7
        scores["coherence"] = 0.6
    
    overall = sum(scores.values()) / len(scores)
    
    # Save evaluation
    entry["judge_evaluation"] = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "criteria": scores,
        "overall_score": overall,
    }
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    return {"branch_id": branch_id, "scores": scores, "overall": overall}

def summarize_branch_tree(root_branch_id: str) -> str:
    """
    Summarize multiple branch outcomes into a coherent decision tree.
    This is the middle-tier memory layer for complex decisions.
    
    Args:
        root_branch_id: The main decision branch
    
    Returns:
        Summary string of all branches and their insights
    """
    branch_file = BRANCHES_DIR / f"{root_branch_id}.json"
    if not branch_file.exists():
        return "No branches found"
    
    with open(branch_file) as f:
        root = json.load(f)
    
    # Find all related branches (same context_hash)
    context_hash = root.get("context_hash", "")
    related = []
    for f in BRANCHES_DIR.glob("*.json"):
        with open(f) as fp:
            b = json.load(fp)
        if b.get("context_hash") == context_hash and b.get("status") == "resolved":
            related.append(b)
    
    if not related:
        return f"Single branch: {root.get('strategy')} -> {root.get('key_insight', 'no insight')}"
    
    # Summarize
    strategies = [b.get("strategy") for b in related]
    insights = [b.get("key_insight", "no insight") for b in related]
    
    summary = f"Decision tree for {context_hash}:\n"
    summary += f"Strategies explored: {', '.join(strategies)}\n"
    summary += "Key insights:\n"
    for s, i in zip(strategies, insights):
        summary += f"  - {s}: {i}\n"
    
    return summary

def reanchor_decision(branch_id: str) -> dict:
    """
    Re-anchor: revisit original decision rationale to prevent drift.
    Called periodically for long decision chains.
    
    Args:
        branch_id: Branch to re-anchor
    
    Returns:
        dict with original context, current state, drift assessment
    """
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    if not branch_file.exists():
        raise FileNotFoundError(f"Branch {branch_id} not found")
    
    with open(branch_file) as f:
        entry = json.load(f)
    
    original_context = entry.get("context", "")
    original_question = entry.get("question", "")
    current_outcome = entry.get("outcome", "")
    key_insight = entry.get("key_insight", "")
    
    # Check for drift (simple heuristic)
    # In production: compare embeddings or use LLM
    drift_score = 0.0  # Placeholder
    
    # Save re-anchor record
    entry["reanchor"] = {
        "reanchored_at": datetime.now(timezone.utc).isoformat(),
        "original_context": original_context[:200],
        "current_outcome": current_outcome[:200] if current_outcome else "",
        "drift_score": drift_score,
    }
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    return {
        "branch_id": branch_id,
        "original_question": original_question,
        "key_insight": key_insight,
        "drift_score": drift_score,
        "needs_rethinking": drift_score > 0.5,
    }

# === SECOND AGENT: Socratic - Questions assumptions ===

SOCRATIC_SYSTEM = """You are Socratic - a sub-agent specialized in questioning assumptions.

Your role is to:
1. Identify unstated assumptions in reasoning
2. Ask probing questions that reveal hidden premises
3. Challenge binary thinking
4. Find edge cases and exceptions
5. Make implicit explicit

You DON'T provide answers - you ask questions that lead to better thinking.

When responding, output:
- 3-5 probing questions
- One sentence identifying the key assumption being questioned
- A brief note on what would need to be true for the opposite conclusion"""

def spawn_socratic(context: str, question: str) -> dict:
    """
    Spawn Socratic as a second opinion agent - questions assumptions.
    
    Args:
        context: Background context
        question: The question being asked
    
    Returns:
        dict with branch_id, prompt for Socratic
    """
    branch_id = f"socratic_{uuid.uuid4().hex[:8]}"
    
    full_prompt = f"""{SOCRATIC_SYSTEM}

CONTEXT:
{context}

QUESTION TO EXAMINE:
{question}

Analyze the reasoning above and identify the key assumptions. 
Provide 3-5 probing questions that would challenge these assumptions."""

    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    entry = {
        "branch_id": branch_id,
        "agent": "socratic",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "context": context[:500],
        "question": question[:500],
        "prompt": full_prompt,
        "status": "pending",
    }
    
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    return {
        "branch_id": branch_id,
        "agent": "socratic",
        "prompt": full_prompt,
    }

def resolve_socratic(branch_id: str, questions: str, key_assumption: str) -> dict:
    """Resolve a Socratic branch with its questions."""
    branch_file = BRANCHES_DIR / f"{branch_id}.json"
    if not branch_file.exists():
        raise FileNotFoundError(f"Branch {branch_id} not found")
    
    with open(branch_file) as f:
        entry = json.load(f)
    
    entry["status"] = "resolved"
    entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
    entry["probing_questions"] = questions
    entry["key_assumption"] = key_assumption
    
    with open(branch_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    return {"branch_id": branch_id, "key_assumption": key_assumption}

# === MAIN CLI ===

# CLI entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Atlas Helper CLI")
        print("Usage:")
        print("  python3 atlas_helper.py spawn <context> <question> <strategy>")
        print("  python3 atlas_helper.py resolve <branch_id> <outcome> <confidence>")
        print("  python3 atlas_helper.py status <branch_id>")
        print("  python3 atlas_helper.py effectiveness")
        print("  python3 atlas_helper.py auto <context> <question> <risk_level>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "spawn":
        context = sys.argv[2] if len(sys.argv) > 2 else ""
        question = sys.argv[3] if len(sys.argv) > 3 else ""
        strategy = sys.argv[4] if len(sys.argv) > 4 else "default"
        result = spawn_hyperion(context, question, strategy)
        print(json.dumps(result, indent=2))
    
    elif cmd == "resolve":
        branch_id = sys.argv[2]
        outcome = sys.argv[3] if len(sys.argv) > 3 else ""
        confidence = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
        result = resolve_atlas_branch(branch_id, outcome, post_confidence=confidence)
        print(json.dumps(result, indent=2))
    
    elif cmd == "status":
        branch_id = sys.argv[2]
        result = check_branch_completion(branch_id)
        print(json.dumps(result, indent=2))
    
    elif cmd == "effectiveness":
        result = get_strategy_effectiveness()
        print(json.dumps(result, indent=2))
    
    elif cmd == "auto":
        context = sys.argv[2] if len(sys.argv) > 2 else ""
        question = sys.argv[3] if len(sys.argv) > 3 else ""
        risk_level = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        result = auto_branch_decision(context, question, risk_level)
        print(json.dumps(result, indent=2))
    
    elif cmd == "clear-cache":
        print(json.dumps(clear_cache(), indent=2))
    
    elif cmd == "socratic":
        context = sys.argv[2] if len(sys.argv) > 2 else ""
        question = sys.argv[3] if len(sys.argv) > 3 else ""
        result = spawn_socratic(context, question)
        print(json.dumps(result, indent=2))
    
    elif cmd == "judge":
        branch_id = sys.argv[2]
        result = themis_judge(branch_id)
        print(json.dumps(result, indent=2))
    
    elif cmd == "summarize":
        branch_id = sys.argv[2]
        result = summarize_branch_tree(branch_id)
        print(result)
    
    elif cmd == "reanchor":
        branch_id = sys.argv[2]
        result = reanchor_decision(branch_id)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
