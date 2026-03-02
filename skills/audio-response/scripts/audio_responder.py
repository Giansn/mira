#!/usr/bin/env python3
"""
Audio responder for audio-only response protocol.
"""

import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class AudioResponder:
    """Handle audio-in, audio-out protocol."""
    
    def __init__(self, tts_engine: str = "espeak"):
        self.tts_engine = tts_engine
        self.whisper_path = "/data/.venv/whisper/bin/whisper"
        
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using Whisper."""
        try:
            cmd = [
                self.whisper_path,
                audio_path,
                "--model", "tiny",
                "--language", "en",
                "--output_format", "txt"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find output file
                base_name = Path(audio_path).stem
                output_file = f"{base_name}.txt"
                
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        return f.read().strip()
                elif result.stdout:
                    # Try to extract from stdout
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if line.startswith('[') and '-->' in line:
                            # Extract transcript part
                            parts = line.split('] ')
                            if len(parts) > 1:
                                return parts[1].strip()
            return None
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def text_to_speech(self, text: str, output_path: str) -> bool:
        """Convert text to speech using configured engine."""
        if self.tts_engine == "espeak":
            return self._espeak_tts(text, output_path)
        else:
            print(f"TTS engine '{self.tts_engine}' not implemented, using espeak")
            return self._espeak_tts(text, output_path)
    
    def _espeak_tts(self, text: str, output_path: str) -> bool:
        """Convert text to speech using espeak."""
        try:
            # espeak command
            cmd = ["espeak", "--stdout", text]
            
            with open(output_path, 'wb') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                # Check if file was created and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
            
            return False
            
        except Exception as e:
            print(f"espeak TTS error: {e}")
            return False
    
    def estimate_duration(self, text: str) -> int:
        """Estimate audio duration in seconds (rough: 150 words/minute)."""
        words = len(text.split())
        seconds = max(3, int(words * 0.4))  # 150 wpm = 0.4 seconds per word
        return min(seconds, 60)  # Cap at 60 seconds
    
    def generate_label(self, topic: str, duration: int, key_point: str) -> str:
        """Generate label in format: [Topic] [Duration] [Key Point]"""
        return f"[{topic}] [{duration}s] {key_point}"
    
    def extract_topic(self, transcript: str) -> str:
        """Extract topic from transcript."""
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ["disk", "space", "storage", "ebs"]):
            return "Infrastructure"
        elif any(word in transcript_lower for word in ["audio", "transcribe", "whisper", "voice"]):
            return "Capabilities"
        elif any(word in transcript_lower for word in ["skill", "create", "protocol", "system"]):
            return "Development"
        elif any(word in transcript_lower for word in ["next", "what", "do", "should"]):
            return "Planning"
        elif any(word in transcript_lower for word in ["understand", "hear", "listen"]):
            return "Communication"
        else:
            return "Response"
    
    def extract_key_point(self, transcript: str, response: str) -> str:
        """Extract key point from response."""
        # Simple extraction: first sentence or first 50 chars
        sentences = response.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 10:
                # Truncate if too long
                if len(first_sentence) > 50:
                    return first_sentence[:47] + "..."
                return first_sentence
        
        # Fallback: first 50 chars of response
        return response[:50].strip()
    
    def process_audio(self, audio_path: str, test_mode: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Process audio input and generate audio response."""
        # Step 1: Transcribe
        print(f"Transcribing: {audio_path}")
        transcript = self.transcribe_audio(audio_path)
        
        if not transcript:
            print("Transcription failed")
            return None, None, None
        
        print(f"Transcript: {transcript}")
        
        # Step 2: Generate response
        if test_mode:
            response_text = "Audio response protocol is now active. I can transcribe your audio and respond with audio using text-to-speech."
        else:
            # For now, use test response
            response_text = f"I received your audio message: '{transcript}'. The audio response protocol is working. I'm using espeak for text-to-speech conversion."
        
        # Step 3: Convert to audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_output = tmp.name
        
        print(f"Converting to audio: {len(response_text)} characters")
        success = self.text_to_speech(response_text, audio_output)
        
        if not success:
            print("TTS conversion failed")
            os.unlink(audio_output)
            return None, None, None
        
        # Step 4: Generate label
        duration = self.estimate_duration(response_text)
        topic = self.extract_topic(transcript)
        key_point = self.extract_key_point(transcript, response_text)
        label = self.generate_label(topic, duration, key_point)
        
        print(f"Generated label: {label}")
        
        return audio_output, label, transcript
    
    def cleanup(self, audio_path: str):
        """Clean up temporary files."""
        if audio_path and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description="Audio responder for audio-only protocol")
    parser.add_argument("--audio", help="Input audio file path")
    parser.add_argument("--tts-engine", default="espeak", choices=["espeak"],
                       help="TTS engine to use")
    parser.add_argument("--test", action="store_true",
                       help="Test mode with sample response")
    parser.add_argument("--keep", action="store_true",
                       help="Keep output audio file (don't delete)")
    
    args = parser.parse_args()
    
    # Test mode without audio file
    if args.test and not args.audio:
        print("=== Testing Audio Response Protocol ===")
        responder = AudioResponder(tts_engine=args.tts_engine)
        
        # Create test audio file
        test_text = "This is a test of the audio response protocol."
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            test_audio = tmp.name
        
        print(f"Testing TTS with: '{test_text}'")
        success = responder.text_to_speech(test_text, test_audio)
        
        if success:
            size = os.path.getsize(test_audio)
            print(f"✓ TTS successful: {test_audio} ({size} bytes)")
            print(f"  Label: [Test] [5s] Audio response protocol working")
            
            if not args.keep:
                os.unlink(test_audio)
                print("  Test file cleaned up")
        else:
            print("✗ TTS failed")
        
        sys.exit(0 if success else 1)
    
    # Normal mode with audio file
    if not args.audio:
        print("Error: --audio argument required (or use --test)")
        sys.exit(1)
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)
    
    print("=== Audio Response Protocol ===")
    responder = AudioResponder(tts_engine=args.tts_engine)
    
    audio_output, label, transcript = responder.process_audio(
        args.audio, test_mode=args.test
    )
    
    if audio_output and label:
        print(f"\n✓ SUCCESS")
        print(f"  Input: {args.audio}")
        print(f"  Transcript: {transcript}")
        print(f"  Output: {audio_output}")
        print(f"  Label: {label}")
        print(f"  Size: {os.path.getsize(audio_output)} bytes")
        
        if not args.keep:
            responder.cleanup(audio_output)
            print(f"  Output cleaned up")
        
        # For integration: this would send the audio via message tool
        print(f"\nNext step: Send audio via message tool with label: {label}")
        
    else:
        print("\n✗ FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
