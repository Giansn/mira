#!/usr/bin/env python3
"""
Sim-Runner: Spawn alternative reasoning branches
Usage: python3 sim_runner.py <branch_id> <context> <question> <strategy>
"""

import sys
import json
sys.path.insert(0, "/home/ubuntu/.openclaw/workspace")

from simulations.self_sim import branch, resolve_branch, SIM_DIR
from pathlib import Path

STRATEGIES = {
    "default": "Respond normally, as you normally would.",
    "devil_advocate": "Argue the opposite of what you would normally say. Challenge assumptions.",
    "conservative": "Give the shortest, safest, most conservative answer possible.",
    "creative": "Be as creative, witty, and unexpected as possible.",
    "expert": "Respond as if you're an expert deep in thought - thorough, precise, nuanced.",
}

def main(branch_id, context, question, strategy="default"):
    strategy_prompt = STRATEGIES.get(strategy, STRATEGIES["default"])
    
    # Log the branch
    branch(branch_id, context, question, strategy)
    
    print(f"Branch '{branch_id}' created with strategy: {strategy}")
    print(f"Strategy: {strategy_prompt}")
    print(f"Context: {context[:200]}...")
    print(f"Question: {question[:200]}...")
    print(f"\nTo resolve: python3 sim_runner.py resolve {branch_id} <outcome> <learnings>")
    
    # Return the prompt for this branch (to be used by a sub-agent)
    return {
        "branch_id": branch_id,
        "strategy": strategy,
        "prompt": f"{strategy_prompt}\n\nContext: {context}\n\nQuestion: {question}\n\nRespond to the question using the {strategy} strategy.",
    }

def resolve(branch_id, outcome, learnings=""):
    resolve_branch(branch_id, outcome, learnings)
    print(f"Branch '{branch_id}' resolved: {outcome}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 sim_runner.py <branch_id> <context> <question> <strategy>")
        print("  python3 sim_runner.py resolve <branch_id> <outcome> <learnings>")
        sys.exit(1)
    
    if sys.argv[1] == "resolve":
        resolve(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else:
        branch_id = sys.argv[1]
        context = sys.argv[2] if len(sys.argv) > 2 else ""
        question = sys.argv[3] if len(sys.argv) > 3 else ""
        strategy = sys.argv[4] if len(sys.argv) > 4 else "default"
        result = main(branch_id, context, question, strategy)
        print("\n--- Prompt for sub-agent ---")
        print(result["prompt"])
