#!/usr/bin/env python3
"""
Simple Edge TTS test.
"""

import subprocess
import json
import os

def test_edge_tts():
    # Test text
    text = "This is a test of Edge TTS voice quality. Much better than espeak."
    
    print(f"Testing Edge TTS with text: '{text}'")
    
    # Try to call the tts tool
    try:
        # Import the tts tool function if possible
        # For now, let's just create a simple test
        print("Creating test audio...")
        
        # Use a simple approach: create text file and use subprocess
        with open("/tmp/test_tts.txt", "w") as f:
            f.write(text)
        
        # Actually, let me check if we can use the tts tool via Python
        import sys
        sys.path.append('/home/ubuntu/.npm-global/lib/node_modules/openclaw')
        
        # Try direct import
        try:
            from openclaw.src.tts import tts as tts_tool
            print("Found tts module")
        except ImportError:
            print("Could not import tts module directly")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_edge_tts()