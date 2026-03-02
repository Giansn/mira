#!/usr/bin/env python3
"""
Auto-transcribe incoming audio files.
"""

import os
import sys
import time
import json
from pathlib import Path
import subprocess
from datetime import datetime


class AutoTranscriber:
    def __init__(self, media_dir=None, output_dir=None, model="base"):
        self.media_dir = media_dir or "/home/ubuntu/.openclaw/media/inbound"
        self.output_dir = output_dir or "/home/ubuntu/.openclaw/media/transcripts"
        self.model = model
        self.whisper_path = "/data/.venv/whisper/bin/whisper"
        self.processed_file = "/tmp/processed_audio.json"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load processed files
        self.processed = self.load_processed()
    
    def load_processed(self):
        """Load list of already processed files."""
        if os.path.exists(self.processed_file):
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_processed(self):
        """Save list of processed files."""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed), f)
    
    def is_audio_file(self, path):
        """Check if file is audio."""
        return path.suffix.lower() in ['.ogg', '.mp3', '.wav', '.m4a', '.flac']
    
    def transcribe_audio(self, audio_path):
        """Transcribe a single audio file."""
        try:
            # Build command
            cmd = [
                self.whisper_path,
                str(audio_path),
                "--model", self.model,
                "--language", "en",
                "--output_dir", self.output_dir,
                "--output_format", "txt"
            ]
            
            print(f"[{datetime.now()}] Transcribing: {audio_path.name}")
            
            # Run transcription
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find output file
                base_name = audio_path.stem
                output_file = Path(self.output_dir) / f"{base_name}.txt"
                
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        transcript = f.read().strip()
                    
                    print(f"  ✓ Success: {len(transcript)} characters")
                    return {
                        "success": True,
                        "transcript": transcript,
                        "output_file": str(output_file)
                    }
                else:
                    print(f"  ✗ No output file generated")
                    return {"success": False, "error": "No output file"}
            else:
                print(f"  ✗ Transcription failed: {result.stderr[:100]}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            return {"success": False, "error": str(e)}
    
    def check_new_files(self):
        """Check for new audio files."""
        media_path = Path(self.media_dir)
        
        if not media_path.exists():
            print(f"Media directory not found: {media_path}")
            return []
        
        # Find audio files
        audio_files = []
        for file in media_path.iterdir():
            if file.is_file() and self.is_audio_file(file):
                if str(file) not in self.processed:
                    audio_files.append(file)
        
        return audio_files
    
    def process_new_files(self):
        """Process all new audio files."""
        new_files = self.check_new_files()
        
        if not new_files:
            print(f"[{datetime.now()}] No new audio files")
            return 0
        
        print(f"[{datetime.now()}] Found {len(new_files)} new audio file(s)")
        
        processed_count = 0
        for audio_file in new_files:
            result = self.transcribe_audio(audio_file)
            
            if result.get("success"):
                self.processed.add(str(audio_file))
                processed_count += 1
        
        # Save processed list
        if processed_count > 0:
            self.save_processed()
        
        return processed_count
    
    def run_continuous(self, interval=10):
        """Run continuously, checking for new files."""
        print(f"Starting auto-transcriber")
        print(f"  Media dir: {self.media_dir}")
        print(f"  Output dir: {self.output_dir}")
        print(f"  Model: {self.model}")
        print(f"  Check interval: {interval}s")
        print(f"  Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                processed = self.process_new_files()
                if processed > 0:
                    print(f"[{datetime.now()}] Processed {processed} file(s)")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nStopping auto-transcriber")
            self.save_processed()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-transcribe audio files")
    parser.add_argument("--media-dir", help="Directory to watch for audio files")
    parser.add_argument("--output-dir", help="Directory for transcripts")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium"],
                       help="Whisper model to use")
    parser.add_argument("--interval", type=int, default=10,
                       help="Check interval in seconds (for continuous mode)")
    parser.add_argument("--once", action="store_true",
                       help="Process once and exit (default: continuous)")
    
    args = parser.parse_args()
    
    transcriber = AutoTranscriber(
        media_dir=args.media_dir,
        output_dir=args.output_dir,
        model=args.model
    )
    
    if args.once:
        processed = transcriber.process_new_files()
        print(f"Processed {processed} file(s)")
        sys.exit(0 if processed >= 0 else 1)
    else:
        transcriber.run_continuous(interval=args.interval)


if __name__ == "__main__":
    main()
