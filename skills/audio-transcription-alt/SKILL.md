---
name: audio-transcription-alt
description: "Alternative audio transcription methods that work within system restrictions. Use when: (1) Can't install Whisper system-wide, (2) Need lightweight solutions, (3) Quick transcription without full installation, (4) System has Python restrictions (PEP 668)."
---

# Alternative Audio Transcription

## Overview

This skill provides workarounds for audio transcription when system-wide Python installations are restricted (PEP 668). It includes methods that don't require `sudo` or breaking system packages.

## The Problem: PEP 668 Restrictions

Modern Linux systems (Ubuntu 23.04+, Debian 12+) enforce PEP 668, which prevents `pip install` without `--break-system-packages` flag. This protects system integrity but makes installing tools like Whisper difficult.

**Error message:**
```
error: externally-managed-environment
```

## Solution Approaches

### 1. Virtual Environments (Recommended)
Create isolated Python environments:

```bash
# Create virtual environment
python3 -m venv ~/venv/whisper

# Activate
source ~/venv/whisper/bin/activate

# Install Whisper
pip install openai-whisper

# Use it
whisper audio.ogg --model tiny
```

### 2. User Installation with `--user` Flag
```bash
# Try user installation
python3 -m pip install --user openai-whisper

# If that fails, use break-system-packages
python3 -m pip install --break-system-packages openai-whisper
```

### 3. AppImage/Standalone Whisper
Use pre-packaged Whisper binaries:

```bash
# Download Whisper.cpp (C++ implementation)
wget https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.0/whisper.cpp-1.5.0-linux-x64.tar.xz
tar -xf whisper.cpp-1.5.0-linux-x64.tar.xz
cd whisper.cpp-1.5.0

# Convert audio to WAV first
ffmpeg -i audio.ogg -ar 16000 -ac 1 -c:a pcm_s16le audio.wav

# Transcribe
./main -m models/ggml-tiny.bin -f audio.wav -l en
```

### 4. Docker Container
Run Whisper in Docker:

```bash
# Pull Whisper image
docker pull onerahmet/openai-whisper-asr-webservice:latest

# Run transcription
docker run -v $(pwd):/data onerahmet/openai-whisper-asr-webservice:latest \
  whisper --model tiny --language en /data/audio.ogg
```

### 5. API Fallback
When local installation isn't possible, use APIs:

```python
# Use OpenAI API (requires API key)
import openai

with open("audio.ogg", "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )
```

## Scripts for Restricted Environments

### `scripts/venv_whisper.py`
Creates and manages virtual environments for Whisper:

```bash
python3 scripts/venv_whisper.py create
python3 scripts/venv_whisper.py transcribe audio.ogg
```

### `scripts/whisper_docker.py`
Manages Docker-based transcription:

```bash
python3 scripts/whisper_docker.py transcribe audio.ogg --model base
```

### `scripts/api_transcribe.py`
Uses cloud APIs (requires credentials):

```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/api_transcribe.py audio.ogg
```

## Step-by-Step: Virtual Environment Method

### 1. Create Environment
```bash
# In workspace directory
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install in Virtual Environment
```bash
# FFmpeg (system package, may need sudo)
sudo apt-get install ffmpeg

# Whisper (in virtual env, no sudo needed)
pip install openai-whisper
```

### 3. Create Wrapper Script
```bash
#!/bin/bash
# whisper-venv.sh
source /home/ubuntu/.openclaw/workspace/.venv/bin/activate
whisper "$@"
```

### 4. Make it Persistent
Add to `.bashrc` or script that activates venv on demand.

## Comparison of Methods

| Method | Setup Complexity | Performance | Privacy | Internet Required |
|--------|------------------|-------------|---------|-------------------|
| Virtual Environment | Medium | Good | Excellent | No (after install) |
| Docker | Medium | Good | Excellent | No (after pull) |
| Whisper.cpp | Easy | Excellent | Excellent | No |
| API | Easy | Good | Poor (data leaves) | Yes |
| System Install | Hard (PEP 668) | Good | Excellent | No |

## Troubleshooting PEP 668

### If `--user` fails:
```bash
# Check pip configuration
python3 -m pip config list

# Create pip.conf for user installs
mkdir -p ~/.config/pip
echo "[global]
break-system-packages = true
user = true" > ~/.config/pip/pip.conf
```

### If virtual env fails:
```bash
# Ensure venv module is installed
sudo apt-get install python3-venv

# Try different Python
python3.10 -m venv .venv
```

### If Docker fails:
```bash
# Install Docker
sudo apt-get install docker.io
sudo usermod -aG docker $USER
# Log out and back in
```

## Integration with OpenClaw

### Auto-Detection Script
Create a script that tries methods in order:

```python
def transcribe_audio(audio_path):
    # Try virtual env first
    if try_venv_transcription(audio_path):
        return
    
    # Try Docker
    if try_docker_transcription(audio_path):
        return
    
    # Try API
    if try_api_transcription(audio_path):
        return
    
    # Fallback: provide audio info
    return get_audio_info(audio_path)
```

### Telegram Integration
When audio is received:
1. Check if any transcription method is available
2. Use best available method
3. If none, provide metadata and installation instructions

## Minimal Viable Transcription

When nothing else works, at least provide:

1. **Audio metadata:** Duration, format, size
2. **Conversion options:** How to convert to text manually
3. **Installation guide:** Steps to enable transcription

```bash
# Basic metadata fallback
ffprobe -v quiet -show_entries format=duration,size -of csv=p=0 audio.ogg
# Output: 7.02,144691
```

## Security Considerations

### Virtual Environments
- Isolated from system Python
- Can be deleted easily
- No root access needed

### Docker
- Containerized, more secure
- Can limit resources
- Easy to clean up

### APIs
- Data leaves your system
- Check provider's privacy policy
- Use for non-sensitive audio only

## Performance Optimization

### For Virtual Environments
```bash
# Use smaller models
whisper audio.ogg --model tiny --fp16 False

# Batch process in venv
for file in *.ogg; do
    whisper "$file" --model tiny --output_dir transcripts/
done
```

### For Docker
```bash
# Mount volume for faster I/O
docker run -v /path/to/audio:/audio -v /path/to/output:/output ...

# Use GPU if available
docker run --gpus all ...
```

### For APIs
```bash
# Compress audio first
ffmpeg -i audio.ogg -b:a 64k compressed.ogg

# Batch API calls when possible
```

## Reference: PEP 668 Workarounds

### Official Recommendations
1. Use virtual environments
2. Use `pipx` for applications
3. Use `--user` flag
4. Use system package manager when possible

### pipx Alternative
```bash
# Install pipx
sudo apt-get install pipx
pipx ensurepath

# Install Whisper with pipx
pipx install openai-whisper

# Run
whisper audio.ogg
```

### Conda/Mamba
```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create environment
conda create -n whisper python=3.10
conda activate whisper
pip install openai-whisper
```

## Emergency: Quick Transcription Needed

If you need transcription immediately and nothing is installed:

1. **Convert to text manually:** Play audio and type
2. **Use online service:** uploadfiles.io, vocaroo.com
3. **Mobile app:** Use phone's voice-to-text
4. **Ask for text version:** Request user to type instead

Then work on proper installation for future audio.
