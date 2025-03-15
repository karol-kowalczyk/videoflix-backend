"""
Utility function for video conversion.

This module provides a function to convert a given video file to 480p resolution 
using FFmpeg.
"""

import subprocess
import os

def convert_480p(source):
    """
    Converts a video file to 480p resolution using FFmpeg.

    Args:
        source (str): The file path of the original video.

    Returns:
        str: The file path of the converted 480p video.
    """
    base_name = os.path.splitext(source)[0]  # Extracts the file name without extension
    target = f"{base_name}_480p.mp4"  # Defines the output file name with 480p suffix
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'

    try:
        subprocess.run(cmd, shell=True, check=True)  # Executes FFmpeg command
        return target  # Returns the path of the converted 480p video
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return None  # Returns None if conversion fails
