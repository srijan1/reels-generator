"""
Instagram Reels Generator with pyttsx3 and Grok API Integration.

This script creates Instagram-style narrative story videos with:
1. Custom scripts based on user prompts (Grok API)
2. pyttsx3 voice-over (replacing Speechify API)
3. AI-generated images (Stable Diffusion)
4. Audio-synchronized video effects and captions
5. Professional-style subtitle overlays

Usage:
    python reel_generator_custom.py

Requirements:
    - Python 3.8+
    - Libraries: pyttsx3, torch, diffusers, pillow, numpy, opencv, tqdm, pydub
    - FFMPEG installed (for video creation)
"""

# Import required modules
from main_pyttsx3 import main
from grok_script_generator import get_user_story_prompt, generate_story_script
import json
import os
import time

def generate_custom_video():
    """Generate a custom narrative video based on user input"""
    print("Starting Instagram Reels Generator with Custom Script Generation...")
    print("This tool creates AI-powered narrative videos with")
    print("- Custom script generation using Grok API")
    print("- pyttsx3 voice-over (no API required)")
    print("- Perfect audio-visual synchronization")
    print("- Professional subtitle overlays")
    print("- Dynamic visual effects")
    print("\nFirst, let's create your custom narrative story script!\n")
    
    # Get user input for the story video
    story_topic, audience, duration_minutes, num_segments = get_user_story_prompt()
    
    # Generate script using Grok API
    print("\nGenerating your custom narrative script using Grok API...")
    
    # Generate the script with 8 segments for a 1-minute video
    story_script = generate_story_script(story_topic, audience, duration_minutes, num_segments)
    
    # Save the script to a file for inspection/reuse
    timestamp = int(time.time())
    script_dir = "./scripts"
    os.makedirs(script_dir, exist_ok=True)
    script_path = f"{script_dir}/story_script_{timestamp}.json"
    
    with open(script_path, 'w') as f:
        json.dump(story_script, f, indent=2)
    
    print(f"\nScript generated and saved to {script_path}")
    print("\nGenerating your custom narrative video. This will take several minutes...\n")
    
    # Call the main function with our custom script
    main(custom_script=story_script)
    
    print("\nProcess complete! Check the current directory for your video.")
    print(f"Your script is saved at {script_path} for future use.")
    print("Thanks for using the Instagram Reels Generator!")

if __name__ == "__main__":
    generate_custom_video()