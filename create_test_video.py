#!/usr/bin/env python3
"""
Create a simple test video for MultiPosti testing
"""

import subprocess
import sys
from pathlib import Path

def create_test_video():
    """Create a simple 5-second test video using FFmpeg"""
    
    output_path = Path("data/videos_to_publish/test_video.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create a simple 5-second video with color bars and text
        cmd = [
            "ffmpeg", "-y",  # -y to overwrite existing file
            "-f", "lavfi",   # Use libavfilter input
            "-i", "testsrc=duration=5:size=1280x720:rate=30",  # 5s test pattern
            "-f", "lavfi",
            "-i", "sine=frequency=440:duration=5",  # 5s audio tone
            "-c:v", "libx264",  # H.264 video codec
            "-c:a", "aac",      # AAC audio codec
            "-pix_fmt", "yuv420p",  # Pixel format for compatibility
            "-shortest",        # Stop when shortest input ends
            str(output_path)
        ]
        
        print("Creating test video with FFmpeg...")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"SUCCESS: Test video created: {output_path}")
            print(f"   File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            return str(output_path)
        else:
            print(f"ERROR: FFmpeg error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("ERROR: FFmpeg not found. Please install FFmpeg:")
        print("   1. Download from https://ffmpeg.org/download.html")
        print("   2. Add to PATH")
        print("   OR use an existing video file")
        return None
    except Exception as e:
        print(f"ERROR: Error creating video: {e}")
        return None

def create_dummy_video():
    """Create a dummy video file for testing (without actual video content)"""
    
    output_path = Path("data/videos_to_publish/dummy_test.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a small dummy file
    with open(output_path, 'wb') as f:
        f.write(b'\x00\x00\x00\x20ftypmp42')  # MP4 header-like bytes
        f.write(b'\x00' * 1000)  # Pad with zeros
    
    print(f"SUCCESS: Dummy video file created: {output_path}")
    print(f"   File size: {output_path.stat().st_size} bytes")
    print("   WARNING: This is NOT a real video, just for testing file handling")
    
    return str(output_path)

if __name__ == '__main__':
    print("MultiPosti Test Video Creator")
    print("=" * 40)
    
    # Try to create a real video first
    video_path = create_test_video()
    
    # If FFmpeg fails, create a dummy file
    if not video_path:
        print("\nCreating dummy file for basic testing...")
        video_path = create_dummy_video()
    
    if video_path:
        print(f"\nReady for testing!")
        print(f"Use this command to test MultiPosti:")
        print(f'python scripts/main.py upload "{video_path}" --title "Test Video" --description "Testing MultiPosti upload" --platforms facebook')