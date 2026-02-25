---
name: causal-analyst
description: Seed-driven analysis of exec-approval flow: safe vs sensitive, with per-seed outcomes and summary metrics; optionally integrate with Telegram approvals.
user-invocable: true
---

# Causal Analyst Skill

Seed-driven causal analysis of the OpenClaw exec approval flow. Returns per-seed outcomes for a set of commands and a compact summary suitable for visualization.

## How it works
- Accepts a command and a list of seeds. For each seed, resets RNG state, classifies the command into SAFE/SENSITIVE/BLOCKED, and simulates an approval decision for SENSITIVE commands.
- Produces per-seed outcomes and a summary across seeds.
- Outputs JSON-friendly data for downstream plotting or dashboards.

## Interfaces
- /analyze --command "<cmd>" --seeds <seed1 seed2 ...>
- /simulate --commands "<cmd>" --seeds <seed1 seed2 ...> --count <n>
- /report --seed <seed> (optional)

## Data model (high level)
- seed: integer
- command: string
- tier: SAFE | SENSITIVE | BLOCKED
- executed: boolean
- status: ran | denied | timeout | blocked
- decision (for SENSITIVE): approved|denied|timeout
- output: string (simulated output if executed)

## Outputs
- Per-seed results
- Aggregate stats: counts by tier, approvals/denials/timeouts for SENSITIVE, blocked
- JSON payload ready for visualization

## Notes
- This MVP uses deterministic seeds for reproducibility. Adjust the random seed to explore different outcomes.
