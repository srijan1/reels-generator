"""
Instagram Reels Generator with Groq API Integration.

This script creates Instagram-style narrative story videos with:
1. Custom scripts based on user prompts (Groq API)
2. pyttsx3 voice-over (replacing Speechify API)
3. AI-generated images (Stable Diffusion)
4. Audio-synchronized video effects and captions
5. Professional-style subtitle overlays

Usage:
    python groq_reel_generator.py

Requirements:
    - Python 3.8+
    - Libraries: pyttsx3, torch, diffusers, pillow, numpy, opencv, tqdm, pydub, requests
    - FFMPEG installed (for video creation)
    - Groq API key: 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
"""

# Import required modules - update these import statements to match your file names
#from main_pyttsx3 import main  # Or whatever your main file is called
from fixed_main_with_sync import main
from groq_script_generator import get_user_story_prompt, generate_story_script
import json
import os
import time

def generate_custom_video():
    """Generate a custom narrative video based on user input using Groq API"""
    print("=" * 60)
    print("🎬 INSTAGRAM REELS GENERATOR WITH GROQ API 🎬")
    print("=" * 60)
    print("\nThis AI-powered tool creates professional narrative videos with:")
    print("✨ Custom script generation using Groq API")
    print("🎙️  High-quality pyttsx3 voice-over (no API limits)")
    print("🎯 Perfect audio-visual synchronization")
    print("📱 Professional subtitle overlays")
    print("🎨 Dynamic visual effects and transitions")
    print("🤖 AI-generated images via Stable Diffusion")
    print("\nLet's create your custom narrative story!\n")
    
    # Get user input for the story video
    story_topic, audience, duration_minutes, num_segments = get_user_story_prompt()
    
    # Generate script using Groq API
    print(f"\n🚀 Generating your custom narrative script using Groq API...")
    print(f"📖 Topic: {story_topic}")
    print(f"👥 Audience: {audience}")
    print(f"⏱️  Duration: {duration_minutes} minute(s)")
    print(f"📊 Segments: {num_segments}")
    
    # Generate the script with the specified parameters
    story_script = generate_story_script(story_topic, audience, duration_minutes, num_segments)
    
    # Save the script to a file for inspection/reuse
    timestamp = int(time.time())
    script_dir = "./generated_scripts"
    os.makedirs(script_dir, exist_ok=True)
    script_path = f"{script_dir}/story_script_{timestamp}.json"
    
    with open(script_path, 'w') as f:
        json.dump(story_script, f, indent=2)
    
    print(f"\n✅ Script generated and saved to {script_path}")
    print(f"📝 Title: {story_script.get('title', 'Custom Story')}")
    print(f"🎭 Style: {story_script.get('style', 'narrative')}")
    print(f"📱 Format: {story_script.get('aspect_ratio', '9:16')} (vertical)")
    
    print("\n🎬 Starting video generation process...")
    print("⚠️  This will take several minutes depending on your hardware.")
    print("📊 Progress will be shown for each step.\n")
    
    # Call the main function with our custom script
    try:
        main(custom_script=story_script)
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your custom narrative video is ready!")
        print("=" * 60)
        print(f"📁 Script saved: {script_path}")
        print("🎥 Video file: Check current directory for final output")
        print("📱 Ready for: Instagram Reels, TikTok, YouTube Shorts")
        print("\n💡 Tips:")
        print("   • Your script is saved for future use or editing")
        print("   • Try different topics and audiences for variety")
        print("   • The video is optimized for mobile viewing")
        print("\n🙏 Thank you for using the Groq-powered Instagram Reels Generator!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
        print(f"📁 Your script was saved to: {script_path}")
        print("💡 You can resume generation later with this script.")
        
    except Exception as e:
        print(f"\n❌ Error during video generation: {e}")
        print(f"📁 Your script was still saved to: {script_path}")
        print("💡 You can try running the generation again or check the logs.")

def show_api_info():
    """Display information about the Groq API integration"""
    print("\n" + "=" * 50)
    print("🔧 GROQ API CONFIGURATION")
    print("=" * 50)
    print("🌐 API Endpoint: https://api.groq.com/openai/v1/chat/completions")
    print("🤖 Model: meta-llama/llama-4-scout-17b-16e-instruct")
    print("🔑 API Key: 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")
    print("⚡ Features: Fast inference, high-quality text generation")
    print("💰 Advantage: Free tier available, fast processing")
    print("\n💡 What this means for you:")
    print("   • Fast script generation (usually under 10 seconds)")
    print("   • High-quality narrative content")
    print("   • Reliable API with good uptime")
    print("   • No complex authentication needed")

def main_menu():
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "=" * 50)
        print("🎬 GROQ-POWERED REEL GENERATOR")
        print("=" * 50)
        print("1. 🚀 Generate Custom Video")
        print("2. 🔧 View API Configuration") 
        print("3. 📚 View Example Scripts")
        print("4. ❌ Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            generate_custom_video()
            break
        elif choice == "2":
            show_api_info()
        elif choice == "3":
            show_example_scripts()
        elif choice == "4":
            print("\n👋 Thanks for using the Groq-powered Reel Generator!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")

def show_example_scripts():
    """Show example prompts and what they generate"""
    print("\n" + "=" * 50)
    print("📚 EXAMPLE STORY PROMPTS")
    print("=" * 50)
    
    examples = [
        {
            "topic": "A hero's journey",
            "audience": "general",
            "description": "Classic hero narrative with challenges and growth"
        },
        {
            "topic": "Friendship and loyalty", 
            "audience": "children",
            "description": "Heartwarming story about the power of friendship"
        },
        {
            "topic": "Overcoming fear",
            "audience": "adult", 
            "description": "Mature exploration of conquering personal fears"
        },
        {
            "topic": "The magic of everyday moments",
            "audience": "general",
            "description": "Finding wonder in ordinary experiences"
        },
        {
            "topic": "Technology and humanity",
            "audience": "adult",
            "description": "Thought-provoking narrative about tech's impact"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. 📖 Topic: '{example['topic']}'")
        print(f"   👥 Audience: {example['audience']}")
        print(f"   📝 Description: {example['description']}")
    
    print(f"\n💡 Pro tip: Be specific with your topics for better results!")
    print(f"   Instead of 'love', try 'finding love in unexpected places'")
    print(f"   Instead of 'adventure', try 'a solo backpacking adventure'")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using the Groq-powered Reel Generator!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your dependencies and try again.")
