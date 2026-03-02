#!/usr/bin/env python3
"""
Audio transcription utility for OpenClaw.

This script attempts to transcribe audio files using available methods:
1. Local Whisper installation
2. OpenAI Whisper API
3. Google Cloud Speech-to-Text
4. Basic conversion and metadata extraction as fallback
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import optional dependencies
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from google.cloud import speech_v1
    from google.oauth2 import service_account
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    import whisper
    HAS_LOCAL_WHISPER = True
except ImportError:
    HAS_LOCAL_WHISPER = False


def check_ffmpeg() -> bool:
    """Check if FFmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_audio_info(audio_path: str) -> Dict[str, Any]:
    """Get audio file information using FFprobe."""
    if not check_ffmpeg():
        return {"error": "FFmpeg not available"}
    
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        info = {
            "format": data.get("format", {}).get("format_name", "unknown"),
            "duration": float(data.get("format", {}).get("duration", 0)),
            "size": int(data.get("format", {}).get("size", 0)),
            "bit_rate": int(data.get("format", {}).get("bit_rate", 0)),
        }
        
        # Audio stream info
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                info.update({
                    "codec": stream.get("codec_name", "unknown"),
                    "sample_rate": int(stream.get("sample_rate", 0)),
                    "channels": int(stream.get("channels", 0)),
                    "channel_layout": stream.get("channel_layout", "unknown"),
                })
                break
        
        return info
    except Exception as e:
        return {"error": f"Failed to get audio info: {e}"}


def convert_audio(input_path: str, output_path: Optional[str] = None, 
                  target_format: str = "wav", sample_rate: int = 16000) -> Optional[str]:
    """Convert audio file to target format using FFmpeg."""
    if not check_ffmpeg():
        print("FFmpeg not available for conversion")
        return None
    
    if output_path is None:
        # Create temp file
        suffix = f".{target_format}"
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        output_path = temp_file.name
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", str(sample_rate),  # Sample rate
            "-ac", "1",  # Mono
            "-y",  # Overwrite output
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")
        return None


def transcribe_local_whisper(audio_path: str, model_size: str = "base") -> Optional[str]:
    """Transcribe using local Whisper installation."""
    if not HAS_LOCAL_WHISPER:
        print("Local Whisper not installed")
        return None
    
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        return result.get("text", "")
    except Exception as e:
        print(f"Local Whisper transcription failed: {e}")
        return None


def transcribe_openai_api(audio_path: str, api_key: Optional[str] = None) -> Optional[str]:
    """Transcribe using OpenAI Whisper API."""
    if not HAS_OPENAI:
        print("OpenAI library not installed")
        return None
    
    # Get API key from environment or parameter
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("OpenAI API key not provided")
        return None
    
    openai.api_key = api_key
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    except Exception as e:
        print(f"OpenAI API transcription failed: {e}")
        return None


def transcribe_google_cloud(audio_path: str, credentials_path: Optional[str] = None) -> Optional[str]:
    """Transcribe using Google Cloud Speech-to-Text."""
    if not HAS_GOOGLE:
        print("Google Cloud library not installed")
        return None
    
    # Set up credentials
    if credentials_path is None:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not credentials_path or not os.path.exists(credentials_path):
        print("Google Cloud credentials not found")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = speech_v1.SpeechClient(credentials=credentials)
        
        with open(audio_path, "rb") as audio_file:
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
    except Exception as e:
        print(f"Google Cloud transcription failed: {e}")
        return None


