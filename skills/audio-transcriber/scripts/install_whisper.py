#!/usr/bin/env python3
"""
Install Whisper and dependencies for audio transcription.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False


def check_system():
    """Check system requirements."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"   Python: {python_version}")
    
    # Check OS
    system = platform.system()
    print(f"   OS: {system} {platform.release()}")
    
    # Check architecture
    arch = platform.machine()
    print(f"   Architecture: {arch}")
    
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("🔍 Checking for FFmpeg...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if "ffmpeg version" in result.stdout:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        return False


def install_ffmpeg():
    """Install FFmpeg based on OS."""
    system = platform.system()
    
    if system == "Linux":
        print("🐧 Installing FFmpeg on Linux...")
        # Try apt (Debian/Ubuntu)
        if run_command("sudo apt-get update", "Update package list"):
            if run_command("sudo apt-get install -y ffmpeg", "Install FFmpeg"):
                return True
        
        # Try yum (RHEL/CentOS)
        if run_command("sudo yum install -y ffmpeg", "Install FFmpeg (yum)"):
            return True
        
        # Try dnf (Fedora)
        if run_command("sudo dnf install -y ffmpeg", "Install FFmpeg (dnf)"):
            return True
    
    elif system == "Darwin":  # macOS
        print("🍎 Installing FFmpeg on macOS...")
        if run_command("brew install ffmpeg", "Install FFmpeg via Homebrew"):
            return True
    
    elif system == "Windows":
        print("🪟 Installing FFmpeg on Windows...")
        print("   Please download FFmpeg from: https://ffmpeg.org/download.html")
        print("   Or use chocolatey: choco install ffmpeg")
        return False
    
    return False


def check_pip():
    """Check if pip is available."""
    print("🔍 Checking for pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip not found")
        return False


def install_whisper():
    """Install Whisper via pip."""
    print("📦 Installing Whisper...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrade pip")
    
    # Install Whisper
    if run_command(f"{sys.executable} -m pip install openai-whisper", "Install Whisper"):
        print("✅ Whisper installed successfully")
        return True
    
    return False


def test_installation():
    """Test the Whisper installation."""
    print("🧪 Testing installation...")
    
    # Test Whisper import
    try:
        import whisper
        print("✅ Whisper Python module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Whisper: {e}")
        return False
    
    # Test Whisper command
    try:
        result = subprocess.run(
            ["whisper", "--help"],
            capture_output=True,
            text=True
        )
        if "usage: whisper" in result.stdout:
            print("✅ Whisper CLI is available")
        else:
            print("❌ Whisper CLI not working properly")
            return False
    except FileNotFoundError:
        print("❌ Whisper command not found in PATH")
        return False
    
    # Test FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg not available after installation")
        return False
    
    print("✅ All tests passed!")
    return True


def create_sample_script():
    """Create a sample transcription script."""
    script_content = '''#!/usr/bin/env python3
"""
Sample transcription script.
"""

import sys
import whisper

def transcribe_audio(audio_path, model_size="base"):
    """Transcribe an audio file."""
    print(f"Loading model: {model_size}")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing: {audio_path}")
    result = model.transcribe(audio_path)
    
    return result["text"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_sample.py <audio_file> [model_size]")
        print("Model sizes: tiny, base, small, medium, large")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    try:
        transcript = transcribe_audio(audio_file, model_size)
        print("\\n=== TRANSCRIPT ===\\n")
        print(transcript)
        print("\\n==================\\n")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
'''
    
    script_path = Path.home() / "transcribe_sample.py"
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    
    print(f"📝 Sample script created: {script_path}")
    print("   Run: python transcribe_sample.py audio.ogg")


def main():
    """Main installation function."""
    print("=" * 60)
    print("Whisper Audio Transcription Installer")
    print("=" * 60)
    
    # Check system
    if not check_system():
        print("❌ System check failed")
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        print("❌ pip is required but not found")
        print("   Install pip first: https://pip.pypa.io/en/stable/installation/")
        sys.exit(1)
    
    # Check/install FFmpeg
    if not check_ffmpeg():
        print("FFmpeg not found, attempting to install...")
        if not install_ffmpeg():
            print("❌ Failed to install FFmpeg")
            print("   Please install FFmpeg manually:")
            print("   Linux: sudo apt-get install ffmpeg")
            print("   macOS: brew install ffmpeg")
            print("   Windows: Download from ffmpeg.org")
            sys.exit(1)
    
    # Install Whisper
    if not install_whisper():
        print("❌ Failed to install Whisper")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Create sample script
    create_sample_script()
    
    print("=" * 60)
    print("✅ Installation complete!")
    print("=" * 60)
    print("\\nNext steps:")
    print("1. Test with: python transcribe_sample.py audio.ogg")
    print("2. Use: whisper audio.ogg --model base --language en")
    print("3. See help: whisper --help")
    print("\\nFor Telegram integration, see the audio-transcriber skill documentation.")


if __name__ == "__main__":
    main()
