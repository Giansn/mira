---
name: audio-response
description: "Respond to audio messages with audio-only responses. Use when: (1) User sends audio message, (2) Protocol requires audio-only response, (3) Need to convert text to speech, (4) Label audio responses usefully."
---

# Audio Response Protocol

## Overview

This skill implements the audio-only response protocol: **When user inputs audio, respond with audio only.** It handles transcription, processing, TTS conversion, and labeled audio delivery.

## Protocol Rules

### 1. **Input:** User sends audio message
### 2. **Processing:**
   - Transcribe audio using Whisper
   - Process the request
   - Generate text response
   - Convert to audio via TTS
### 3. **Output:** Send audio-only response with useful label

## Labeling Format

Audio responses are labeled with:
```
[Topic] [Duration] [Key Point]
```

**Examples:**
- `[Disk Space] [15s] EBS volume solved capacity crisis`
- `[Transcription] [8s] Whisper now working with 95% accuracy`
- `[TTS Setup] [12s] espeak configured for basic audio responses`

## TTS Options

### 1. **Local (espeak)** - Available now
```bash
echo "Response text" | espeak --stdout > response.wav
```
- **Pros:** No API, works offline, fast
- **Cons:** Robotic voice, basic quality

### 2. **OpenAI TTS** - Needs API key
```python
from openai import OpenAI
client = OpenAI()
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Response text"
)
```

### 3. **ElevenLabs** - Best quality
```python
from elevenlabs import generate, play
audio = generate(text="Response text", voice="Rachel")
```

### 4. **Google TTS** - Free, requires internet
```python
from gtts import gTTS
tts = gTTS(text="Response text", lang="en")
tts.save("response.mp3")
```

## Implementation Scripts

### `scripts/audio_responder.py`
Main script that:
1. Receives audio file path
2. Transcribes using Whisper
3. Generates response
4. Converts to audio
5. Sends with label

### `scripts/tts_engine.py`
TTS conversion with fallback:
1. Try ElevenLabs if configured
2. Fall back to OpenAI TTS
3. Fall back to Google TTS
4. Final fallback: espeak

### `scripts/label_generator.py`
Generate useful labels:
- Extract topic from conversation
- Estimate duration
- Identify key point

## Workflow

```
User Audio → Transcription → Processing → Text Response → TTS → Labeled Audio Response
```

## Quick Start

### Using espeak (immediate):
```bash
python3 scripts/audio_responder.py \
  --audio /path/to/user_audio.ogg \
  --tts-engine espeak \
  --label-format "[{topic}] [{duration}s] {key_point}"
```

### Testing:
```bash
# Test TTS
echo "Audio response protocol is now active" | espeak --stdout > test.wav

# Test full workflow
python3 scripts/audio_responder.py --test
```

## Integration with OpenClaw

### Telegram Handler:
```python
def handle_telegram_audio(audio_path):
    # Transcribe
    transcript = transcribe_audio(audio_path)
    
    # Generate response
    response_text = generate_response(transcript)
    
    # Convert to audio
    audio_response = text_to_speech(response_text)
    
    # Send with label
    label = generate_label(transcript, response_text)
    send_audio_response(audio_response, label)
```

### Auto-Configuration:
Script checks and configures best available TTS:
1. Check for ElevenLabs API key
2. Check for OpenAI API key  
3. Check for Google TTS (internet)
4. Default to espeak

## Label Generation Examples

**Input:** "How did you fix the disk space issue?"
**Output Label:** `[Infrastructure] [18s] Added 50GB EBS volume, now 47GB free`

**Input:** "Can you transcribe audio now?"
**Output Label:** `[Capabilities] [10s] Whisper transcription working with 9 files processed`

**Input:** "What's next?"
**Output Label:** `[Planning] [14s] Fix Moltbook cron, set up auto-transcription`

## Error Handling

### TTS Failure:
- Fall back to next available engine
- If all fail, respond with text (breaking protocol, but informative)

### Transcription Failure:
- Use audio metadata (duration, format)
- Generic response: "Received your audio message"

### Label Generation Failure:
- Default label: `[Response] [{duration}s] Audio reply`

## Performance Notes

### Speed:
- **espeak:** ~1x realtime (fastest)
- **OpenAI TTS:** ~2-3s API call
- **ElevenLabs:** ~3-5s API call
- **Google TTS:** ~2-4s with internet

### Quality:
- **ElevenLabs:** Best (human-like)
- **OpenAI TTS:** Very good
- **Google TTS:** Good
- **espeak:** Basic (robotic)

## Configuration

### Environment Variables:
```bash
export ELEVENLABS_API_KEY="..."
export OPENAI_API_KEY="..."
export TTS_ENGINE="elevenlabs"  # or openai, google, espeak
```

### Config File (`~/.config/audio-response.json`):
```json
{
  "tts_engine": "espeak",
  "label_format": "[{topic}] [{duration}s] {key_point}",
  "fallback_engines": ["openai", "google", "espeak"],
  "max_duration": 30
}
```

## Testing the Protocol

Send an audio message to test:
1. System transcribes it
2. Processes request
3. Generates audio response
4. Sends with descriptive label

The first audio response will explain the TTS setup status.
