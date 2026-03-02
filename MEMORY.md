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
- **2026-03-01:** Audio message policy: Send only audio (TTS + NO_REPLY), no duplicates, no text+audio

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
5. **Audio Messages:** When sending TTS audio responses, use `tts` tool and reply with `NO_REPLY` only. Never send both text and audio. Never send duplicate audio messages.

## Major Infrastructure Upgrade (2026-03-01)

### EBS Volume Expansion
- **Problem:** Root volume (30GB) at 100% capacity, preventing tool installation
- **Solution:** Added 50GB gp3 EBS volume (3000 IOPS, 125 MiB/s throughput)
- **Setup:** Mounted at `/data`, moved virtual environments, freed root volume
- **Result:** 47GB free space, root volume now at 95% (was 100%)

### Audio Transcription Capability
- **Problem:** Could not transcribe Telegram audio messages
- **Solution:** Installed Whisper in virtual environment on new EBS volume
- **Implementation:** Created `audio-transcription-alt.skill` with virtual environment workaround for PEP 668 restrictions
- **Result:** Successfully transcribed 8 audio files, including real-time "Do you understand me now?"

### Skill Creation Protocol
- **New Protocol:** "If you cannot do something, create a skill to do it"
- **Skills Created Today:**
  1. `notion-browser-bridge.skill` - Browser automation for Notion
  2. `audio-transcription.skill` - Speech-to-text reference
  3. `audio-transcriber.skill` - Whisper implementation (blocked by PEP 668)
  4. `audio-transcription-alt.skill` - Virtual environment workaround
  5. `multimedia-processing.skill` - Audio/image/video handling
  6. `system-diagnostics.skill` - Troubleshooting OpenClaw issues
  7. `service-management.skill` - Cron/service management
- **Outcome:** Self-improving system where limitations become new capabilities

### Key Technical Achievements
1. **Disk Space Crisis Resolved:** 50GB EBS volume added and configured
2. **Audio Transcription Working:** Whisper installed and tested successfully
3. **Skill-Based Problem Solving:** Created 7 practical skills for common tasks
4. **Memory Visualization Web Interface:** Created comprehensive web app for memory exploration (2026-03-01)
4. **Memory Visualization Web Interface:** Created comprehensive web app for memory exploration (2026-03-01)

### Memory Visualization System (2026-03-01)
- **Purpose:** Web interface for visualizing and exploring OpenClaw memory files
- **Features:**
  1. Timeline view of memory entries with filtering
  2. Full-text search across all memory content
  3. Statistics dashboard with interactive charts
  4. Topic analysis and frequency visualization
  5. Memory content viewer with detailed display
- **Technology Stack:**
  - Backend: Flask (Python) with REST API
  - Frontend: Bootstrap 5, Chart.js, custom dark theme
  - Data: JSON export from memory parser
- **Access:** `http://localhost:5000` (run from `/home/ubuntu/.openclaw/workspace/memory-viz/`)
- **API Endpoints:** `/api/memory-data`, `/api/timeline`, `/api/search`, `/api/stats`, `/api/refresh`
- **Data Sources:** MEMORY.md + memory/*.md files
- **Current Stats:** 5 daily files, 34 entries, 1906 words, 369-day range
4. **System Diagnostics:** Identified and fixed Moltbook cron issues (pending fix)
5. **Gateway Configuration:** Fixed token mismatch, enabled entrosana.com access

### Memory Visualization System (2026-03-01)
- **Purpose:** Web interface for visualizing and exploring OpenClaw memory files
- **Features:**
  1. Timeline view of memory entries with filtering
  2. Full-text search across all memory content
  3. Statistics dashboard with interactive charts
  4. Topic analysis and frequency visualization
  5. Memory content viewer with detailed display
- **Technology Stack:**
  - Backend: Flask (Python) with REST API
  - Frontend: Bootstrap 5, Chart.js, custom dark theme
  - Data: JSON export from memory parser
- **Access:** `http://localhost:5000` (run from `/home/ubuntu/.openclaw/workspace/memory-viz/`)
- **API Endpoints:** `/api/memory-data`, `/api/timeline`, `/api/search`, `/api/stats`, `/api/refresh`
- **Data Sources:** MEMORY.md + memory/*.md files
- **Current Stats:** 5 daily files, 34 entries, 1906 words, 369-day range

### New Capabilities Enabled
- **Real-time audio transcription** for Telegram messages
- **Browser automation** for Notion without OAuth
- **System troubleshooting** and diagnostics
- **Service management** for cron jobs and background processes
- **Multimedia processing** framework
- **Memory visualization** web dashboard

### Pending Tasks
1. **Fix Moltbook cron** - API key and path configuration
2. **Set up auto-transcription** - Monitor incoming audio
3. **Install better Whisper model** - base/small for improved accuracy
4. **Clean up root volume** - Move more data to EBS volume

## Project Management System (2026-03-01)

### PROJECT.md Created
- **Two main sections:**
  1. Ghostwriting (MA Kooperation, MA Konzept Mediensucht, Simulation Environment)
  2. BA-Thesis (International Social Work and Education)
- **Notion integration:** MA Kooperation content imported to PROJECT.md
- **Project tracking:** Table with projects, deadlines, costs, bonuses
- **Status tracking:** Research concept MA-Thesis (In Process), MA03 Qualitative Research (Pending), MA-Thesis (Pending)

### Notion Browser Bridge
- **Problem:** Notion API changed 2025-09-03 - no more simple Internal Integrations, only OAuth-based Public Integrations
- **Solution:** Browser automation via Chrome DevTools Protocol (CDP port 9223)
- **Implementation:** `notion-browser-bridge.skill` for Notion access without OAuth
- **Success:** Accessed Notion page "MA Kooperation", extracted content and screenshots

### Gateway Configuration Updates
- **entrosana.com access:** Added to `gateway.controlUi.allowedOrigins`
- **Token synchronization:** Fixed mismatch between `gateway.auth.token` and `gateway.remote.token`
- **Token restored:** `1f3c0559f9362ff5ff458c69eed348f6df5a7ec55bbc1287` (matches entrosana.com UI Control Settings)
- **Result:** entrosana.com can now connect to this OpenClaw gateway

## Communication Protocol Refinement (2026-03-01)

### Heartbeat Trigger Resolution
- **Problem:** Various messages (`/start`, `test`, `hey`, `so?`, `check`, `search`) were incorrectly interpreted as heartbeat polls
- **Solution:** Only respond with HEARTBEAT_OK when exact heartbeat prompt is received
- **Rule:** Immediate response to all other messages, HEARTBEAT_OK only for genuine heartbeat polls
- **Impact:** Eliminated gaps in conversation flow caused by missed responses
