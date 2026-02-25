# Claude Briefing — Phase 4 Atlas MVP (OpenClaw)

Overview
- Phase 4 private MVP (Atlas) in OpenClaw is a seed-driven analysis engine with a mirror layer, audit trail, and redacted memory log. The current trajectory aligns with a modular, multi-agent style architecture where an orchestrator (SimEnv Controller) sequences phases (packaging, UX, tests), and a separate MirrorAgent provides one-pass critique.

Context & Goals
- Goal: validate core Phase 4 flows, ensure reproducibility, and establish guardrails for safe experimentation. Prepare for future policy integration, metrics, and UI polish.
- Primary deliverables: deterministic Run objects, audit trail, memory log (redacted), and a compact, pluggable pattern set (atlas-patterns.md).

Phase 4 MVP Scope (core elements)
- SimEnv Controller: sequences phases for each seed/command pair.
- Run object: immutable record with fields: run_id, timestamp, seed, command, tier, decision, status, executed, elapsed_ms, mirror_trace, prev_hash, hash, schema_version.
- Whitelisted surface: only allowed commands per tier (SAFE/SENSITIVE/BLOCKED).
- Audit Trail: append-only log of Run objects with hash-chain integrity.
- Memory Log (redacted): derived from audit trail, redact sensitive fields.
- Mirror (one-pass): critique and risk flags; attaches to Run as mirror_trace.
- Pattern anchors: atlas-patterns.md ties Atlas patterns to MVP components.

Phase 4 Patterns & References
- Atlas Pattern Mappings: atlas-patterns.md (patterns -> components, interface contracts for phase_hooks, MirrorAgent, etc.).
- Atlas Briefing: atlas-briefing.md (detailed rationale and integration guidance).
- Architecture: architecture.md (private integration of Atlas patterns).

Data Model Snapshot (Run)
- Required fields: run_id (UUID), timestamp (ISO8601 UTC), seed (int), command (string), tier (SAFE|SENSITIVE|BLOCKED), decision (GRANTED|DENIED|TIMEOUT|null), status (ran|denied|timeout|blocked), executed (bool), elapsed_ms (int), mirror_trace (object), prev_hash (string, 64 hex), hash (string, 64 hex), schema_version (e.g., v1.0).
- Mirror trace fields: reasoning (string), risk_flags (array), confidence (0.0–1.0), alternative_action (string|null).
- Hash chain: prev_hash links to previous run; hash is a hash of the run payload (excluding hash).

What to implement next (Claude tasks)
- Implement Atlas patterns per atlas-patterns.md and ensure alignment with MVP components.
- Add a Phase 4 private governance doc (atlas-governance.md).
- Expand sim_env/orchestrator_skeleton.py to emit Run objects using RunBuilder (as a canonical MVP; hooks for phase_hooks).
- Wire MirrorAgent interface (evaluate) and a minimal MirrorTrace producer.
- Add reflect() prototype for periodic memory insights (phase 1 MVP upgrade).

Key References (fast access)
- atlas-patterns.md: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/atlas-patterns.md
- atlas-briefing.md: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/atlas-briefing.md
- architecture.md: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/architecture.md
- run.schema.json: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/run.schema.json
- run.example.json: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/run.example.json
- mvp-test-plan.md: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/mvp-test-plan.md
- memory-log-contract.md: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/memory-log-contract.md
- hash-chain.md: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/references/hash-chain.md
- sim_env/orchestrator_skeleton.py: /home/ubuntu/.openclaw/workspace/skills/causal-analyst/sim_env/orchestrator_skeleton.py

Notes for Claude
- Treat Run objects as a contract between components; ensure deterministic replay with a stable hash chain.
- Keep memory redaction strict; only share what is necessary for auditing and learning.
- Progressively introduce guardrails (policy rules) and reflectors to avoid persona drift and bias.
- Use atlas-patterns.md as the single source of truth for architectural pattern mappings.

If you want, I can export this briefing as a Markdown file into the workspace and also attach a compact one-page TL;DR. Also happy to tailor the tone and depth to your preference.