def transcribe_audio(audio_path: str, method: str = "auto", **kwargs) -> Dict[str, Any]:
    """
    Main transcription function.
    
    Args:
        audio_path: Path to audio file
        method: "auto", "local", "openai", "google", or "info"
        **kwargs: Additional parameters for specific methods
    
    Returns:
        Dictionary with transcription results and metadata
    """
    result = {
        "success": False,
        "method": method,
        "transcript": None,
        "audio_info": None,
        "error": None,
        "converted_path": None
    }
    
    # Check if file exists
    if not os.path.exists(audio_path):
        result["error"] = f"Audio file not found: {audio_path}"
        return result
    
    # Get audio information
    audio_info = get_audio_info(audio_path)
    result["audio_info"] = audio_info
    
    if "error" in audio_info:
        result["error"] = audio_info["error"]
        return result
    
    # Convert if needed (for APIs that require specific formats)
    converted_path = None
    if audio_info.get("format") not in ["wav", "mp3"]:
        print(f"Converting {audio_info.get('format')} to WAV for compatibility...")
        converted_path = convert_audio(audio_path, target_format="wav")
        if converted_path:
            result["converted_path"] = converted_path
            audio_path = converted_path  # Use converted file
    
    # Choose transcription method
    if method == "auto":
        # Try methods in order of preference
        methods_to_try = []
        
        if HAS_LOCAL_WHISPER:
            methods_to_try.append(("local", transcribe_local_whisper))
        
        if HAS_OPENAI and os.environ.get("OPENAI_API_KEY"):
            methods_to_try.append(("openai", transcribe_openai_api))
        
        if HAS_GOOGLE and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            methods_to_try.append(("google", transcribe_google_cloud))
        
        if not methods_to_try:
            result["error"] = "No transcription methods available"
            return result
        
        # Try each method until one succeeds
        for method_name, transcribe_func in methods_to_try:
            print(f"Trying {method_name} transcription...")
            transcript = transcribe_func(audio_path)
            if transcript:
                result["method"] = method_name
                result["transcript"] = transcript
                result["success"] = True
                break
        
        if not result["success"]:
            result["error"] = "All transcription methods failed"
    
    elif method == "local":
        transcript = transcribe_local_whisper(audio_path, **kwargs)
        if transcript:
            result["transcript"] = transcript
            result["success"] = True
        else:
            result["error"] = "Local transcription failed"
    
    elif method == "openai":
        transcript = transcribe_openai_api(audio_path, **kwargs)
        if transcript:
            result["transcript"] = transcript
            result["success"] = True
        else:
            result["error"] = "OpenAI transcription failed"
    
    elif method == "google":
        transcript = transcribe_google_cloud(audio_path, **kwargs)
        if transcript:
            result["transcript"] = transcript
            result["success"] = True
        else:
            result["error"] = "Google Cloud transcription failed"
    
    elif method == "info":
        # Just return audio info
        result["success"] = True
    
    else:
        result["error"] = f"Unknown method: {method}"
    
    # Clean up converted file if we created one
    if converted_path and os.path.exists(converted_path):
        try:
            os.unlink(converted_path)
        except:
            pass
    
    return result


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcribe audio files")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--method", choices=["auto", "local", "openai", "google", "info"],
                       default="auto", help="Transcription method")
    parser.add_argument("--output", "-o", help="Output file for transcript")
    parser.add_argument("--model", default="base", help="Whisper model size (for local)")
    parser.add_argument("--api-key", help="OpenAI API key (overrides environment)")
    parser.add_argument("--credentials", help="Google Cloud credentials path")
    
    args = parser.parse_args()
    
    # Prepare kwargs for transcription
    kwargs = {}
    if args.method == "local":
        kwargs["model_size"] = args.model
    elif args.method == "openai" and args.api_key:
        kwargs["api_key"] = args.api_key
    elif args.method == "google" and args.credentials:
        kwargs["credentials_path"] = args.credentials
    
    # Transcribe
    result = transcribe_audio(args.audio_file, args.method, **kwargs)
    
    # Output results
    if args.output:
        with open(args.output, "w") as f:
            if result["transcript"]:
                f.write(result["transcript"])
            else:
                json.dump(result, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        if result["success"]:
            if result["transcript"]:
                print("\n=== TRANSCRIPT ===\n")
                print(result["transcript"])
                print("\n==================\n")
            
            print("Audio Information:")
            for key, value in result["audio_info"].items():
                print(f"  {key}: {value}")
            
            print(f"\nMethod used: {result['method']}")
        else:
            print(f"Error: {result['error']}")
            print("\nAudio Information:")
            for key, value in result["audio_info"].items():
                print(f"  {key}: {value}")
    
    # Return exit code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
