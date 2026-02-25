# Causal Analyst MVP Plan (Atlas)

Objective

Seed-driven analysis engine for OpenClaw exec approvals with mirror layer.

Data Model

- seed: int | command: string | tier: SAFE|SENSITIVE|BLOCKED
- executed: bool | status: ran|denied|timeout|blocked
- decision (SENSITIVE): GRANTED|DENIED|TIMEOUT
- mirror: reasoning trace + self-critique

Seeds & Commands

- Seeds: [123, 999, 555, 777]
- Commands: ls, df, free, bash stats.sh, curl, systemctl restart, openclaw config set, mv /etc, docker rm, rm -rf /, dd, shutdown

Interfaces

- CLI: --seeds and --commands
- Output: dry_run.json, stats, mirror trace log

Roadmap

- Phase 1: Baseline MVP (core + mirror) DONE
- Phase 2: Calibration + threshold-tuning DONE
- Phase 3: Telegram-backed approvals DONE
- Phase 4: ClawHub publishing + UX polish NEXT

Quick usage

```bash
python3 causal_analyst.py --seeds 123 999 555 777 --commands "ls" "df" ...
```