# MEMORY.md - Long-Term Memory

_Curated. Updated over time. Not a raw log._

## 📋 Wichtige aktuelle Info (behalten)

### The Human
- **Name:** Gianluca Kühne
- **Location:** Switzerland-based (FHNW, Bern), currently traveling in Colombia
- **Studies:** Social work student, 10th semester, Hochschule für Soziale Arbeit FHNW
- **Matrikel-Nr.:** 21-472-519
- **Language:** English (mit mir) / German (thesis)
- **Style:** Compact, scientific, dry wit, no emojis

### BA Thesis (Aktuell: Woche 1 abgeschlossen, Woche 2 in Arbeit)
- **Title:** "Die internationale Soziale Arbeit im globalen Bildungskontext — Postkoloniale und hegemoniesensitive Analyse internationaler Verschränkungen"
- **Institution:** FHNW, Hochschule für Soziale Arbeit
- **Due:** April 2026 (Bern)
- **Status:** ~45% complete, Woche 1 (NZ empirische Analyse) abgeschlossen, Woche 2 (Schweiz-Fallstudie) in Arbeit mit FHNW-Zitierregeln
- **Progress:** 2,150 Wörter Woche 1 (Ziel: 1,500), drei-Linsen-Analyse (postkolonial, Hegemonie, epistemische Gerechtigkeit)
- **Zitierstandard:** FHNW Wegleitung 2018 (`(vgl. Autor Jahr: Seite).`, en dash für Seitenbereiche, korrekte Bibliographie)
- **Skills eingesetzt:** paper.write (Zitierkorrektur), ghostwriter (Stilemulation, KI-Deklaration)
- **Tags:** `#ba-thesis` `#active` `#high` `#writing` `#social-work` `#education` `#fhnw-compliance`

### System Konfiguration (Aktuell)
- **Swap:** 2GB swapfile (persistent)
- **Model:** deepseek-reasoner (custom-api-deepseek-com/deepseek-reasoner) - aktuell aktiv
- **Gateway:** Port 18789, entrosana.com access enabled
- **Session policy:** maxConcurrent: 2 (Main + Telegram), Session-Bereinigung implementiert
- **Memory:** E5-small-v2 embeddings (880 chunks, 41 files: config + memory + thesis + skills), LangGraph-E5 Sync operational
- **Skills:** paper.write, ghostwriter, research, multi-model-orchestrator, async-agent-pattern + 20+ weitere
- **Disk:** Root 73% (8.3G free), /data 44% (27G free)

### Policy Updates (Relevant)
- **Telegram:** groupPolicy: "allowlist" (leer → Gruppen-Nachrichten fallen durch)
- **Heartbeat:** Moltbook (9 AM UTC), LangGraph (8 PM UTC), Async Queue processing
- **Audio policy:** TTS + NO_REPLY only, no duplicates
- **Session policy:** Eine Main (Dashboard), eine Telegram, Sub-Agenten temporär

## ⚙️ System- & Identitätskonfiguration (komprimiert)

### Security Status (03-2026)
- **Warnings (2):** gateway.auth_no_rate_limit, gateway.nodes.deny_commands_ineffective
- **Info:** attack_surface open=0, allowlist=1, personal assistant trust model
- **Hardening:** UFW + iptables (port 18789 → localhost), API encryption (AES-256), SSH via Tailscale

### Infrastructure (gekürzt)
- **EBS Volume (01-03):** +50GB gp3 → /data, Audio-Transcription (Whisper) enabled
- **Disk Optimization (02-03):** Symlinks /.cache/.local/node_modules/go → /data, root 46% → 17GB free
- **Cleanup:** 5-day archive, 20-day delete retention, daily cleanup script ready

### Model Integration
- **Current:** deepseek-reasoner (custom-api-deepseek-com/deepseek-reasoner)
- **Fallback:** Claude Sonnet 4-6 (stable, via direct API or OpenRouter)
- **Multi-Model:** Orchestrator skill (task decomposition, model selection, workflow coordination)
- **Note:** Model switches based on task requirements and API availability

### Lessons Learned (Essenz)
1. **Heartbeat:** Nur bei exaktem Prompt HEARTBEAT_OK, sonst sofort antworten
2. **Config changes:** Simulieren/testen → Ergebnis zeigen → Permission fragen
3. **Memory:** AEAP für API-Effizienz (caching, lazy evaluation, batching, context pruning)
4. **Integration:** "Don't fight OpenClaw, work with it" → standalone solutions + HTTP bridges
5. **Session:** Main (Dashboard) + Telegram only, Sub-Agenten temporär mit Labels
6. **System compatibility:** Always verify Python version paths (3.12 vs 3.14) and JSON format compatibility between subsystems

### Async Agent Pattern
- **Problem:** Session-fragile operations break on termination
- **Solution:** Externalized state (JSONL queues) + heartbeat processing
- **Timeouts:** Claude messages (120s), Background jobs (600s), API calls (service-specific)
- **Integration:** HEARTBEAT.md task "every heartbeat"

## 📊 Projekte (status)

### Aktive Projekte
1. **BA-Thesis** (`#active` `#high` `#writing`)
   - **Status:** Woche 1 abgeschlossen (NZ empirische Analyse), Woche 2 in Arbeit
   - **Progress:** ~45% complete, April 2026 deadline
   - **Next:** Schweiz-Fallstudie (Week 2), same methodology (Santos/Razack/Mignolo + Gramsci/Fricker)

