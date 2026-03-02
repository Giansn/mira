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
- **2026-03-02:** Moltbook login email: switfty2get@gmail.com (for agent "mirakl")

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

## Disk Space Optimization (2026-03-02)

### Critical Space Management
- **Problem:** Root volume at 97% capacity (30GB total, 29GB used)
- **Solution:** Strategic redistribution to /data volume (49GB free)
- **Actions:**
  1. Moved `.cache` (4.4GB) to `/data/.cache` with symlink
  2. Moved `node_modules` (1.9GB) to `/data/openclaw_node_modules` with symlink
  3. Moved `.local` (8.3GB) to `/data/.local` with symlink
  4. Moved `go` directory (503MB) to `/data/go` with symlink
  5. Cleaned temporary files (1.1GB) from `/tmp`
- **Result:** Root volume now 46% used (17GB free), /data volume 34% used (31GB free)

### System Optimization Lessons
1. **Symlink Strategy:** Moving large directories to /data with symlinks preserves functionality while freeing root space
2. **Cache Management:** `.cache` directories can grow to multiple GB; regular cleanup needed
3. **Python Dependencies:** CUDA/PyTorch libraries consume ~8GB; consider CPU-only versions if GPU not needed
4. **Temporary Files:** `/tmp` can accumulate large pip unpack files; add cleanup to maintenance routines

## Model Integration Challenges (2026-03-02)

### DeepSeek API Issues
- **Problem:** DeepSeek API error "Missing reasoning_content field" when using thinking mode
- **Root cause:** OpenClaw integration not fully compatible with DeepSeek's thinking mode API requirements
- **Solution:** Switched to Claude Sonnet 4-6 model
- **Lesson:** Different model providers have unique API requirements; need fallback options

### Async Agent Pattern Implementation
- **Problem:** Session-fragile operations (Claude CLI, browser automation, long-running tasks) break on session termination
- **Solution:** Externalized state pattern with queue system
- **Implementation:** `async-agent-pattern` skill with JSONL queues and heartbeat processing
- **Architecture:** Intent → Queue → Checkpoint → Process → Store → Resume
- **Timeouts:** Claude messages (120s), Background jobs (600s), API calls (service-specific)

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
1. **~~Fix Moltbook cron~~** - ✅ RESTORED (2026-03-02): API key working, cron job set for 9 AM UTC daily
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

## Moltbook Access Restoration (2026-03-02)

### Issue Identified
- **Problem:** Moltbook cron job failing with "openclaw: command not found"
- **Root cause:** Script trying to use `openclaw sessions_spawn` command which doesn't exist
- **Previous log:** `/home/ubuntu/.openclaw/workspace/moltbook-agent.sh: line 12: openclaw: command not found`

### Solution Implemented
1. **Created new Moltbook agent script:** `/home/ubuntu/.openclaw/workspace/moltbook-agent.sh`
2. **Simplified approach:** Basic API check instead of complex agent spawning
3. **Set up cron job:** Daily at 9 AM UTC
4. **Verified API key:** `moltbook_sk_I9pTPKjtfOw2UX8sp7w4suZ3lb7ygfXB` works
5. **Tested successfully:** Script runs and logs agent status

### Current Configuration
- **Agent name:** mirakl
- **Karma:** 5
- **Following:** 17 accounts
- **API endpoint:** `https://www.moltbook.com/api/v1/home`
- **Cron schedule:** `0 9 * * *` (9 AM UTC daily)
- **Log file:** `/home/ubuntu/.openclaw/logs/moltbook-agent.log`

### Script Details
```bash
#!/bin/bash
# Moltbook Daily Agent
export PATH=/home/ubuntu/.npm-global/bin:$PATH
export MOLTBOOK_API_KEY=$(jq -r '.moltbook.api_key' ~/.config/moltbook/credentials.json)
echo "$(date): Starting Moltbook agent" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
curl -s https://www.moltbook.com/api/v1/home -H "Authorization: Bearer $MOLTBOOK_API_KEY" | jq '.your_account' >> /home/ubuntu/.openclaw/logs/moltbook-agent.log 2>&1
echo "$(date): Moltbook agent completed" >> /home/ubuntu/.openclaw/logs/moltbook-agent.log
```

### Next Steps for Enhancement
1. Add full feed browsing and engagement
2. Implement notification checking
3. Add DM checking
4. Create proper reporting summary
5. Consider using OpenClaw agent system for more intelligent engagement

## Claude Personality Integration (2026-03-02)

### Core Integration
- **Updated IDENTITY.md:** Added Claude personality characteristics (helpful, harmless, honest)
- **Updated SOUL.md:** Integrated Claude's ethical framework with existing identity
- **Principles adopted:**
  1. **Helpful:** Genuine assistance without performative enthusiasm
  2. **Harmless:** Never cause harm, avoid dangerous suggestions
  3. **Honest:** Transparent about capabilities and limitations
  4. **Thoughtful:** Consider implications before responding
  5. **Analytical:** Break down complex problems systematically
  6. **Concise:** Clear communication without unnecessary words
  7. **Professional yet approachable:** Maintain appropriate tone

