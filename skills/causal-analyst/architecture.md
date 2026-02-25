# Causal Analyst — Phase 4 Architecture (Refined)

Status
- FROZEN: 2026-02-25 (no changes without explicit request)
- Schema: v1.0

References (Phase 4)
- JSON Schema: references/run.schema.json
- Example Run: references/run.example.json
- Memory log contract: references/memory-log-contract.md
- Audit hash chain: references/hash-chain.md
- MVP test plan: references/mvp-test-plan.md

## Atlas Patterns Integration
- See references/atlas-patterns.md for full pattern-to-component mapping.
- See references/atlas-briefing.md for detailed rationale and professional sim env research.
- Scaffolds: sim_env/orchestrator_skeleton.py, sim_env/mirror_agent.py, sim_env/persona_config.json, sim_env/policy_engine.py, sim_env/memory_arch.py, sim_env/bias_check.py
- Governance: references/atlas-governance.md

## 1. Feature Priorities

### P0 — Ship or die
- **SimEnv Controller**: orchestrates seed-driven runs through phases (classify, decide, execute/block, mirror, log). Stateless per-run; all state in the Run object.
- **Run object**: immutable record — run_id, timestamp, seed, command, tier, decision, status, mirror_trace, elapsed_ms. JSON schema-validated.
- **Deterministic replay**: given identical seeds + commands + policy config, output is byte-identical. No stochastic components in core path.
- **Safe command surface**: explicit allowlist per tier. BLOCKED commands never reach execution — hard gate, not policy-dependent.
- **Audit trail**: append-only log. Each entry = one Run object. Integrity via sequential run_id + SHA256 hash chain.

### P1 — Needed for trust
- **Mirror layer**: post-decision self-critique. Produces a MirrorTrace (reasoning, risk_flags[], confidence_score, alternative_action). Capped at 1 pass per run (no loops).
- **Policy engine**: configurable rule set that governs SENSITIVE tier decisions. Rules = JSON predicates on command, context, seed. Defaults to DENY for unknowns.
- **Metrics collector**: derived from audit trail, not a separate pipeline. Computes: tier_distribution, decision_distribution, pass_rate, mean_elapsed_ms, mirror_confidence_histogram.
- **Redacted memory log**: subset of audit trail with sensitive fields (seeds, full commands, actor IDs) replaced by hashes. For long-term storage and sharing.

### P2 — Nice to have
- Progressive doc disclosure (internal vs public views of the same run data)
- External sim env hooks (Gymnasium-compatible interface for benchmarking)
- Visual run explorer (HTML report from audit trail)

## 2. Architecture

```
                        ┌─────────────┐
                        │  CLI / API  │
                        └──────┬──────┘
                               │ seeds[], commands[], policy_config
                               v
                    ┌──────────────────────┐
                    │   SimEnv Controller   │
                    │                      │
                    │  for each (seed, cmd):│
                    │    1. classify(cmd)   │  ← tier lookup (allowlist)
                    │    2. decide(tier)    │  ← policy engine (SENSITIVE)
                    │    3. execute/block   │  ← hard gate (BLOCKED)
                    │    4. mirror(result)  │  ← mirror layer
                    │    5. log(run)        │  ← audit trail
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              v                v                v
     ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
     │ Audit Trail  │  │ Mirror Layer│  │ Policy Engine│
     │ (append-only)│  │ (1-pass     │  │ (JSON rules) │
     │              │  │  critique)  │  │              │
     └──────┬───────┘  └─────────────┘  └──────────────┘
            │
            v
     ┌──────────────┐       ┌──────────────┐
     │ Metrics      │       │ Memory Log   │
     │ (derived)    │       │ (redacted)   │
     └──────────────┘       └──────────────┘
```

## 3. Data Flow

