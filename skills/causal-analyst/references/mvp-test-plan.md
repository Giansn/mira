# MVP Test Plan (Phase 4)

Target
- Validate P0/P1 core behavior: determinism, safe-surface gating, auditability, and mirror constraints.

Test sets
- Seeds: [123, 999, 555, 777]
- Commands:
  - SAFE: ls, df, free
  - SENSITIVE: bash stats.sh, curl, systemctl restart, openclaw config set, docker rm
  - BLOCKED: mv /etc, rm -rf /, dd, shutdown

Unit tests (P0)
- Schema validation
  - Run object validates against run.schema.json
- Tier classification
  - Each command maps to the expected tier
  - Unknown command defaults to BLOCKED
- Decision logic
  - SAFE -> decision=null, status=ran, executed=true
  - BLOCKED -> status=blocked, executed=false
  - SENSITIVE -> requires policy; default DENIED for underspecified commands (e.g., bare curl)
- Deterministic replay
  - Same seeds/commands/config -> byte-identical audit log output

Integration tests (P1)
- Mirror constraints
  - Mirror runs exactly once per run
  - Mirror outputs risk_flags from allowed vocabulary
  - reasoning length cap enforced for memory log
- Hash chain integrity
  - Validate hash chain for a multi-line audit file
  - Detect tampering (edit line N) -> chain fails at N
- Memory log redaction
  - Seeds/commands not present raw
  - command_preview only for SAFE

Negative tests
- Timeout path
  - Inject simulated timeout -> status=timeout, decision=TIMEOUT, executed=false
- Partial failure
  - One command fails -> batch continues, audit entries still written for completed runs

Exit criteria
- All P0 unit tests pass.
- Integration tests pass for mirror + hash chain + redaction.
- Determinism test passes twice in a row.
