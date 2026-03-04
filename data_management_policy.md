# Data Management & Cleanup Policy Proposal

## 1. Data Categorization & Tagging

### **Memory Files** (`memory/YYYY-MM-DD.md`)
- **Tagging**: Automatic tag assignment based on content
  - `[VOICE]`: Voice/accent/TTS/audio conversations
  - `[DISK]`: Disk space, storage, cleanup operations
  - `[CRON]`: Scheduled jobs, automation, cron tasks
  - `[HEARTBEAT]`: System health checks, monitoring
  - `[AUDIO]`: Audio file processing, transcription
  - `[TTS]`: Text-to-speech operations
  - `[TRANSCRIPTION]`: Speech-to-text processing
  - `[CLEANUP]`: Data cleanup, optimization
  - `[DECISION]`: Important decisions, choices
  - `[ERROR]`: Errors, failures, issues
  - `[SUCCESS]`: Successful operations, fixes
  - `[SYSTEM]`: System status, performance
  - `[MEMORY]`: Memory management, search, embeddings
  - `[CONVERSATION]`: General conversation tracking

- **Format**: `## [TAG1] [TAG2] Title (YYYY-MM-DD HH:MM UTC)`

### **Log Files** (`logs/`)
- **Structured logging levels**: INFO, WARN, ERROR, DEBUG
- **Component tagging**: `[GATEWAY]`, `[TELEGRAM]`, `[CRON]`, `[HEARTBEAT]`, `[MEMORY]`
- **Format**: `[TIMESTAMP] [LEVEL] [COMPONENT] Message`

### **Cache Directories** (`.cache/`, `memory/embeddings/`)
- **Metadata**: Source, creation date, last access, size
- **Purpose tagging**: `[MODEL]`, `[EMBEDDING]`, `[TRANSIENT]`

## 2. Retention Policies

### **Memory Files**
- **Detailed logs**: Last 7 days (keep full detail)
- **Summarized logs**: 8-30 days (prune to key events only)
- **Archived logs**: >30 days (compress, move to `/data/archive/`)
- **MEMORY.md**: Curated long-term memory (manual updates)

### **Log Files**
- **Active logs**: Last 7 days (keep uncompressed)
- **Archived logs**: 8-90 days (compressed `.gz`)
- **Deleted**: >90 days (except critical errors)

### **Cache**
- **Model cache** (`.cache/huggingface`, `.cache/whisper`):
  - Frequently used: Keep indefinitely
  - Infrequently used (>30 days): Delete
  - Large unused models (>100MB, unused >7 days): Delete
- **Embedding cache** (`memory/embeddings/`):
  - Keep all (regenerating is expensive)
  - Prune only if disk critical
- **Temporary cache** (`.cache/misc`):
  - Delete after 7 days

### **Virtual Environment**
- **Unused packages**: Remove if not used in 30 days
- **GPU libraries**: Remove if no GPU available
- **Development tools**: Keep only in development environment

## 3. Cleanup Automation

### **Daily Tasks** (run at 3 AM UTC)
1. **Memory pruning**: Remove low-importance entries from yesterday's file
2. **Log rotation**: Compress logs >7 days old
3. **Cache check**: Flag unused large files

### **Weekly Tasks** (Sunday 3 AM UTC)
1. **Memory summarization**: Create weekly summary, archive detailed logs
2. **Package cleanup**: Remove unused pip packages
3. **Temp file cleanup**: Delete all temporary files

### **Monthly Tasks** (1st of month, 3 AM UTC)
1. **Comprehensive cleanup**: Full system cleanup
2. **Archive rotation**: Move old archives to long-term storage
3. **Policy review**: Update policies based on usage patterns

## 4. Monitoring & Reporting

### **Metrics to track:**
- Disk usage by category (memory, logs, cache, models)
- Cleanup effectiveness (GB freed, files removed)
- Tag distribution (most common activity types)
- Retention compliance (policy adherence)

### **Reports:**
- **Daily**: Cleanup summary (what was removed/compressed)
- **Weekly**: Disk usage trends, tag analysis
- **Monthly**: Comprehensive data management report

## 5. Implementation Plan

### **Phase 1: Immediate (This week)**
1. Implement basic memory tagging for new entries
2. Remove CUDA libraries (5GB gain)
3. Create daily cleanup script skeleton

### **Phase 2: Short-term (Next 2 weeks)**
1. Full tagging system for all data
2. Automated cleanup routines
3. Monitoring dashboard

### **Phase 3: Long-term (Next month)**
1. Machine learning for importance scoring
2. Predictive cleanup (anticipate disk needs)
3. Self-optimizing policies

## 6. Success Metrics

- Disk usage consistently <80%
- Cleanup operations <5 minutes daily
- All data properly tagged and categorized
- No manual cleanup interventions needed
- User satisfaction with system organization