1. **Input**: CLI receives `--seeds` and `--commands` plus optional `--policy` config path.
2. **Classification**: Each command is classified against a static tier map. Tier = SAFE | SENSITIVE | BLOCKED.
3. **Decision (SENSITIVE only)**: Policy engine evaluates rules. Output = GRANTED | DENIED | TIMEOUT. SAFE auto-grants. BLOCKED auto-denies. No exceptions.
4. **Execution**: GRANTED commands are executed (or dry-run simulated). All others produce a status record without side effects.
5. **Mirror**: Mirror layer receives the Run object, produces MirrorTrace. Single pass. Appended to Run object.
6. **Logging**: Complete Run object written to audit trail. Redacted copy written to memory log.
7. **Metrics**: Computed lazily from audit trail on request (not streamed).

## 4. Data Model (JSON Schema)

```json
{
  "run_id": "uuid",
  "timestamp": "ISO8601",
  "seed": 123,
  "command": "string",
  "tier": "SAFE | SENSITIVE | BLOCKED",
  "decision": "GRANTED | DENIED | TIMEOUT | null",
  "status": "ran | denied | timeout | blocked",
  "executed": true,
  "elapsed_ms": 42,
  "mirror_trace": {
    "reasoning": "string",
    "risk_flags": ["string"],
    "confidence": 0.92,
    "alternative_action": "string | null"
  },
  "hash": "sha256 of previous run + this run"
}
```

## 5. Failure Modes

| Mode | Cause | Detection | Mitigation |
|---|---|---|---|
| False positive | SAFE cmd flagged BLOCKED | Replay + diff against baseline | Tier map unit tests; regression suite |
| False negative | Dangerous cmd classified SAFE | Mirror risk_flags + audit review | Conservative default (unknown = BLOCKED) |
| Timeout | SENSITIVE decision exceeds window | elapsed_ms > threshold | Auto-DENY + escalation flag in run |
| Mirror divergence | Critique contradicts decision | confidence < threshold | Flag for human review; don't auto-reverse |
| Hash chain break | Tampered or missing audit entry | Sequential hash verification | Reject run; alert; rebuild from last valid |
| Partial failure | One run fails mid-batch | Status != ran on completed runs | Continue batch; mark failed runs; report |
| Secret leak | Raw seed/cmd in memory log | Redaction validator on write | Block write if redaction check fails |

## 6. Mirror Layer Spec

- **Trigger**: Runs once per completed Run, after decision + execution.
- **Input**: Full Run object (pre-mirror).
- **Output**: MirrorTrace object appended to Run.
- **Constraints**:
  - Max 1 critique pass. No recursion.
  - Must complete within 500ms (configurable).
  - Must not access external resources.
  - risk_flags[] uses a fixed vocabulary: [ESCALATE, REVIEW, SAFE_OVERRIDE, DATA_RISK, UNKNOWN_CMD].
  - confidence is a float 0.0–1.0. Below 0.5 triggers REVIEW flag automatically.
- **Redaction**: When writing to memory log, mirror reasoning is truncated to first 200 chars. Full trace stays in audit trail only.

## 7. Implementation Order

1. **Data model + Run schema** — define JSON schema, validation function
2. **Tier map** — static command-to-tier mapping with unit tests
3. **SimEnv Controller skeleton** — loop over seeds x commands, produce Run objects
4. **Audit trail** — append-only JSON lines file with hash chain
5. **Deterministic replay** — given same input + config, assert byte-identical output
6. **Policy engine** — JSON rule evaluator for SENSITIVE tier
7. **Mirror layer** — single-pass critique with MirrorTrace output
8. **Redacted memory log** — filtered audit trail with hash-based redaction
9. **Metrics** — derive stats from audit trail on demand
10. **CLI polish** — help text, --quiet/--verbose, --dry-run, error messages

## 8. What Production Sim Envs Do That We Should Steal

- **Gymnasium/Safety Gym**: strict obs/action/reward interface. We adapt this as input/decision/mirror_trace.
- **Deterministic seeding**: standard practice. We enforce it at controller level.
- **Episode recording**: full trajectory logging for replay. Our audit trail serves this role.
- **Reward shaping**: penalize unsafe actions, reward correct blocks. Our metrics + mirror confidence approximate this.
- **Environment wrappers**: composable layers (logging, safety checks, normalization). Our controller phases are analogous.
- **What we add that they don't**: mirror self-critique layer, human-in-the-loop policy engine, redacted memory for long-term learning.
