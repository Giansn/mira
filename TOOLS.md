# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Device Pairing/Approval

To approve a pending device:
```bash
openclaw devices list
openclaw devices approve <request-id>
```

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## E5 Semantic Memory Search System

### **Overview**
Standalone semantic search system using E5-small-v2 embeddings. Created because OpenClaw integration failed due to context size limitations (E5: 512 tokens, OpenClaw default: 400+80 tokens).

### **Working Solution**
- **File**: `/home/ubuntu/.openclaw/workspace/e5_memory_search_wrapper.py`
- **Model**: `intfloat/e5-small-v2` (384-dimensional embeddings)
- **Chunk size**: 256 tokens (E5-compatible, 50% of 512 context)
- **Overlap**: 64 tokens (25% of chunk)
- **Embedded chunks**: 234 memory chunks from 8 files
- **Performance**: First load ~30s, subsequent searches instant

### **Usage**
```bash
# Activate virtual environment
cd /home/ubuntu/.openclaw/workspace
source .venv-embeddings/bin/activate

# Semantic search
python3 e5_memory_search_wrapper.py "your query here"

# Get statistics
python3 e5_memory_search_wrapper.py --stats

# JSON output
python3 e5_memory_search_wrapper.py "German thesis" --json

# Test with example queries
python3 e5_memory_search_wrapper.py "OpenClaw system architecture"
python3 e5_memory_search_wrapper.py "BA thesis research"
python3 e5_memory_search_wrapper.py "E5 embedding engine"
```

### **Test Results**
- **"OpenClaw system"**: Score 0.8579 ✅
- **"BA thesis research"**: Score 0.870 ✅  
- **"E5 embedding engine"**: Score 0.900 ✅
- **"Memory system"**: Score 0.866 ✅

### **Key Features**
1. **Semantic understanding**: Meaning-based search vs keyword matching
2. **Multilingual support**: German thesis content searchable
3. **Proper chunking**: 256-token chunks work with E5's 512 context
4. **Caching**: Embeddings cached for performance
5. **Standalone**: No OpenClaw integration complexities

### **Why Standalone (Not OpenClaw Integration)**
1. **Context size limitation**: E5 has 512 token limit, OpenClaw uses 400+80 tokens
2. **Configuration inflexibility**: `chunkTokens`/`chunkOverlap` not valid schema keys
3. **Better control**: Standalone allows E5-optimized chunking (256+64)
4. **Proven working**: Tested and verified with real queries

### **Source Files**
- `e5_embedding_engine.py` - E5 model wrapper
- `memory_rag.py` - Memory RAG system
- `e5_memory_search_wrapper.py` - CLI interface
- `memory/embeddings/` - Cached embeddings (.npy + .json)

### **Virtual Environment**
```bash
# Location
/home/ubuntu/.openclaw/workspace/.venv-embeddings

# Key packages
sentence-transformers==2.7.0
torch==2.5.1
numpy==2.2.4
```

### **When to Use**
- **Semantic searches**: When keyword matching isn't enough
- **Multilingual content**: German thesis, mixed-language memories
- **Concept matching**: Finding related ideas with different wording
- **Research queries**: Complex questions about past work

### **When Not to Use**
- **Simple keyword searches**: Use OpenClaw's FTS memory_search
- **Exact phrase matching**: OpenClaw FTS is better for exact matches
- **Quick lookups**: If you know the exact term

### **Maintenance**
- **Embedding updates**: Run wrapper after adding new memory files
- **Cache location**: `/home/ubuntu/.openclaw/workspace/memory/embeddings/`
- **Model updates**: Check HuggingFace for newer E5 versions
- **Performance**: First query loads model, subsequent queries fast

### **Integration Status**
- ✅ **Standalone E5 Memory RAG**: Fully working
- ❌ **OpenClaw memory search**: FTS-only (keyword matching)
- ✅ **Alternative solution**: Semantic search available via wrapper
- ✅ **User needs met**: Can perform semantic memory searches

### **Last Updated**
2026-03-03 01:11 UTC - E5 semantic search system documented
