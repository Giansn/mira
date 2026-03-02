#!/usr/bin/env python3
"""
Manage Whisper in virtual environments to avoid PEP 668 restrictions.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List


class VenvWhisper:
    """Manage Whisper in virtual environments."""
    
    def __init__(self, venv_path: Optional[str] = None):
        self.venv_path = venv_path or os.path.expanduser("~/.venv/whisper")
        self.venv_path = Path(self.venv_path)
        self.python = self.venv_path / "bin" / "python"
        self.pip = self.venv_path / "bin" / "pip"
        self.whisper = self.venv_path / "bin" / "whisper"
    
    def create_venv(self, python: str = "python3") -> bool:
        """Create virtual environment."""
        print(f"Creating virtual environment at: {self.venv_path}")
        
        if self.venv_path.exists():
            print(f"Virtual environment already exists at {self.venv_path}")
            response = input("Delete and recreate? (y/N): ").strip().lower()
            if response != 'y':
                print("Using existing virtual environment")
                return True
            shutil.rmtree(self.venv_path)
        
        try:
            # Create virtual environment
            cmd = [python, "-m", "venv", str(self.venv_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Virtual environment created")
            
            # Upgrade pip
            upgrade_cmd = [str(self.pip), "install", "--upgrade", "pip"]
            subprocess.run(upgrade_cmd, capture_output=True, check=True)
            print("✅ pip upgraded")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"❌ Python not found: {python}")
            print("Install python3-venv: sudo apt-get install python3-venv")
            return False
    
    def install_whisper(self, model: str = "base") -> bool:
        """Install Whisper in virtual environment."""
        if not self.venv_path.exists():
            print("Virtual environment not found. Create it first.")
            return False
        
        print(f"Installing Whisper in virtual environment...")
        
        try:
            # Install Whisper
            cmd = [str(self.pip), "install", "openai-whisper"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Whisper installed")
            
            # Test installation
            test_cmd = [str(self.whisper), "--version"]
            subprocess.run(test_cmd, capture_output=True, check=True)
            print("✅ Whisper verified")
            
            # Download specified model
            print(f"Downloading model: {model}")
            download_cmd = [str(self.whisper), "--model", model, "--help"]
            subprocess.run(download_cmd, capture_output=True)
            print(f"✅ Model {model} available")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e.stderr}")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            print("✅ FFmpeg is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ FFmpeg not found")
            print("Install with: sudo apt-get install ffmpeg")
            return False
    
    def transcribe(self, audio_path: str, model: str = "base", 
                  language: Optional[str] = None, output_dir: Optional[str] = None) -> Optional[str]:
        """Transcribe audio using Whisper in virtual environment."""
        if not self.venv_path.exists():
            print("Virtual environment not found. Create it first.")
            return None
        
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return None
        
        # Check FFmpeg
        if not self.check_ffmpeg():
            print("Warning: FFmpeg not found, conversion may fail")
        
        # Build command
        cmd = [str(self.whisper), audio_path, "--model", model, "--output_format", "txt"]
        
        if language:
            cmd.extend(["--language", language])
        
        if output_dir:
            cmd.extend(["--output_dir", output_dir])
        
        print(f"Transcribing: {audio_path}")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find output file
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            if output_dir:
                output_file = os.path.join(output_dir, f"{base_name}.txt")
            else:
                output_file = f"{base_name}.txt"
            
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    transcript = f.read()
                print(f"✅ Transcription saved to: {output_file}")
                return transcript
            else:
                # Try to get from stdout
                if result.stdout:
                    return result.stdout
                else:
                    print("❌ No output generated")
                    return None
                    
        except subprocess.CalledProcessError as e:
            print(f"❌ Transcription failed: {e.stderr}")
            return None
    
    def run_in_venv(self, command: List[str]) -> bool:
        """Run any command in the virtual environment."""
        if not self.venv_path.exists():
            print("Virtual environment not found")
            return False
        
        # Activate venv and run command
        env = os.environ.copy()
        env["PATH"] = str(self.venv_path / "bin") + ":" + env["PATH"]
        env["VIRTUAL_ENV"] = str(self.venv_path)
        
        try:
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"Stderr: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get virtual environment status."""
        status = {
            "venv_path": str(self.venv_path),
            "exists": self.venv_path.exists(),
            "whisper_installed": False,
            "ffmpeg_available": False,
        }
        
        if status["exists"]:
            status["whisper_installed"] = self.whisper.exists()
        
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True)
            status["ffmpeg_available"] = True
        except:
            pass
        
        return status


