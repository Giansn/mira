#!/usr/bin/env python3
"""
Extract information from multimedia files (audio, image, video).
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any


def get_file_type(file_path: str) -> str:
    """Get file type using `file` command."""
    try:
        result = subprocess.run(
            ["file", "--brief", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_audio_info(file_path: str) -> Dict[str, Any]:
    """Get audio file information using FFprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        info = {
            "type": "audio",
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
        return {"type": "audio", "error": str(e)}


def get_image_info(file_path: str) -> Dict[str, Any]:
    """Get image file information."""
    try:
        # Try identify command (ImageMagick)
        cmd = ["identify", "-format", "%wx%h", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dimensions = result.stdout.strip()
        
        info = {
            "type": "image",
            "dimensions": dimensions,
        }
        
        # Try to get more info with file command
        file_type = get_file_type(file_path)
        info["file_type"] = file_type
        
        # Get file size
        info["size"] = os.path.getsize(file_path)
        
        return info
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to basic file info
        return {
            "type": "image",
            "size": os.path.getsize(file_path),
            "file_type": get_file_type(file_path),
        }


def get_video_info(file_path: str) -> Dict[str, Any]:
    """Get video file information using FFprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        info = {
            "type": "video",
            "format": data.get("format", {}).get("format_name", "unknown"),
            "duration": float(data.get("format", {}).get("duration", 0)),
            "size": int(data.get("format", {}).get("size", 0)),
            "bit_rate": int(data.get("format", {}).get("bit_rate", 0)),
        }
        
        # Video and audio streams
        video_streams = []
        audio_streams = []
        
        for stream in data.get("streams", []):
            stream_type = stream.get("codec_type")
            if stream_type == "video":
                video_streams.append({
                    "codec": stream.get("codec_name", "unknown"),
                    "width": stream.get("width", 0),
                    "height": stream.get("height", 0),
                    "fps": eval(stream.get("avg_frame_rate", "0/1")) if "/" in stream.get("avg_frame_rate", "0/1") else 0,
                })
            elif stream_type == "audio":
                audio_streams.append({
                    "codec": stream.get("codec_name", "unknown"),
                    "sample_rate": int(stream.get("sample_rate", 0)),
                    "channels": int(stream.get("channels", 0)),
                })
        
        info["video_streams"] = video_streams
        info["audio_streams"] = audio_streams
        
        return info
    except Exception as e:
        return {"type": "video", "error": str(e)}


def get_media_info(file_path: str) -> Dict[str, Any]:
    """Get information about any media file."""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    # Get basic file info
    file_type = get_file_type(file_path).lower()
    
    # Determine media type
    if any(x in file_type for x in ["audio", "ogg", "mp3", "wav", "m4a", "flac"]):
        return get_audio_info(file_path)
    elif any(x in file_type for x in ["image", "jpeg", "jpg", "png", "gif", "bmp"]):
        return get_image_info(file_path)
    elif any(x in file_type for x in ["video", "mp4", "avi", "mov", "mkv", "webm"]):
        return get_video_info(file_path)
    else:
        # Generic file info
        return {
            "type": "unknown",
            "file_type": file_type,
            "size": os.path.getsize(file_path),
            "path": file_path,
        }


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python media_info.py <file_path> [<file_path> ...]")
        print("Example: python media_info.py audio.ogg image.jpg video.mp4")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        print(f"\n=== {file_path} ===")
        
        if not os.path.exists(file_path):
            print(f"Error: File not found")
            continue
        
        info = get_media_info(file_path)
        
        if "error" in info:
            print(f"Error: {info['error']}")
            continue
        
        # Print formatted info
        print(f"Type: {info.get('type', 'unknown')}")
        
        if info.get("type") == "audio":
            print(f"Format: {info.get('format', 'unknown')}")
            print(f"Duration: {info.get('duration', 0):.2f}s")
            print(f"Size: {info.get('size', 0)} bytes")
            print(f"Codec: {info.get('codec', 'unknown')}")
            print(f"Sample rate: {info.get('sample_rate', 0)} Hz")
            print(f"Channels: {info.get('channels', 0)}")
        
        elif info.get("type") == "image":
            print(f"Dimensions: {info.get('dimensions', 'unknown')}")
            print(f"Size: {info.get('size', 0)} bytes")
            print(f"File type: {info.get('file_type', 'unknown')}")
        
        elif info.get("type") == "video":
            print(f"Format: {info.get('format', 'unknown')}")
            print(f"Duration: {info.get('duration', 0):.2f}s")
            print(f"Size: {info.get('size', 0)} bytes")
            
            if info.get("video_streams"):
                for i, stream in enumerate(info["video_streams"]):
                    print(f"Video {i+1}: {stream.get('width', 0)}x{stream.get('height', 0)} "
                          f"{stream.get('codec', 'unknown')} "
                          f"{stream.get('fps', 0):.2f} fps")
            
            if info.get("audio_streams"):
                for i, stream in enumerate(info["audio_streams"]):
                    print(f"Audio {i+1}: {stream.get('codec', 'unknown')} "
                          f"{stream.get('sample_rate', 0)} Hz "
                          f"{stream.get('channels', 0)} channels")
        
        else:
            # Generic info
            for key, value in info.items():
                if key not in ["type", "path"]:
                    print(f"{key}: {value}")


if __name__ == "__main__":
    main()
