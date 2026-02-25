# Causal Analyst — Tasks (High-Level)

## Phase 4: ClawHub Publishing + UX Polish

### P4.1 — Packaging
- [ ] Finalize SKILL.md (name, description, triggers, interface spec)
- [ ] Write README.md (usage, examples, output format)
- [ ] Add LICENSE if publishing publicly later

### P4.2 — UX Polish
- [ ] Improve CLI help/usage text
- [ ] Validate seed/command inputs with clear error messages
- [ ] Add --quiet and --verbose flags
- [ ] Color/formatting for terminal output (optional)

### P4.3 — Test Harness
- [ ] Generate sample dry_run.json from default seeds/commands
- [ ] Generate sample stats output
- [ ] Generate sample mirror_trace.log
- [ ] Add a run-tests.sh that validates output schema

### P4.4 — ClawHub Prep (deferred — private until finetuned)
- [ ] clawhub publish dry-run
- [ ] Review metadata and description
- [ ] Publish when ready

## Backlog / Future
- [ ] Expand seed library (more edge-case commands)
- [ ] Configurable tier thresholds via config file
- [ ] Integration tests against live OpenClaw gateway
- [ ] Mirror-layer self-critique quality metrics
