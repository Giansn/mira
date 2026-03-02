---
name: multimedia-processing
description: "Process audio, images, and video files. Use when: (1) User sends audio messages that need transcription, (2) Images require description or OCR, (3) Video files need processing, (4) Multimedia content needs analysis or conversion."
---

# Multimedia Processing

## Overview

This skill provides tools and workflows for handling multimedia files (audio, images, video) when OpenClaw agents can't process them directly. It includes practical scripts for common tasks and fallback strategies.

## Quick Start

### When You Receive Multimedia Files

1. **Identify file type:** Check extension (.ogg, .jpg, .mp4, etc.)
2. **Read metadata:** Use `file` command or FFprobe
3. **Choose processing method:** Based on available tools
4. **Provide results or alternatives:** Transcript, description, or conversion

## Audio Processing

### Transcription Methods

**1. Local Whisper (Recommended if installed)**
```bash
# Install
pip install openai-whisper

# Transcribe
whisper audio.ogg --model base --language en --output_format txt
```

**2. FFmpeg Conversion (Fallback)**
```bash
# Convert to standard format
ffmpeg -i input.ogg -ar 16000 -ac 1 output.wav

# Get duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.ogg
```

**3. API-Based (OpenAI, Google Cloud)**
See `references/audio_apis.md` for API setup.

### Audio Analysis Scripts

- `scripts/audio_info.py`: Extract metadata and basic info
- `scripts/transcribe_audio.py`: Attempt multiple transcription methods
- `scripts/convert_audio.py`: Format conversion utilities

## Image Processing

### Basic Image Analysis

**1. File Information**
```bash
# Get basic info
file image.jpg
identify image.jpg  # If ImageMagick installed

# Get dimensions
identify -format "%wx%h" image.jpg
```

**2. OCR (Optical Character Recognition)**
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr

# Extract text
tesseract image.jpg output -l eng
```

**3. Image Description (AI-based)**
Requires vision-capable API (OpenAI GPT-4V, Claude 3.5, etc.)

### Image Analysis Scripts

- `scripts/image_info.py`: Extract metadata and dimensions
- `scripts/ocr_image.py`: Perform OCR on images
- `scripts/convert_image.py`: Format conversion and resizing

## Video Processing

### Basic Video Operations

**1. Extract Frames**
```bash
# Extract frame at 10 seconds
ffmpeg -i video.mp4 -ss 00:00:10 -vframes 1 frame.jpg

# Extract all frames
ffmpeg -i video.mp4 frames/frame_%04d.jpg
```

**2. Get Video Information**
```bash
ffprobe -v quiet -print_format json -show_streams -show_format video.mp4
```

**3. Convert Formats**
```bash
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
```

### Video Analysis Scripts

- `scripts/video_info.py`: Extract video metadata
- `scripts/extract_frames.py`: Extract frames at intervals
- `scripts/convert_video.py`: Format conversion

## Common Workflows

### Workflow 1: Audio Message Processing
```
Receive audio file
    ↓
Check if transcription possible → Yes → Transcribe
    ↓ No
Convert to standard format → Provide file info
    ↓
Suggest manual processing
```

### Workflow 2: Image Analysis
```
Receive image file
    ↓
Check if OCR needed → Yes → Run Tesseract
    ↓ No
Check if description needed → Yes → Use vision API if available
    ↓ No
Provide basic metadata
```

### Workflow 3: System Check for Multimedia Tools
```
Check available tools:
1. FFmpeg/FFprobe
2. ImageMagick
3. Tesseract OCR
4. Whisper
5. Vision APIs
```

## Troubleshooting

### Issue: "Command not found"
**Solution:** Install missing tools:
```bash
# FFmpeg
sudo apt-get install ffmpeg

# ImageMagick
sudo apt-get install imagemagick

# Tesseract
sudo apt-get install tesseract-ocr

# Whisper
pip install openai-whisper
```

### Issue: File format not supported
**Solution:** Convert to standard format:
- Audio: WAV or MP3 (16kHz mono recommended)
- Images: JPEG or PNG
- Video: MP4 (H.264/AAC)

### Issue: Poor quality results
**Solutions:**
- Audio: Increase sample rate, reduce noise
- Images: Improve resolution, adjust contrast
- OCR: Pre-process images (deskew, binarize)

## Integration with OpenClaw

### Automatic Processing
Configure OpenClaw to automatically process incoming media:
```json
{
  "media": {
    "autoTranscribeAudio": true,
    "autoOCRImages": false,
    "maxFileSize": 10485760
  }
}
```

### Fallback Strategies
1. **Primary:** Use installed tools
2. **Secondary:** Convert and provide metadata
3. **Tertiary:** Suggest manual processing

## References

- `references/audio_apis.md`: API setup for speech-to-text
- `references/image_apis.md`: Vision API configurations
- `references/tool_installation.md`: Installation guides for multimedia tools
- `references/file_formats.md`: Supported formats and conversions

## Examples

### Example 1: Telegram Audio Message
```bash
# File: /home/ubuntu/.openclaw/media/inbound/file_0---[uuid].ogg
# Process with:
python3 scripts/audio_info.py /home/ubuntu/.openclaw/media/inbound/file_0---[uuid].ogg
```

### Example 2: Image with Text
```bash
# File: screenshot.jpg
# Extract text:
python3 scripts/ocr_image.py screenshot.jpg --language eng
```

### Example 3: Video Processing
```bash
# File: recording.mp4
# Extract key frames:
python3 scripts/extract_frames.py recording.mp4 --interval 5
```
