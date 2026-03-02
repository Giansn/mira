# Audio Response Protocol

## Core Rule
**Always reply with audio when addressed in audio. Send voice message only, nothing else.**

## Protocol Details

### 1. **Input Detection**
- User sends audio message → Trigger audio response
- Text messages → Text responses (unless specified otherwise)
- Mixed input → Follow primary input type

### 2. **Response Process**
```
Audio Input → Transcription → Processing → TTS → Audio Output
```

### 3. **Label Format**
```
[Topic] [Duration] [Key Point]
```
**Examples:**
- `[World Politics] [25s] US elections, Ukraine war, China-Taiwan tensions`
- `[Technical] [12s] Fixed voice quality with Edge TTS`
- `[Response] [8s] Received your audio message`

### 4. **Metadata**
- **Artist:** Always "Mira" (replaces "Unknown Artist")
- **Title:** Use label format
- **File format:** MP3 (Edge TTS default)
- **Voice:** Edge TTS neural voice (natural, expressive)

## Technical Implementation

### TTS System
- **Provider:** Edge TTS (Microsoft neural text-to-speech)
- **Quality:** Natural, human-like voice
- **Configuration:** No API key required
- **Voice:** Default neural voice (adjustable)

### Transcription
- **Tool:** Whisper (OpenAI)
- **Model:** Tiny (fast, accurate enough)
- **Language:** Auto-detection (supports multiple languages)

### File Handling
1. Create temporary audio file via TTS
2. Copy to workspace for Telegram sending
3. Clean up temporary files
4. Send with proper metadata

## Workflow Example

**User sends audio:** "What's the weather?"
**Process:**
1. **Check MD file:** Read `audio_behaviour.md` to confirm protocol
2. **Status indicator:** Show "recording audio message" or typing indicator
3. **Transcribe:** "What's the weather?"
4. **Generate response:** "Current weather is sunny, 22°C"
5. **TTS conversion:** Create audio file via Edge TTS
6. **Label:** Generate `[Weather] [5s] Sunny, 22 degrees`
7. **Send audio:** With label, artist: "Mira"
8. **Clear indicators:** Remove status/typing indicators

## Edge Cases

### Transcription Failure
- Use generic response: "Received your audio message"
- Label: `[Audio] [5s] Response to your message`

### TTS Failure
- Fallback systems available
- Report issue in next response

### Unknown Topic
- Label: `[Response] [Duration] [First sentence of response]`

## Voice Profile

### Current Configuration
- **Provider:** Edge TTS (Microsoft neural text-to-speech)
- **Voice:** `en-US-MichelleNeural` (female, natural)
- **Pitch:** Slightly lowered for more organic sound
- **Rate:** Normal speaking pace
- **Intonation:** Expressive, natural rhythm
- **Quality:** Neural TTS (human-like, not robotic)

### Audio Characteristics
- **Tone:** Warm, clear, professional
- **Pace:** 150-160 words per minute
- **Emphasis:** Natural sentence stress patterns
- **Clarity:** High intelligibility, neutral accent

### Technical Settings
- **Output format:** MP3, 24kHz, 48kbitrate, mono
- **Sample rate:** 24000 Hz
- **Bitrate:** 48 kbps
- **Channels:** Mono (optimized for voice)

### Quality Notes
- **Current:** Much improved over espeak (robotic)
- **Organic:** Natural pitch variation, not monotone
- **Intonation:** Proper sentence melody and emphasis
- **Lower pitch:** Adjusted from default for more natural sound

### Configuration Source
- **Default:** Edge TTS with neural voice
- **No API key required**
- **Adjustable:** Can modify pitch, rate, voice selection
- **Current settings optimized for:** Clarity, naturalness, listenability

## Configuration Notes

### Voice Quality
- Default: Edge TTS neural voice
- Adjustable: Pitch, rate, specific voice
- Current: Natural, expressive intonation, slightly lowered pitch

### Performance
- Transcription: ~2-5 seconds
- TTS: ~3-7 seconds  
- Total response time: ~5-12 seconds

## Integration

### Telegram Specific
- Send as audio file (not voice note)
- Metadata: Artist = "Mira", Title = label
- Works with Telegram auto-playback settings

### Status Indicators
1. **On audio receipt:** Show "recording audio message" if Telegram API supports it
2. **Fallback:** Show typing indicator immediately upon receiving audio
3. **During processing:** Maintain status indicator until audio sent
4. **After sending:** Clear indicators

### Protocol Enforcement
- **Mandatory check:** Read `audio_behaviour.md` before processing any audio
- **Verification:** Ensure current response follows documented protocol
- **Updates:** Modify MD file first if protocol changes needed

### Other Platforms
- Adaptable to any platform supporting audio
- Same core protocol applies

## Updates & Changes

### 2026-03-01
- **Protocol established:** Audio in → Audio out only
- **TTS upgrade:** Switched from espeak (robotic) to Edge TTS (neural, natural)
- **Voice profile:** Configured for lower, more organic pitch with better intonation
- **Label system:** Implemented `[Topic] [Duration] [Key Point]` format
- **Metadata:** Artist always "Mira" (replaces "Unknown Artist")
- **Documentation:** Created audio_behaviour.md with full protocol details

## Testing
Send audio message to verify:
1. Audio response received
2. Label present and informative
3. Artist shows as "Mira"
4. No text accompanying audio

## Mandatory Protocol Check
**Before processing ANY audio message:**
1. **Read:** `audio_behaviour.md` file
2. **Verify:** Current response follows documented protocol
3. **Update:** If protocol needs changes, update MD file first
4. **Status:** Show Telegram indicators as documented

### Check Procedure
```
Audio Received → Read MD File → Show Status → Process → Send → Clear Status
```

### Telegram Status Implementation
- **Preferred:** "Recording audio message" (if API supports)
- **Fallback:** Typing indicator
- **Timing:** Start immediately on audio receipt
- **Duration:** Maintain until audio sent
- **Clear:** Remove indicators after sending

## Maintenance
- Monitor TTS quality
- Update transcription accuracy
- Adjust voice parameters as needed
- Document any protocol changes
- Ensure MD file check happens every time