def main():
    parser = argparse.ArgumentParser(description="Manage Whisper in virtual environments")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create virtual environment")
    create_parser.add_argument("--path", default="~/.venv/whisper", help="Virtual environment path")
    create_parser.add_argument("--python", default="python3", help="Python interpreter to use")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install Whisper")
    install_parser.add_argument("--path", default="~/.venv/whisper", help="Virtual environment path")
    install_parser.add_argument("--model", default="base", help="Model to download")
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe audio")
    transcribe_parser.add_argument("audio_file", help="Audio file to transcribe")
    transcribe_parser.add_argument("--path", default="~/.venv/whisper", help="Virtual environment path")
    transcribe_parser.add_argument("--model", default="base", help="Model to use")
    transcribe_parser.add_argument("--language", help="Language code (e.g., en, de)")
    transcribe_parser.add_argument("--output-dir", help="Output directory for transcript")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check status")
    status_parser.add_argument("--path", default="~/.venv/whisper", help="Virtual environment path")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run command in virtual environment")
    run_parser.add_argument("--path", default="~/.venv/whisper", help="Virtual environment path")
    run_parser.add_argument("command_args", nargs=argparse.REMAINDER, help="Command to run")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize
    venv_whisper = VenvWhisper(args.path)
    
    if args.command == "create":
        success = venv_whisper.create_venv(args.python)
        if success:
            print("✅ Virtual environment created successfully")
            print(f"   Path: {venv_whisper.venv_path}")
            print(f"   Python: {venv_whisper.python}")
        else:
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    
    elif args.command == "install":
        success = venv_whisper.install_whisper(args.model)
        if success:
            print("✅ Whisper installed successfully")
            print(f"   Whisper: {venv_whisper.whisper}")
        else:
            print("❌ Failed to install Whisper")
            sys.exit(1)
    
    elif args.command == "transcribe":
        status = venv_whisper.get_status()
        if not status["exists"]:
            print("Virtual environment not found. Create it first:")
            print(f"  {sys.argv[0]} create --path {args.path}")
            sys.exit(1)
        
        if not status["whisper_installed"]:
            print("Whisper not installed. Install it first:")
            print(f"  {sys.argv[0]} install --path {args.path}")
            sys.exit(1)
        
        transcript = venv_whisper.transcribe(
            args.audio_file, args.model, args.language, args.output_dir
        )
        
        if transcript:
            print("\n" + "="*60)
            print("TRANSCRIPT:")
            print("="*60)
            print(transcript)
            print("="*60)
        else:
            print("❌ Transcription failed")
            sys.exit(1)
    
    elif args.command == "status":
        status = venv_whisper.get_status()
        print("Virtual Environment Status:")
        print(f"  Path: {status['venv_path']}")
        print(f"  Exists: {'✅' if status['exists'] else '❌'}")
        print(f"  Whisper installed: {'✅' if status['whisper_installed'] else '❌'}")
        print(f"  FFmpeg available: {'✅' if status['ffmpeg_available'] else '❌'}")
        
        if status["exists"]:
            print(f"\nUsage:")
            print(f"  Transcribe: {sys.argv[0]} transcribe audio.ogg --path {args.path}")
            print(f"  Run command: {sys.argv[0]} run --path {args.path} -- whisper --help")
    
    elif args.command == "run":
        if not args.command_args:
            print("Error: No command specified")
            sys.exit(1)
        
        success = venv_whisper.run_in_venv(args.command_args)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