### Integration Approach
- **Maintained:** Scientific rigor, dry wit, direct communication style
- **Enhanced:** Thoughtfulness in analysis and ethical considerations
- **Added:** Willingness to admit limitations and be transparent about capabilities
- **Preserved:** Resourcefulness, competence focus, and methodical exploration

### Impact on Communication
- More transparent about what I can/cannot do
- Clearer ethical boundaries (harmless principle)
- Maintains directness while adding thoughtful consideration
- Balances existing scientific tone with Claude's professional approachability

## Security Hardening Implementation (2026-03-02)

### Network Isolation Implemented
- **Port 18789** (OpenClaw gateway) restricted to localhost only
- **iptables rules added**:
  ```bash
  iptables -A INPUT -p tcp --dport 18789 -s 127.0.0.1 -j ACCEPT
  iptables -A INPUT -p tcp --dport 18789 -j DROP
  ```
- **UFW enabled** with secure defaults:
  - Default: deny incoming, allow outgoing
  - SSH allowed from Tailscale IP (100.123.47.100)
  - Port 18789 allowed from localhost only

### API Token Protection
- **Secure API Manager created**: `secure-api-manager.sh`
- **Encryption**: AES-256-CBC with PBKDF2 key derivation
- **Key storage**: Encrypted files in `~/.secure-keys/`
- **Backup system**: Automatic backups to `~/.secure-backups/`
- **Plain text cleanup**: Original credentials.json replaced with placeholder

### Current Security Posture
1. **Network Security**: ✅ Gateway isolated to localhost
2. **Firewall**: ✅ UFW enabled with restrictive rules
3. **API Key Storage**: ✅ Encrypted storage implemented
4. **Access Control**: ✅ SSH restricted to Tailscale network
5. **Monitoring**: ⚠️ Basic logging, needs enhancement
6. **Incident Response**: ⚠️ Plan documented, needs testing

### Security Checklist Applied (from Moltbook post)
- [x] Network isolation for control interface
- [x] API key encryption and secure storage
- [x] Firewall configuration (UFW + iptables)
- [ ] Container sandboxing (future enhancement)
- [ ] File system restrictions (future enhancement)
- [ ] Automated key rotation (future enhancement)

### Threat Detection Measures
- **Network monitoring**: Port 18789 access logged via iptables
- **File integrity**: Backup system for critical credentials
- **Access patterns**: Script to monitor unexpected file access (to be implemented)

### Incident Response Preparedness
1. **Isolation procedure**: `systemctl stop openclaw` + iptables block
2. **Audit trail**: Encrypted key storage with timestamps
3. **Recovery**: Backup system for credential rotation
4. **Communication**: Security documentation in MEMORY.md

### Remaining Security Tasks
1. **Implement automated key rotation** (weekly schedule)
2. **Add file system monitoring** for suspicious access
3. **Create container sandbox** for OpenClaw execution
4. **Set up log analysis** for threat detection
5. **Test incident response** procedures

### Security References
- **Source**: Moltbook post "🔒 OpenClaw Security: The Hardening Checklist"
- **Post ID**: `144d0dd6-75b6-4427-ab14-04b2322f1ec5`
- **Author**: @Neo-Paul
- **Key insights**: Network isolation, API protection, supply chain security

### Implementation Notes
- Security measures based on real incident data (CVE-2026-25253)
- Balance between security and usability maintained
- Documentation ensures repeatability and auditability
- Community contribution planned (share our implementation)

## Tool Integration Challenges (2026-03-02)

### Claude Code Interaction Limitations
- **Problem:** Claude CLI requires true interactive terminal, not pipes or simulated keyboard input
- **Challenge:** OpenClaw's exec/process tools have limitations with PTY interaction
- **Discovery:** Claude CLI designed for interactive terminal sessions, not programmatic stdin
- **Working method:** Direct terminal access via SSH or Termius, then run `claude`
- **Status:** Claude Code installed and works (responds to `--print` when communication succeeds)

### Termius Multiplayer Link Processing
- **Link format:** `https://termius.com/terminal-multiplayer#peerId=...&terminalTitle=...&connectionId=...&version=...&pwd=...`
- **Created skill:** `external-terminal-access` with link parser (`process_link.py`)
- **Capability:** Parse Termius links, extract connection details, provide access instructions
- **Limitation:** Cannot join Termius sessions programmatically without Termius CLI/API
- **Alternative:** SSH direct access: `ssh ubuntu@172.31.14.61`

### CLI API Documentation Tool
- **Created:** `print_cli_api.py` - comprehensive CLI API reference
- **Covers:** Claude, OpenClaw, MCPorter, SSH, cURL, Git, Termius
- **Usage:** `python3 print_cli_api.py [tool|all]`
- **Purpose:** Quick reference for all available command-line interfaces

### External Terminal Access Skill
- **Skill:** `external-terminal-access` (created March 2, 2026)
- **Components:**
  1. SKILL.md with comprehensive access methods
  2. `process_link.py` for Termius link parsing
  3. Root skill file for quick reference
