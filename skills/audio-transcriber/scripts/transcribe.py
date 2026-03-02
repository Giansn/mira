#!/usr/bin/env python3
"""
Audio transcription script using Whisper.
"""

import os
import sys
import argparse
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List


def check_whisper_installed() -> bool:
    """Check if Whisper is installed."""
    try:
        import whisper
        return True
    except ImportError:
        return False


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_audio(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convert audio to WAV format for better compatibility."""
    if output_path is None:
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        output_path = temp_file.name
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", "16000",  # Sample rate
            "-ac", "1",      # Mono
            "-y",            # Overwrite
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e.stderr.decode() if e.stderr else str(e)}")
        return None


def transcribe_with_whisper(audio_path: str, model_size: str = "base", 
                           language: Optional[str] = None, 
                           convert: bool = True) -> Optional[str]:
    """Transcribe audio using Whisper."""
    try:
        import whisper
        
        # Convert if needed
        actual_audio_path = audio_path
        temp_file = None
        
        if convert:
            print(f"Converting {audio_path} to WAV format...")
            converted = convert_audio(audio_path)
            if converted:
                actual_audio_path = converted
                temp_file = converted
            else:
                print("Warning: Conversion failed, using original file")
        
        # Load model
        print(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        # Transcribe
        print(f"Transcribing: {audio_path}")
        
        kwargs = {}
        if language:
            kwargs["language"] = language
            print(f"Language specified: {language}")
        else:
            print("Language: auto-detection")
        
        result = model.transcribe(actual_audio_path, **kwargs)
        
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
        
        return result.get("text", "")
        
    except ImportError:
        print("Error: Whisper not installed. Run: pip install openai-whisper")
        return None
    except Exception as e:
        print(f"Transcription error: {e}")
        return None


def transcribe_with_cli(audio_path: str, model_size: str = "base", 
                       language: Optional[str] = None) -> Optional[str]:
    """Transcribe using Whisper CLI command."""
    try:
        cmd = ["whisper", audio_path, "--model", model_size, "--output_format", "txt"]
        
        if language:
            cmd.extend(["--language", language])
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find output file
        base_name = os.path.splitext(audio_path)[0]
        output_file = f"{base_name}.txt"
        
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read()
        else:
            # Try to extract from stdout
            if result.stdout:
                return result.stdout
            else:
                return None
                
    except subprocess.CalledProcessError as e:
        print(f"CLI transcription failed: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: whisper command not found. Make sure it's in PATH")
        return None


def batch_transcribe(audio_files: List[str], model_size: str = "base", 
                    language: Optional[str] = None, output_dir: Optional[str] = None) -> dict:
    """Transcribe multiple audio files."""
    results = {}
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file}")
        
        if not os.path.exists(audio_file):
            results[audio_file] = {"error": "File not found"}
            continue
        
        # Transcribe
        transcript = transcribe_with_whisper(audio_file, model_size, language)
        
        if transcript:
            results[audio_file] = {"success": True, "transcript": transcript}
            
            # Save to file if output directory specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                base_name = Path(audio_file).stem
                output_file = Path(output_dir) / f"{base_name}.txt"
                output_file.write_text(transcript)
                print(f"  Saved to: {output_file}")
        else:
            results[audio_file] = {"success": False, "error": "Transcription failed"}
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper")
    parser.add_argument("audio_files", nargs="+", help="Audio file(s) to transcribe")
    parser.add_argument("--model", "-m", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--language", "-l", help="Language code (e.g., en, de, fr). Auto-detected if not specified.")
    parser.add_argument("--output-dir", "-o", help="Output directory for transcripts")
    parser.add_argument("--no-convert", action="store_true", 
                       help="Don't convert audio to WAV format")
    parser.add_argument("--use-cli", action="store_true", 
                       help="Use whisper CLI instead of Python API")
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_whisper_installed() and not args.use_cli:
        print("Whisper Python module not installed.")
        print("Install with: pip install openai-whisper")
        print("Or use --use-cli flag if whisper command is available")
        sys.exit(1)
    
    if not check_ffmpeg_installed():
        print("FFmpeg not found. Audio conversion may fail.")
        print("Install with: sudo apt-get install ffmpeg")
    
    # Single file or batch
    if len(args.audio_files) == 1:
        # Single file
        audio_file = args.audio_files[0]
        
        if not os.path.exists(audio_file):
            print(f"Error: File not found: {audio_file}")
            sys.exit(1)
        
        print(f"Transcribing: {audio_file}")
        print(f"Model: {args.model}")
        if args.language:
            print(f"Language: {args.language}")
        
        if args.use_cli:
            transcript = transcribe_with_cli(audio_file, args.model, args.language)
        else:
            transcript = transcribe_with_whisper(
                audio_file, args.model, args.language, convert=not args.no_convert
            )
        
        if transcript:
            print("\n" + "="*60)
            print("TRANSCRIPT:")
            print("="*60)
            print(transcript)
            print("="*60)
            
            # Save to file if output directory specified
            if args.output_dir:
                os.makedirs(args.output_dir, exist_ok=True)
                base_name = Path(audio_file).stem
                output_file = Path(args.output_dir) / f"{base_name}.txt"
                output_file.write_text(transcript)
                print(f"\nSaved to: {output_file}")
        else:
            print("Transcription failed")
            sys.exit(1)
            
    else:
        # Batch processing
        print(f"Batch processing {len(args.audio_files)} files")
        print(f"Model: {args.model}")
        if args.language:
            print(f"Language: {args.language}")
        
        results = batch_transcribe(
            args.audio_files, args.model, args.language, args.output_dir
        )
        
        # Summary
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY:")
        print("="*60)
        
        success_count = sum(1 for r in results.values() if r.get("success"))
        fail_count = len(results) - success_count
        
        print(f"Total files: {len(results)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")
        
        if fail_count > 0:
            print("\nFailed files:")
            for file, result in results.items():
                if not result.get("success"):
                    print(f"  {file}: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
