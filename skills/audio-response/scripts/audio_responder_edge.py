#!/usr/bin/env python3
"""
Audio responder using OpenClaw's Edge TTS for better voice quality.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class AudioResponderEdge:
    """Handle audio-in, audio-out protocol using OpenClaw's Edge TTS."""
    
    def __init__(self):
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
    
    def text_to_speech_edge(self, text: str) -> Optional[str]:
        """Convert text to speech using OpenClaw's Edge TTS."""
        try:
            # Use OpenClaw's tts tool
            cmd = ["openclaw", "tts", text]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse the output to find the audio file path
                for line in result.stdout.split('\n'):
                    if line.startswith('MEDIA:'):
                        media_path = line.split('MEDIA:')[1].strip()
                        if os.path.exists(media_path):
                            return media_path
                
                # Try to parse JSON output
                try:
                    output = json.loads(result.stdout)
                    if 'media' in output:
                        return output['media']
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return None
    
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
        
        if any(word in transcript_lower for word in ["voice", "sound", "quality", "bad", "good"]):
            return "Audio Quality"
        elif any(word in transcript_lower for word in ["disk", "space", "storage", "ebs"]):
            return "Infrastructure"
        elif any(word in transcript_lower for word in ["audio", "transcribe", "whisper"]):
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
    
    def process_audio(self, audio_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Process audio input and generate audio response using Edge TTS."""
        # Step 1: Transcribe
        print(f"Transcribing: {audio_path}")
        transcript = self.transcribe_audio(audio_path)
        
        if not transcript:
            print("Transcription failed")
            return None, None, None
        
        print(f"Transcript: {transcript}")
        
        # Step 2: Generate response based on transcript
        transcript_lower = transcript.lower()
        
        if "voice" in transcript_lower or "bad" in transcript_lower or "quality" in transcript_lower:
            response_text = "I've switched to Edge TTS for better voice quality. This uses Microsoft's neural text-to-speech for more natural sounding audio responses."
        else:
            response_text = f"I received your audio message: '{transcript}'. The audio response protocol is working with improved voice quality using Edge TTS."
        
        # Step 3: Convert to audio using Edge TTS
        print(f"Converting to audio with Edge TTS: {len(response_text)} characters")
        audio_output = self.text_to_speech_edge(response_text)
        
        if not audio_output:
            print("Edge TTS conversion failed")
            return None, None, None
        
        print(f"Edge TTS created: {audio_output}")
        
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
    parser = argparse.ArgumentParser(description="Audio responder using Edge TTS")
    parser.add_argument("--audio", required=True, help="Input audio file path")
    parser.add_argument("--keep", action="store_true",
                       help="Keep output audio file (don't delete)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)
    
    print("=== Audio Response Protocol (Edge TTS) ===")
    responder = AudioResponderEdge()
    
    audio_output, label, transcript = responder.process_audio(args.audio)
    
    if audio_output and label:
        print(f"\n✓ SUCCESS")
        print(f"  Input: {args.audio}")
        print(f"  Transcript: {transcript}")
        print(f"  Output: {audio_output}")
        print(f"  Label: {label}")
        print(f"  Size: {os.path.getsize(audio_output)} bytes")
        
        # Copy to workspace for sending
        workspace_path = f"/home/ubuntu/.openclaw/workspace/edge_tts_response.mp3"
        import shutil
        shutil.copy2(audio_output, workspace_path)
        print(f"  Copied to: {workspace_path}")
        
        if not args.keep:
            responder.cleanup(audio_output)
            print(f"  Original cleaned up")
        
        print(f"\nReady to send with label: {label}")
        
    else:
        print("\n✗ FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
