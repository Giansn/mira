# Atlas Offline Experiments

Private, offline-first sandbox for Mira's own projects. Zero API cost.

## Rules
- OFFLINE=1 always unless explicitly overridden
- No external API calls
- All outputs audit-only (no memory log leakage)
- Git-tracked, versioned, rollback-friendly

## How to run
```bash
cd ~/.openclaw/workspace/projects/atlas-offline-experiments
export OFFLINE=1
python3 sim_env/run_pipeline.py
```

## Structure
- sim_env/ — pipeline, mirror, policy, risk, mocks
- output/ — audit trail, memory log, insights
- AEAP/ — config and briefings
- references/ — patterns, briefings, docs
