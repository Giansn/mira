# Audio Formats and Compatibility

## Common Audio Formats in Messaging Apps

### Telegram
- **Primary format:** OGG container with Opus codec
- **File pattern:** `file_0---[uuid].ogg`
- **Typical specs:** 48kHz, mono, Opus @ ~64kbps
- **Transcription compatibility:** May need conversion to WAV/MP3

### WhatsApp
- **Primary format:** OGG with Opus or MP4 with AAC
- **Variations:** Depends on device and settings
- **Transcription compatibility:** Usually good with modern APIs

### Signal
- **Format:** MP4 with AAC
- **Specs:** Variable bitrate
- **Transcription compatibility:** Good

### iMessage
- **Format:** CAF (Core Audio Format) or M4A
- **Transcription compatibility:** May need conversion

## Format Conversion Guide

### OGG (Opus) to WAV
```bash
ffmpeg -i input.ogg -acodec pcm_s16le -ar 16000 output.wav
```

### OGG to MP3
```bash
ffmpeg -i input.ogg -acodec libmp3lame -ab 128k output.mp3
```

### MP4/M4A to WAV
```bash
ffmpeg -i input.m4a -acodec pcm_s16le output.wav
```

### CAF to WAV
```bash
ffmpeg -i input.caf output.wav
```

## Optimal Transcription Settings

### Sample Rate
- **Recommended:** 16000 Hz (16kHz)
- **Acceptable range:** 8000-48000 Hz
- **Whisper preference:** 16000 Hz

### Channels
- **Recommended:** Mono (single channel)
- **Conversion to mono:**
  ```bash
  ffmpeg -i input.wav -ac 1 output_mono.wav
  ```

### Bit Depth
- **Recommended:** 16-bit PCM
- **Format:** Signed 16-bit little-endian (s16le)

### File Size Optimization
For large files:
```bash
# Trim to first 5 minutes if only need beginning
ffmpeg -i input.wav -t 300 trimmed.wav

# Reduce sample rate
ffmpeg -i input.wav -ar 16000 reduced.wav
```

## API Compatibility Matrix

### OpenAI Whisper API
- **Formats:** MP3, MP4, M4A, WAV, FLAC
- **Max file size:** 25 MB
- **Languages:** Automatic detection or specified
- **Best practice:** Convert to MP3 or WAV, 16kHz mono

### Google Cloud Speech-to-Text
- **Formats:** FLAC, LINEAR16, MULAW, AMR, AMR_WB, OGG_OPUS, SPEEX_WITH_HEADER_BYTE
- **Max file size:** 10 MB (60 MB with long-running)
- **Best practice:** Use OGG_OPUS for Telegram files directly

### AWS Transcribe
- **Formats:** MP3, MP4, WAV, FLAC, OGG, AMR, WebM
- **Max file size:** 2 GB
- **Best practice:** MP3 or WAV

### Local Whisper
- **Formats:** All FFmpeg-supported formats
- **No size limit** (system memory dependent)
- **Best practice:** Convert to WAV for consistency

## FFmpeg Command Reference

### Basic Information
```bash
# Get file info
ffmpeg -i input.ogg

# Get duration only
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.ogg
```

### Quality Settings
```bash
# High quality MP3
ffmpeg -i input.ogg -q:a 2 output.mp3

# Balanced quality/size
ffmpeg -i input.ogg -b:a 128k output.mp3

# Optimized for speech
ffmpeg -i input.ogg -acodec libmp3lame -ab 64k -ar 16000 -ac 1 output.mp3
```

### Batch Processing
```bash
# Convert all OGG files in directory
for file in *.ogg; do
    ffmpeg -i "$file" "${file%.ogg}.wav"
done
```

## Troubleshooting Conversion Issues

### Issue: "Invalid data found when processing input"
**Cause:** Corrupted file or unsupported codec
**Solution:** Try different conversion approach or obtain file again

### Issue: "Codec not supported"
**Cause:** Unusual codec variant
**Solution:** List available codecs: `ffmpeg -codecs`
**Workaround:** Convert to PCM WAV first, then to target format

### Issue: File too large for API
**Solutions:**
1. Compress audio: `ffmpeg -i input.wav -b:a 64k compressed.mp3`
2. Split file: `ffmpeg -i input.wav -f segment -segment_time 300 -c copy output_%03d.wav`
3. Reduce sample rate: `ffmpeg -i input.wav -ar 8000 reduced.wav`

### Issue: Poor transcription accuracy
**Check:**
1. Sample rate (should be 16000 Hz for speech)
2. Background noise (consider noise reduction)
3. Audio levels (normalize if too quiet/loud)
4. Multiple speakers (may need speaker diarization)

## Normalization and Cleaning

### Volume Normalization
```bash
# Normalize to -16 dB LUFS (broadcast standard)
ffmpeg -i input.wav -af loudnorm=I=-16:LRA=11:TP=-1.5 output.wav
```

### Noise Reduction (basic)
```bash
# Simple noise reduction (requires noise profile)
ffmpeg -i input.wav -af afftdn=nf=-25 output.wav
```

### Silence Removal
```bash
# Remove silence longer than 1 second
ffmpeg -i input.wav -af silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-30dB output.wav
```

## Metadata Extraction

### Using FFprobe
```bash
# JSON output with all metadata
ffprobe -v quiet -print_format json -show_streams -show_format input.ogg

# Specific fields
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=noprint_wrappers=1 input.ogg
```

### Common Metadata Fields
- `duration`: Length in seconds
- `size`: File size in bytes
- `bit_rate`: Average bitrate
- `sample_rate`: Audio sample rate
- `channels`: Number of audio channels
- `codec_name`: Audio codec used
