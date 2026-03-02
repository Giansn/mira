# API Setup Guides for Speech-to-Text

## OpenAI Whisper API

### Prerequisites
- OpenAI API key with access to Whisper
- Sufficient credits/balance

### Installation
```bash
pip install openai
```

### Configuration
```python
import openai
openai.api_key = "your-api-key-here"
```

### Basic Usage
```python
def transcribe_with_whisper(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            response_format="text"  # or "json", "srt", "vtt"
        )
    return transcript
```

### Advanced Options
```python
transcript = openai.Audio.transcribe(
    model="whisper-1",
    file=audio_file,
    language="en",  # Optional: specify language
    prompt="Transcribe this audio:",  # Optional: context prompt
    temperature=0.0,  # Optional: control randomness
    response_format="verbose_json"  # Detailed output
)
```

### Error Handling
```python
try:
    transcript = openai.Audio.transcribe(...)
except openai.error.AuthenticationError:
    print("Invalid API key")
except openai.error.RateLimitError:
    print("Rate limit exceeded")
except openai.error.APIConnectionError:
    print("Network error")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Google Cloud Speech-to-Text

### Prerequisites
- Google Cloud project with Speech-to-Text API enabled
- Service account credentials JSON file

### Installation
```bash
pip install google-cloud-speech
```

### Authentication
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

Or in code:
```python
from google.cloud import speech_v1
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "/path/to/credentials.json"
)
client = speech_v1.SpeechClient(credentials=credentials)
```

### Basic Usage
```python
def transcribe_with_google(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech_v1.RecognitionAudio(content=content)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    
    response = client.recognize(config=config, audio=audio)
    
    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)
    
    return " ".join(transcripts)
```

### Long Audio Files (Async)
```python
def transcribe_long_audio(gcs_uri):
    audio = speech_v1.RecognitionAudio(uri=gcs_uri)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )
    
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)
    
    return response
```

## AWS Transcribe

### Prerequisites
- AWS account with Transcribe access
- AWS credentials configured

### Installation
```bash
pip install boto3
```

### Configuration
```python
import boto3

client = boto3.client(
    'transcribe',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-east-1'
)
```

### Basic Usage (Async)
```python
def start_transcription_job(job_name, media_uri):
    response = client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
    return response

def get_transcription_results(job_name):
    response = client.get_transcription_job(
        TranscriptionJobName=job_name
    )
    
    if response['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        # Download and parse transcript
        return transcript_uri
    else:
        return None
```

## Local Whisper Installation

### System Requirements
- Python 3.8+
- FFmpeg installed
- Sufficient RAM/VRAM for model size

### Installation
```bash
# Install Whisper
pip install openai-whisper

# Or from source
pip install git+https://github.com/openai/whisper.git
```

### Basic Usage
```python
import whisper

def transcribe_local(audio_file_path):
    # Load model (choose based on accuracy/speed tradeoff)
    model = whisper.load_model("base")  # tiny, base, small, medium, large
    
    # Transcribe
    result = model.transcribe(audio_file_path)
    return result["text"]
```

### Advanced Options
```python
result = model.transcribe(
    audio_file_path,
    language="en",  # Specify language
    task="transcribe",  # or "translate"
    fp16=False,  # Use FP16 if GPU available
    verbose=True  # Show progress
)
```

### Model Comparison
- **tiny**: 39M params, ~1GB RAM, fastest, lowest accuracy
- **base**: 74M params, ~1GB RAM, good speed/accuracy balance
- **small**: 244M params, ~2GB RAM, better accuracy
- **medium**: 769M params, ~5GB RAM, high accuracy
- **large**: 1550M params, ~10GB RAM, highest accuracy

## API Comparison Table

| Feature | OpenAI Whisper | Google Cloud | AWS Transcribe | Local Whisper |
|---------|---------------|--------------|----------------|---------------|
| Cost | $0.006/min | $0.024/min (standard) | $0.024/min | Free (once installed) |
| Max file size | 25 MB | 10 MB (60 MB async) | 2 GB | System dependent |
| Languages | 99+ | 125+ | 79+ | 99+ |
| Real-time | No | Yes | Yes | No |
| Speaker diarization | No | Yes | Yes | No |
| Custom models | No | Yes | Yes | No (fine-tuning possible) |
| Setup complexity | Low | Medium | Medium | High (installation) |

## Security Considerations

### API Keys
- Never hardcode API keys in scripts
- Use environment variables or secure credential stores
- Rotate keys regularly
- Set usage limits and alerts

### Audio Data Privacy
- Check API provider's data retention policies
- For sensitive audio, consider local processing
- Some APIs offer data redaction features

### Cost Management
- Set budget alerts
- Monitor usage regularly
- Consider caching transcripts for repeated audio
- Use smaller models/files when appropriate

## Integration with OpenClaw

### Environment Configuration
Add API keys to OpenClaw environment:
```bash
# In shell profile
export OPENAI_API_KEY="sk-..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/creds.json"

# Or in OpenClaw config
# openclaw.json environment section
```

### Fallback Strategy
Implement tiered approach:
1. Try local Whisper if installed
2. Fall back to OpenAI Whisper API
3. Then Google Cloud
4. Finally, AWS or manual conversion

### Error Recovery
- Implement retry logic with exponential backoff
- Log transcription attempts and failures
- Provide clear error messages to users
- Suggest alternative approaches when APIs fail
