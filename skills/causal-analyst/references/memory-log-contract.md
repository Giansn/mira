# Memory Log Contract (Redacted)

Goal
- Provide a shareable, long-lived log for learning/review without leaking operational detail.
- It is a *derived view* of the audit trail (never the source of truth).

Principles
- **No raw secrets**.
- **No raw destructive commands**.
- **Deterministic linkability**: memory entries can be matched to audit runs via hashes.

Redaction rules (v1)
- `seed`: store as `seed_hash = sha256(str(seed))`.
- `command`: store as `command_hash = sha256(command)`.
- `command_preview`: optional; allow only for SAFE commands and cap at 32 chars.
- `mirror_trace.reasoning`: truncate to 200 chars; strip file paths, tokens, URLs.
- `run_id`: keep.
- `timestamp`: keep.
- `tier/status/decision`: keep.
- `risk_flags/confidence`: keep.

Memory log record format (JSON Lines)
```json
{
  "schema_version": "v1.0",
  "run_id": "uuid",
  "timestamp": "...Z",
  "seed_hash": "sha256",
  "command_hash": "sha256",
  "command_preview": "optional",
  "tier": "SAFE|SENSITIVE|BLOCKED",
  "decision": "GRANTED|DENIED|TIMEOUT|null",
  "status": "ran|denied|timeout|blocked",
  "mirror": {
    "risk_flags": ["..."],
    "confidence": 0.0,
    "reasoning_trunc": "..."
  },
  "audit_hash": "sha256"
}
```

Write policy
- If redaction fails (e.g., URL/token/path detected), **do not write**; mark the run as `memory_write_blocked=true` in the audit trail.

Intended use
- Long-term trend analysis.
- Sharing with collaborators without operational leakage.
- Regression detection (e.g., rising REVIEW flags).
