"""
Instagram Reels Generator with pyttsx3 Integration.

This script creates Instagram-style travel reels with:
1. Enhanced narration 
2. pyttsx3 voice-over (replacing Speechify API)
3. AI-generated images (Stable Diffusion)
4. Audio-synchronized video effects and captions
5. Professional-style subtitle overlays

Usage:
    python reel_generator_pyttsx3.py
    

Requirements:
    - Python 3.8+
    - Libraries: pyttsx3, torch, diffusers, pillow, numpy, opencv, tqdm, pydub
    - FFMPEG installed (for video creation)
"""

# Import required modules
from main_pyttsx3 import main

if __name__ == "__main__":
    print("Starting Instagram Reels Generator with pyttsx3...")
    print("This tool creates AI-powered travel videos with")
    print("- Enhanced narration")
    print("- pyttsx3 voice-over (no API required)")
    print("- Perfect audio-visual synchronization")
    print("- Professional subtitle overlays")
    print("- Dynamic visual effects")
    print("\nThe process will take several minutes. Please be patient!\n")
    
    # Run the main function
    main()
    
    print("\nProcess complete! Check current directory for your travel video.")
    print("Thanks for using Instagram Reels Generator with pyttsx3!")
