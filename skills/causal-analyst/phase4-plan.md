# Phase 4 — Packaging, UX, Testing, and ClawHub Prep (Private, no public publishing yet)

Objective
- Finish packaging and user experience improvements for the Causal Analyst MVP (Atlas) and prepare private publication metadata for ClawHub when ready.
- Validate test harness integration and ensure reproducible results.
- Establish a controlled, auditable path toward eventual public publishing (private-first stance).

Deliverables
- Finalized packaging artifacts: SKILL.md, README.md, LICENSE (as applicable)
- UX improvements documented and implemented in CLI (help text, error messages, flags)
- Completed Phase 4 test harness integration and runbook
- Private publication metadata draft for ClawHub (not public yet)

Milestones
- M1: Phase4 plan finalized
- M2: Packaging artifacts ready
- M3: UX improvements implemented
- M4: Test harness complete and validated
- M5: ClawHub prep metadata draft

Dependencies
- Access to workspace/docs and local repository for publishing metadata
- Phase 3 artifacts (plan.md, tasks.md, test harness) as input

Planned Tasks
- T4.1 Packaging: finalize SKILL.md, README.md, and license notes
- T4.2 UX Polish: improve CLI usage/help, add --quiet/--verbose, consistent error handling
- T4.3 Test Harness Harden: extend dry_run.json and mirror_trace with more edge cases; add run-tests.sh
- T4.4 ClawHub Prep: draft private clawhub-metadata.json and publishing plan; do not publish yet
- T4.5 Documentation: update phase4-plan.md and related docs with progress updates

Success Criteria
- All Phase 4 artifacts exist and are self-contained; verification scripts pass; no leakage of secrets
- Phase 4 metadata ready for a private publish workflow
