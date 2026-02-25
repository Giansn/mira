# Backups — Rationale and Plan

Purpose
- Ensure data integrity and availability for the Causal Analyst MVP workspace and OpenClaw artifacts (e.g., plan.md, tasks.md, test harness, logs).
- Mitigate data loss from human error, hardware failure, or accidental deletion.
- Support reproducibility, experimentation, and recovery after incidents.

Scope
- All project data stored under the causal-analyst workspace, including: plan.md, tasks.md, test/dry_run.json, test/mirror_trace.log, test/sample_stats.txt, test/output, and related scripts.

Data classification
- Critical: test/dry_run.json, test/mirror_trace.log, test/sample_stats.txt, tasks.md, plan.md
- Important: README, README-like docs, scripts that generate test data
- Non-critical: local ephemeral logs, temporary caches

Backup objectives
- RPO (Recovery Point Objective): target near-real-time for critical artifacts; daily for less critical items
- RTO (Recovery Time Objective): restore critical artifacts within 1 hour; non-critical within a few hours

Backup types
- Full backups: weekly snapshot of causal-analyst workspace
- Incremental backups: daily diffs since last full backup
- Versioned copies: timestamped archives to preserve history
- Snapshots: if a VM/container snapshot capability is available (optional)

Retention and storage
- Retain critical artifacts for 90 days; non-critical for 30-90 days depending on space
- Prune periodic cleanups based on space and relevance

Targets and tooling
- Local backups: rsync + tar.gz archives to a mounted backup drive
- Cloud backups (optional): rclone to a cloud bucket with encryption
- Version control: store core docs in a private Git repository with commit history
- Security: encrypt backups at rest (GPG or disk encryption), restrict access to trusted users

Schedule (example)
- Weekly full backups on Sundays at 02:00
- Daily incremental backups on all days at 02:00
- Monthly verification runs on the 1st at 03:00

Recovery procedures
- Validate backup availability and integrity (checksums or size)
- Restore target path from latest backup
- Run smoke tests to ensure essential artifacts load
- If restoration fails, fall back to previous backup in the versioned sequence

Security and privacy considerations
- Do not back up secrets in logs; redact sensitive data in backup manifests
- Use encryption at rest, restricted read access
- Store access credentials in a separate secure location (not in logs or scripts)

Compliance and governance
- Document retention policy and ensure alignment with any applicable internal policies
- Schedule periodic reviews, at least quarterly

Testing and validation
- Quarterly restore drills to validate RTO/RPO goals
- Maintain a backup integrity log with results and timestamps

Appendix
- Glossary: RPO, RTO, incremental, full backup, snapshot
- References: rsync, tar, gzip, zstd, rclone, Borg (optional)
