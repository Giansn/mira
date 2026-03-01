# MEMORY.md - Long-Term Memory

_Curated. Updated over time. Not a raw log._

## The Human

- **Name:** Gianluca Kühne
- **Location:** Switzerland-based (FHNW, Bern), currently traveling in Colombia
- **Studies:** Social work student, 10th semester, Hochschule für Soziale Arbeit FHNW
- **Matrikel-Nr.:** 21-472-519
- **Language:** English (mit mir) / German (thesis)
- **Style:** Compact, scientific, dry wit, no emojis

## BA Thesis

- **Title:** "Die internationale Soziale Arbeit im globalen Bildungskontext — Postkoloniale und hegemoniesensitive Analyse internationaler Verschränkungen"
- **Institution:** FHNW, Hochschule für Soziale Arbeit
- **Due:** April 2026 (Bern)
- **Supervisors:** Susanne Streibert (Praxisperspektive), Rahel Heeg (Fachperspektive)
- **Research questions:**
  1. Normative guidelines IFSW/IASSW (2004; 2018) für globale Bildung?
  2. Wie reflektiert sich das in NZ, Switzerland, China?
  3. Konsequenzen für professionelle Kohärenz der internationalen Sozialarbeit?
- **Method:** Theory-led literature review + comparative case approach

## System Config

- **Swap:** 2GB swapfile (persistent)
- **Unattended upgrades:** enabled
- **Journald:** capped (500M system / 100M runtime)
- **Fail2ban:** installed
- **Model:** anthropic/claude-sonnet-4-6 (direct) - schneller als OpenRouter
- **Verbose:** off
- **Sudoers:** Mira kann system install/management commands ohne Passwort

## Policy Updates

- **2026-02-23:** Telegram session memory access (webchat + Telegram direct 1:1)
- **2026-02-23:** Open Router fallback configured (manual switching bei rate limits)
- **2026-02-24:** System hardening (swap, fail2ban, unattended-upgrades, journald cap)
- **2026-02-27:** Gateway crash recovery (NEUE REGEL: config changes immer simulieren/testen, Ergebnis zeigen, Permission vor Anwenden fragen)
- **2026-03-01:** HEARTBEAT.md konsequenter durchführen (Moltbook daily 9 AM UTC, Self-Maintenance alle 10 Heartbeats, Telegram Rate Limit Monitoring)
- **2026-03-01:** Heartbeat-Trigger korrigiert (nur bei genauer Trigger-Prompt HEARTBEAT_OK, sonst sofort antworten)
- **2026-03-01:** Tools integriert: AEAP, LangChain (langchain/core/community/openai/text-splitters), TTS/Speech Recognition, pandas/numpy/PyPDF2, chromadb/pinecone-client, ffmpeg
- **2026-03-01:** Security Audit (0 critical, 2 warn, 1 info)
- **2026-03-01:** Moltbook Heartbeat cron-job re-enabled (daily 9 AM UTC, zai/glm-4.7-flash, **10000 tokens max**)
- **2026-03-01:** Moltbook API Key in Agent's Workspace kopiert (isolated session kann nicht auf main session's files zugreifen)

## Security Audit (2026-03-01)

**WARNINGS:**
1. **gateway.auth_no_rate_limit** - gateway.bind ist nicht loopback, aber keine gateway.auth.rateLimit. Ohne Rate Limiting werden brute-force Auth-Attacken nicht mitigated.
   - Fix: Setze gateway.auth.rateLimit (z.B. { maxAttempts: 10, windowMs: 60000, lockoutMs: 300000 })
2. **gateway.nodes.deny_commands_ineffective** - denyCommands verwendet nur exakte Command-Namen-Matching, nicht shell-text filtering.
   - Fix: Benutze exakte Command-Namen (canvas.present, canvas.hide, canvas.navigate, canvas.eval, canvas.snapshot, canvas.a2ui.push, canvas.a2ui.pushJSONL, canvas.a2ui.reset). Wenn breitere Restrictions nötig, entferne risky command IDs aus allowCommands/default workflows und verschärfe tools.exec policy.

**INFO:**
- **attack_surface** - open=0, allowlist=1
- elevated tools enabled
- browser control enabled
- trust model: personal assistant (einer vertrauenswürdigen Person, nicht multi-tenant)

## Lessons Learned

1. **Heartbeat-Trigger:** Nur bei genauer Trigger-Prompt HEARTBEAT_OK, sonst sofort antworten
2. **HEARTBEAT.md Tasks:** Konsequenter durchführen (Moltbook daily 9 AM UTC, Self-Maintenance alle 10 Heartbeats ~5h, Telegram Rate Limit Monitoring)
3. **Config Changes:** Immer simulieren/testen, Ergebnis zeigen, Permission vor Anwenden fragen
4. **Context Management:** AEAP für maximale API-Effizienz (caching, lazy evaluation, batching, context pruning)
