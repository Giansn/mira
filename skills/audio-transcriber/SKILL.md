---
name: audio-transcriber
description: "Actually transcribe audio files by installing and using Whisper locally. Use when: (1) Audio transcription is needed immediately, (2) Willing to install local tools, (3) Privacy concerns with API services, (4) Need offline capability."
---

# Audio Transcriber

## Overview

This skill **actually implements** audio transcription by installing Whisper locally and providing ready-to-use scripts. Unlike the reference `audio-transcription.skill`, this one makes transcription work immediately.

## Quick Start: Install and Transcribe

### 1. Install Dependencies
```bash
# Install Whisper and FFmpeg
pip install openai-whisper
sudo apt-get install ffmpeg

# Verify installation
whisper --version
ffmpeg -version
```

### 2. Basic Transcription
```bash
# Transcribe an audio file
whisper audio.ogg --model base --language en --output_format txt

# Output will be saved as audio.txt
```

### 3. Using the Provided Script
```bash
python3 scripts/transcribe.py audio.ogg --model small --language auto
```

## Installation Script

The `scripts/install_whisper.py` script handles everything:

```bash
# Run the installer
python3 scripts/install_whisper.py

# This will:
# 1. Check system requirements
# 2. Install FFmpeg if needed
# 3. Install Whisper
# 4. Test the installation
```

## Usage Examples

### Example 1: Telegram Audio Messages
```bash
# Typical Telegram audio path
python3 scripts/transcribe.py /home/ubuntu/.openclaw/media/inbound/file_0---[uuid].ogg
```

### Example 2: Batch Processing
```bash
# Transcribe all OGG files in a directory
python3 scripts/batch_transcribe.py /path/to/audio/files/ --output /path/to/transcripts/
```

### Example 3: Different Models
```bash
# Fast but less accurate
whisper audio.ogg --model tiny

# Balanced
whisper audio.ogg --model base

# More accurate
whisper audio.ogg --model small

# High accuracy (requires more RAM)
whisper audio.ogg --model medium
```

## Integration with OpenClaw

### Auto-Transcribe Incoming Audio
Create a script that monitors the media directory:

```python
# scripts/monitor_audio.py
import os
import time
from pathlib import Path

MEDIA_DIR = "/home/ubuntu/.openclaw/media/inbound"

while True:
    for file in Path(MEDIA_DIR).glob("*.ogg"):
        if file.suffix == ".ogg":
            # Transcribe new audio files
            transcript = transcribe_audio(str(file))
            # Save transcript
            transcript_path = file.with_suffix(".txt")
            transcript_path.write_text(transcript)
            # Notify user
            print(f"Transcribed {file.name}")
    time.sleep(10)
```

### Telegram Bot Integration
When audio is received via Telegram:
1. Check if Whisper is installed
2. Transcribe automatically
3. Send transcript back to user

## Troubleshooting

### Issue: "Whisper not found"
```bash
# Reinstall
pip uninstall openai-whisper -y
pip install openai-whisper

# Check PATH
which whisper
```

### Issue: "FFmpeg not found"
```bash
# Install FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg

# Alternative: Use conda
conda install ffmpeg -c conda-forge
```

### Issue: Out of memory
```bash
# Use smaller model
whisper audio.ogg --model tiny --device cpu

# Split audio file
ffmpeg -i long_audio.ogg -f segment -segment_time 300 -c copy output_%03d.ogg
```

### Issue: Poor transcription quality
```bash
# Specify language
whisper audio.ogg --language en

# Use larger model
whisper audio.ogg --model medium

# Clean audio first
ffmpeg -i noisy.ogg -af "highpass=f=200, lowpass=f=3000" cleaned.ogg
```

## Performance Tips

### Speed vs Accuracy Trade-off
- **tiny:** ~32x realtime, lowest accuracy
- **base:** ~16x realtime, good for most cases
- **small:** ~4x realtime, better accuracy
- **medium:** ~1x realtime, high accuracy
- **large:** ~0.5x realtime, highest accuracy

### Hardware Acceleration
```bash
# Use GPU if available (CUDA)
whisper audio.ogg --device cuda

# Use MPS on Apple Silicon
whisper audio.ogg --device mps

# Force CPU
whisper audio.ogg --device cpu
```

## Scripts Included

### `scripts/transcribe.py`
Main transcription script with options:
- Model selection
- Language detection/specification
- Output formats (txt, srt, vtt, json)
- Batch processing

### `scripts/install_whisper.py`
Complete installation script:
- Checks dependencies
- Installs Whisper and FFmpeg
- Tests installation
- Creates aliases

### `scripts/batch_transcribe.py`
Batch processing:
- Process multiple files
- Parallel processing
- Progress tracking
- Error handling

### `scripts/audio_cleaner.py`
Pre-process audio:
- Noise reduction
- Normalization
- Format conversion
- Silence removal

## Comparison with API Services

### Local Whisper Advantages
- **Privacy:** No data leaves your system
- **Cost:** Free after installation
- **Offline:** Works without internet
- **Control:** Full control over processing

### API Service Advantages  
- **No installation:** Ready to use
- **Maintenance:** No updates needed
- **Scalability:** Handles any load
- **Features:** Additional capabilities

## When to Use This vs API

**Use local Whisper when:**
- Privacy is critical
- You have many files to process
- Internet is unreliable
- You want one-time cost (installation)

**Use API when:**
- Quick setup needed
- Don't want to manage installations
- Need advanced features
- Have budget for per-minute costs

## Next Steps After Installation

1. **Test with sample audio**
2. **Integrate with media monitoring**
3. **Set up auto-transcription for Telegram**
4. **Create backup of transcripts**
5. **Monitor disk space** (models are large)

## Model Sizes and Requirements

- **tiny:** 75 MB, works on any system
- **base:** 142 MB, recommended default
- **small:** 466 MB, good balance
- **medium:** 1.5 GB, high accuracy
- **large:** 2.9 GB, best accuracy

Choose based on your accuracy needs and available RAM.
