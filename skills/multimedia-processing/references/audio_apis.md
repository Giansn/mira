# Audio API Reference

## Available Speech-to-Text APIs

### 1. OpenAI Whisper API
**Best for:** High accuracy, multiple languages
**Cost:** $0.006 per minute
**Limits:** 25 MB file size, no real-time

**Setup:**
```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

**Usage:**
```python
import openai

with open("audio.ogg", "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file,
        response_format="text",
        language="en"  # Optional
    )
```

### 2. Google Cloud Speech-to-Text
**Best for:** Real-time, speaker diarization
**Cost:** $0.024 per minute (standard)
**Limits:** 10 MB (60 MB async)

**Setup:**
```bash
pip install google-cloud-speech
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

**Usage:**
```python
from google.cloud import speech_v1

client = speech_v1.SpeechClient()
config = speech_v1.RecognitionConfig(
    encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
    enable_automatic_punctuation=True,
)
```

### 3. AWS Transcribe
**Best for:** Large files, batch processing
**Cost:** $0.024 per minute
**Limits:** 2 GB file size

**Setup:**
```bash
pip install boto3
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

### 4. Local Whisper
**Best for:** Privacy, offline use
**Cost:** Free (compute resources)
**Limits:** System dependent

**Setup:**
```bash
pip install openai-whisper
sudo apt-get install ffmpeg
```

## Audio Format Compatibility

### Supported Formats by API

| API | MP3 | WAV | OGG | M4A | FLAC | WebM |
|-----|-----|-----|-----|-----|------|------|
| OpenAI Whisper | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Google Cloud | ✅ | ✅ | ✅ (Opus) | ✅ | ✅ | ✅ |
| AWS Transcribe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Local Whisper | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Recommended Settings
- **Sample rate:** 16000 Hz (16kHz)
- **Channels:** Mono (1 channel)
- **Bit depth:** 16-bit
- **Format:** WAV (PCM) or MP3 (128kbps)

## Conversion Commands

### OGG (Opus) to WAV
```bash
ffmpeg -i input.ogg -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

### MP4/M4A to WAV
```bash
ffmpeg -i input.m4a -acodec pcm_s16le -ar 16000 output.wav
```

### MP3 to WAV
```bash
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 16000 output.wav
```

## Error Handling

### Common API Errors

**OpenAI:**
- `401 Invalid Authentication` - Check API key
- `429 Rate limit exceeded` - Wait and retry
- `413 Request too large` - File > 25 MB

**Google Cloud:**
- `401 UNAUTHENTICATED` - Check credentials
- `429 RESOURCE_EXHAUSTED` - Quota exceeded
- `400 INVALID_ARGUMENT` - Audio format issue

### Fallback Strategies
1. Try local Whisper if installed
2. Convert format and retry
3. Split large files
4. Use different API

## Cost Optimization

### For Development/Testing
- Use local Whisper (free)
- Use short audio samples
- Mock API responses

### For Production
- Cache transcripts
- Compress audio before sending
- Use appropriate quality (16kHz vs 48kHz)
- Monitor usage with alerts

## Security Considerations

### Data Privacy
- **Sensitive data:** Use local processing
- **API providers:** Check data retention policies
- **Encryption:** Use TLS for API calls

### API Key Management
- Never commit keys to git
- Use environment variables
- Rotate keys regularly
- Set usage limits

## Performance Tips

### Faster Processing
1. **Pre-process audio:** Convert to optimal format
2. **Split long audio:** Process in parallel
3. **Use appropriate model:** Tiny/base for speed, large for accuracy
4. **Batch requests:** When possible

### Accuracy Improvement
1. **Clean audio:** Remove noise, normalize volume
2. **Specify language:** If known
3. **Add context:** Provide prompts for difficult terms
4. **Use larger models:** Medium/large for complex audio

## Integration Examples

### Telegram Audio Handler
```python
def handle_telegram_audio(audio_path):
    # Telegram sends OGG/Opus files
    if audio_path.endswith('.ogg'):
        # Convert to WAV for APIs
        wav_path = convert_ogg_to_wav(audio_path)
        return transcribe_audio(wav_path)
    else:
        return transcribe_audio(audio_path)
```

### Batch Processing
```python
def batch_transcribe(audio_files, api='openai'):
    results = {}
    for file in audio_files:
        try:
            results[file] = transcribe_audio(file, api=api)
        except Exception as e:
            results[file] = f"Error: {e}"
    return results
```

## Monitoring and Logging

### Track Usage
```python
import logging
from datetime import datetime

logging.basicConfig(filename='audio_transcription.log', level=logging.INFO)

def log_transcription(file, duration, api, success):
    logging.info(f"{datetime.now()}: {file} - {duration}s - {api} - {'Success' if success else 'Failed'}")
```

### Alert on Issues
```python
def check_api_health():
    # Test API connectivity
    # Alert if multiple failures
    # Fall back to alternative APIs
    pass
```
