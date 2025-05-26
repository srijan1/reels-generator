"""
Utility functions for handling common tasks in the Instagram Reels Generator.
"""

import os
import math

def adjust_segment_duration(story_script, target_total_duration=60):
    """Adjust segment durations to make total video about 1 minute long"""
    segments = story_script["segments"]
    
    # Count how many segments we have
    num_segments = len(segments)
    
    # Reserve time for transitions (approximately 0.5 seconds per transition)
    transition_time = 0.5 * (num_segments - 1)
    
    # Available time for segments
    available_segment_time = target_total_duration - transition_time
    
    # Calculate average time per segment
    avg_time_per_segment = available_segment_time / num_segments
    
    # Update durations
    for segment in segments:
        # Set all segments to the same duration for simplicity
        # Could be made more sophisticated based on text length
        segment["duration_seconds"] = avg_time_per_segment
    
    print(f"Adjusted segments to average {avg_time_per_segment:.2f} seconds each")
    return story_script

def ensure_dir(path):
    """Ensure a directory exists, creating it if necessary"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_frame_count(dir_path):
    """Count number of PNG frames in a directory"""
    if not os.path.exists(dir_path):
        return 0
    return len([f for f in os.listdir(dir_path) if f.endswith('.png')])

def format_time(seconds):
    """Format seconds as minutes:seconds"""
    minutes = math.floor(seconds / 60)
    seconds = math.floor(seconds % 60)
    return f"{minutes}:{seconds:02d}"