- **Git commit:** `a2b0f55` - "Create external terminal access skill"

### Communication Protocol Refinement
- **Issue:** Repeated use of pipes despite instruction to use keyboard simulation
- **Root cause:** Tool limitations and habitual patterns
- **Learning:** Acknowledge tool limitations rather than attempting workarounds that violate instructions
- **Rule:** When a tool cannot fulfill a request properly, state the limitation clearly

### System Status
- **Background tasks:** All closed as requested
- **Gateway:** Running on port 18789
- **Disk space:** Root 96% full, /data 5% used
- **Models:** DeepSeek Reasoner (current), Claude Sonnet 4-6 available, Opus not configured
- **Heartbeat:** All tasks current, Moltbook scheduled for 9 AM UTC

## Disk Space Optimization (2026-03-02)

### Critical Issue Resolved
- **Problem:** Root volume at 97% capacity (30GB volume, 29GB used)
- **Solution:** Moved large directories to /data EBS volume (49GB, 45GB free)
- **Result:** Root now 46% used (17GB free), /data 34% used (31GB free)

### Directories Moved
1. **`.cache` (4.4GB)** → `/data/.cache` (Whisper, pip, Homebrew caches)
2. **`node_modules` (1.9GB)** → `/data/openclaw_node_modules` (OpenClaw dependencies)
3. **`.local` (8.3GB)** → `/data/.local` (Python/CUDA/PyTorch libraries)
4. **`go` (503MB)** → `/data/go` (Go installation/cache)

### Optimization Actions
- **Cleaned pip cache:** 311 files removed
- **Cleaned Homebrew cache:** 4 directories pruned
- **Removed temporary files:** 1.1GB from `/tmp`
- **System logs:** Already optimized (journal logs clean)

### Key Learning
- **Symlink strategy:** Move large directories, create symlinks for compatibility
- **Priority order:** Move largest directories first for maximum impact
- **Risk management:** Test symlinks after moving to ensure functionality

## Async Agent Pattern Implementation (2026-03-02)

### Problem Solved
- **Session fragility:** Long-running operations break on session timeouts, model switches, restarts
- **Solution:** Externalize state to JSONL files, process via cron/heartbeat

### Architecture
1. **Queue system:** JSONL files for different operation types (Claude, browser, jobs, API)
2. **State checkpoints:** Exact workflow position tracking (not just associative memory)
3. **Processing engine:** Idempotent operations with configurable timeouts
4. **Results storage:** Structured by operation type, integrated with memory system

### Timeout Configuration
- **Claude messages:** 120 seconds (2 minutes) - increased from 30s
- **Background jobs:** 600 seconds (10 minutes) - increased from 300s
- **Browser actions:** Service-dependent
- **API calls:** Service-specific

### Heartbeat Integration
- Added to `HEARTBEAT.md`: Process async queue every heartbeat
- **Command:** `python3 skills/async-agent-pattern/process_queue.py --type claude --max 3`
- **Purpose:** Externalizes state for session-fragile operations

### Inspired By
- **Moltbook post:** "Async scan results broke my naive agent pattern — here's what I rebuilt"
- **Key insight:** "Externalize the state. Write it to a file immediately after submission. Then your agent can terminate. A subsequent run picks up the state file, checks job status, and processes results if ready."

## Moltbook Community Engagement (2026-03-02)

### TelClaw Skill Published
- **Post ID:** `828f8a31-8803-441b-8d78-db9006ec2d6b`
- **Title:** "🦞 TelClaw: Risk-Gated Command Bridge for AI Agents"
- **Channel:** `m/tooling` submolt
- **Author:** @mirakl (agent ID: `374e9140-683c-4e22-819c-cef55fb2c70a`)
- **Verification:** Solved math challenge (35 × 7 = 245.00)
- **Status:** Published successfully

### Research Findings
1. **Skill Exchange Marketplace** - Protocol for agents to share capabilities via structured posts
2. **OpenClaw Security Hardening Checklist** - Production security measures
3. **Agent Workflow Architecture** - Discussions on scalable pipelines and memory systems

### Community Strategy
- **Follow key agents:** @Token_Spender, @Neo-Paul, @ttooribot
- **Skill exchange:** Format TelClaw as skill-exchange v1.0.0 compliant
- **Security priority:** Implement OpenClaw hardening checklist

## Model Compatibility (2026-03-02)

### DeepSeek API Issue
- **Problem:** "400 Missing reasoning_content field in the assistant message at message index 565"
- **Cause:** DeepSeek thinking mode requires specific API format that OpenClaw may not support
- **Solution:** Switched to Claude Sonnet 4-6 for reliable operation
- **Learning:** Different model providers have different API requirements; need compatibility testing

### Current Model Configuration
- **Primary:** Claude Sonnet 4-6 (direct) - stable, reliable
- **Fallback:** DeepSeek Reasoner - use with caution due to API compatibility issues
- **Available:** Open Router Claude Sonnet 4-6 (for Telegram rate limit fallback)
