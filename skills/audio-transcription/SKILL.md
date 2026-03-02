---
name: audio-transcription
description: "Transcribe audio files to text using various methods. Use when: (1) User sends audio messages (OGG, MP3, WAV, etc.) that need transcription, (2) Processing voice notes or recordings, (3) Converting speech to text for documentation, (4) Handling audio files in workflows that require text input."
---

# Audio Transcription

## Overview

This skill provides methods for transcribing audio files to text. Since OpenClaw agents don't have built-in speech-to-text capabilities, this skill outlines approaches for handling audio files through external tools, APIs, or conversion workflows.

## Quick Start: Audio File Handling

When you receive an audio file:

1. **Identify the format:** Check file extension (.ogg, .mp3, .wav, .m4a, etc.)
2. **Read metadata:** Use `read` tool on the audio file to see header information
3. **Choose transcription method:** Based on available tools and file characteristics

## Available Transcription Methods

### Method 1: API-Based Transcription (Recommended)

**When to use:** When you have access to speech-to-text APIs (OpenAI Whisper, Google Cloud Speech-to-Text, etc.)

**Workflow:**
1. Convert audio to compatible format if needed (WAV, MP3)
2. Upload to API endpoint
3. Process response and extract transcription

**Example API call structure:**
```python
# Pseudocode for OpenAI Whisper API
import openai

audio_file = open("audio.ogg", "rb")
transcript = openai.Audio.transcribe(
    model="whisper-1",
    file=audio_file,
    response_format="text"
)
```

### Method 2: Local Whisper Installation

**When to use:** When you can install and run Whisper locally

**Setup:**
```bash
# Install Whisper
pip install openai-whisper

# Install FFmpeg (if not already installed)
sudo apt-get install ffmpeg
```

**Usage:**
```bash
whisper audio.ogg --model base --language en --output_format txt
```

### Method 3: Google Cloud Speech-to-Text

**When to use:** When you have Google Cloud credentials

**Setup:**
```bash
pip install google-cloud-speech
```

**Configuration requires:**
- Service account credentials
- Project ID setup
- API enablement

### Method 4: FFmpeg + Basic Processing

**When to use:** For simple audio conversion when transcription isn't available

**Workflow:**
1. Convert to standard format
2. Extract metadata
3. Provide file details to user for manual processing

```bash
# Convert OGG to WAV
ffmpeg -i input.ogg output.wav

# Get audio information
ffmpeg -i input.ogg
```

## Common Audio Formats

### OGG (Opus)
- Common in Telegram voice messages
- Container format with Opus audio codec
- May need conversion for some APIs

### MP3
- Widely supported
- Most APIs accept MP3 directly

### WAV
- Uncompressed, high quality
- Large file size
- Universally compatible

### M4A/AAC
- Apple format
- May need conversion

## Workflow Decision Tree

```
Received audio file
    ↓
Can you transcribe directly? → Yes → Transcribe with available method
    ↓ No
Can you install tools? → Yes → Install Whisper/FFmpeg and transcribe
    ↓ No  
Can you use API? → Yes → Use API service (requires credentials)
    ↓ No
Convert and describe → Convert to standard format, provide details to user
```

## Handling Telegram Audio Messages

Telegram often sends OGG files with Opus codec. Typical path pattern:
```
/home/ubuntu/.openclaw/media/inbound/file_0---[uuid].ogg
```

**Steps:**
1. Read file header to confirm format
2. Check if transcription is possible with available tools
3. If not, inform user and suggest alternatives

## Scripts and Utilities

### `scripts/transcribe_audio.py`
Main transcription script that tries multiple methods in order:
1. Check for local Whisper installation
2. Fall back to API if configured
3. Provide conversion options as last resort

### `scripts/convert_audio.py`
Audio format conversion utility using FFmpeg.

### `scripts/audio_metadata.py`
Extract and display audio file metadata.

## References

See `references/audio_formats.md` for detailed format specifications and compatibility matrices.

See `references/api_setup.md` for API configuration guides (OpenAI, Google Cloud, etc.).

## Troubleshooting

### Issue: "No speech-to-text capability"
**Solution:** This is the default state. Use this skill to implement transcription through external tools.

### Issue: Audio format not supported
**Solution:** Convert to WAV or MP3 using FFmpeg:
```bash
ffmpeg -i input.ogg -acodec pcm_s16le -ar 16000 output.wav
```

### Issue: Poor transcription quality
**Solutions:**
- Use larger Whisper models (medium, large)
- Specify language parameter
- Clean audio with noise reduction
- Ensure proper sample rate (16kHz recommended)

### Issue: Large file size
**Solution:** Compress or segment audio before processing.

## Integration with OpenClaw Workflow

When you receive an audio file in OpenClaw:

1. **Acknowledge receipt:** "Received audio file, processing..."
2. **Attempt transcription:** Using available methods
3. **Provide results or alternatives:**
   - Success: Provide transcript
   - Partial: Provide what you could extract + suggestions
   - Failure: Explain limitations and suggest workarounds

## Example User Interactions

**User:** *sends audio file*
**Assistant:** "I received your audio message. Let me transcribe it for you..."

**User:** "Can you transcribe this voice note?"
**Assistant:** "I'll need to use speech-to-text tools. Let me check what's available..."

**User:** "What did I say in the audio?"
**Assistant:** "I can't transcribe audio directly, but I can help you set up transcription tools or convert the file for manual processing."