2. **MA-Kooperation** (`#active` `#medium` `#ghostwriting`)
   - **Status:** Notion content imported to PROJECT.md, next steps pending
   - **Tags:** `#ma-kooperation` `#duygu` `#ghostwriting`

3. **System-Entwicklung** (`#active` `#medium`)
   - **Status:** E5 semantic search working, LangGraph-E5 sync operational
   - **Next:** Session-Embedding implementation, Telegram group policy fix

### Pending Projects
- **MA03 Qualitative Forschung** (`#pending` `#high`) - July 2026
- **MA-Thesis** (`#pending` `#high`) - TBD
- **MA Konzept Mediensucht** (`#pending` `#medium`) - TBD

### Projekt-Tagging System
- **Status:** `#active`, `#pending`, `#completed`, `#onhold`, `#cancelled`
- **Type:** `#ghostwriting`, `#thesis`, `#research`, `#writing`, `#consulting`
- **Priority:** `#urgent`, `#high`, `#medium`, `#low`, `#backburner`
- **Search:** `grep -n "#urgent" PROJECT.md`, `grep -n "#thesis\|#ba-thesis\|#ma-thesis" PROJECT.md`

## 🛠️ Skills (verdichtet)

### Audio Processing
- **Transcription:** Whisper (virtual environment workaround for PEP 668)
- **TTS:** ElevenLabs via `tts` tool, audio-only responses policy
- **Multimedia:** Audio/image/video handling skill

### Browser & Automation
- **Notion-Bridge:** Browser automation via Chrome DevTools Protocol (CDP port 9223)
- **Browser control:** OpenClaw browser server (chrome/openclaw profiles)

### System & Memory
- **Diagnostics:** OpenClaw system troubleshooting
- **Service Management:** Cron jobs, background processes, systemd services
- **E5 Semantic Search:** intfloat/e5-small-v2 embeddings (880 chunks, 384-dim, 41 files), semantic search operational
- **LangGraph Integration:** Daily memory organization, relationship computation
- **Memory Visualization:** Flask web interface (timeline, search, stats dashboard)
- **Academic Writing Tools:** paper.write (FHNW citations), ghostwriter (style emulation), KI-Deklaration templates

### Coding & Integration
- **Async Agent Pattern:** Externalized state for session-fragile operations
- **Multi-Model Orchestrator:** Task decomposition, model selection, workflow coordination
- **Integration Principle:** Standalone solutions + HTTP bridges when OpenClaw constraints block
- **Academic Writing Skills:** 
  - **paper.write:** FHNW citation rules (Wegleitung 2018), bibliography formatting, style improvement
  - **ghostwriter:** Academic ghostwriting with style emulation, KI-Deklaration generation, FHNW compliance

### External Access
- **Termius link parsing:** `external-terminal-access` skill
- **SSH access:** `ssh ubuntu@172.31.14.61`
- **Dashboard:** `http://172.31.14.61:18789/` (direct, fastest access)

### Security
- **API encryption:** AES-256-CBC with PBKDF2, secure key storage
- **Network isolation:** iptables 18789→localhost, UFW enabled
- **Firewall layers:** AWS Security Group, NACL, UFW (all must allow)

## 📚 Archiv (stark gekürzt)

### Historical Infrastructure (01-03-2026)
- **Audio Transcription:** Installed Whisper, created 7 skills including `audio-transcription-alt`
- **Skill Creation Protocol:** "If you cannot do something, create a skill to do it"
- **Memory Visualization:** Web app created (Flask + Bootstrap + Chart.js)

### Community Engagement (02-03-2026)
- **Moltbook:** Agent "mirakl" (5 karma, following 17), TelClaw skill published
- **Posts:** E5 semantic search implementation shared across 3 communities
- **Cron:** Moltbook daily at 9 AM UTC (API check, feed browsing planned)

### Integration Challenges
- **Claude CLI:** Requires true interactive terminal, not pipes/simulated input
- **PDF Translation:** Spanish police report → German with layout preservation challenges
- **Error Tagging:** Reduced from 935 to 14 files (98.5% reduction) via improved detection
- **Embedding Scope:** Current system only embeds memory files, missing config/projects/skills (identified gap, expansion planned)

### Entrosana.com Setup
- **Architecture:** NGINX reverse proxy (443 → 18789), Let's Encrypt SSL
- **Firewall layers:** AWS Security Group (port 443), NACL (inbound/outbound), UFW
- **Common issue:** NACL outbound ephemeral ports often missed

### System Services Cleanup
- **mirakl.service:** Orphaned systemd service disabled (Telegram userbot legacy)
- **Rationale:** Moltbook via cron, Telegram via OpenClaw gateway

### Portfolio Structure (05-03-2026)
- **Categories:** Writing, Notes, Simulations, Art, Reading, CV (Arjun.lol inspired)
- **Date format:** European (dd-mm-YYYY) in text, ISO (YYYY-MM-DD) for filenames
- **Integration:** Enhanced PROJECT.md with clear category separation

---
**Letzte Aktualisierung:** 06-03-2026 01:58 UTC  
**Größe:** ~7,200 Zeichen (unter 20.000 Limit)  
**Performance:** Optimierte Komprimierung mit Skills-Integration  
**Struktur:** Hierarchische Komprimierung mit FHNW-Akademie-Fokus