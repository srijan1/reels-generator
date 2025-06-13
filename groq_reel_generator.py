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
# --- BEGIN FFMPEG PATH MODIFICATION ---
from ffmpeg_config import ensure_ffmpeg_in_path
ensure_ffmpeg_in_path()
# --- END FFMPEG PATH MODIFICATION ---
from fixed_main_with_sync import main
from groq_script_generator import get_user_story_prompt, generate_story_script
import json
import os
import time
import glob

def generate_custom_video():
    """Generate a custom narrative video based on user input using Groq API"""
    print("=" * 60)
    print("🎬 INSTAGRAM REELS GENERATOR WITH GROQ API 🎬")
    print("=" * 60)
    print("\nThis AI-powered tool creates professional narrative videos with:")
    print("✨ Custom script generation using Groq API")
    print("🎙️  High-quality pyttsx3 voice-over (no API limits)")
    print("🎯 Perfect audio-visual synchronization")
    print("📱 Professional subtitle overlays") # Ensure this matches fixed_main_with_sync.py features
    print("🎨 Dynamic visual effects and transitions")
    print("🤖 AI-generated or Pexels stock images") # Reflects mixed image generation
    print("\nLet's create your video!\n")

    resume_dir_path = None
    story_script_for_main = None
    script_path_for_messages = None
    resume_state = {}

    resume_choice = input("Do you want to attempt to resume a previous incomplete run? (yes/no): ").strip().lower()
    if resume_choice == 'yes':
        resume_dir_path_input = input("Enter the full path to the directory to resume: ").strip()
        if os.path.isdir(resume_dir_path_input):
            resume_dir_path = resume_dir_path_input
            print(f"Will attempt to resume from {resume_dir_path}")

            # Detect script file (most complete version)
            script_path_audio_json = os.path.join(resume_dir_path, "1_script", "story_script_with_audio.json")
            script_path_narration_json = os.path.join(resume_dir_path, "1_script", "story_script_with_narration.json")
            script_path_base_json = os.path.join(resume_dir_path, "1_script", "story_script.json")
            
            script_to_load = None
            if os.path.exists(script_path_audio_json):
                script_to_load = script_path_audio_json
                resume_state['script_generated'] = True
                resume_state['narration_generated'] = True
                resume_state['audio_segments_generated'] = True
            elif os.path.exists(script_path_narration_json):
                script_to_load = script_path_narration_json
                resume_state['script_generated'] = True
                resume_state['narration_generated'] = True
                resume_state['audio_segments_generated'] = False
            elif os.path.exists(script_path_base_json):
                script_to_load = script_path_base_json
                resume_state['script_generated'] = True
                resume_state['narration_generated'] = False
                resume_state['audio_segments_generated'] = False
            else:
                # Fallback for scripts saved in ./generated_scripts/ by older versions or direct calls
                alt_script_dir = os.path.join(os.path.dirname(resume_dir_path), "generated_scripts")
                if os.path.isdir(alt_script_dir):
                    # Try to match timestamp from resume_dir_path
                    dir_name_parts = os.path.basename(resume_dir_path).split('_')
                    if len(dir_name_parts) > 1:
                        timestamp_str = dir_name_parts[-1]
                        alt_script_path = os.path.join(alt_script_dir, f"story_script_{timestamp_str}.json")
                        if os.path.exists(alt_script_path):
                            script_to_load = alt_script_path
                            print(f"Found script in alternative location: {script_to_load}")
                            # Assume only script is done if loaded from here
                            resume_state['script_generated'] = True
                            resume_state['narration_generated'] = False 
                            resume_state['audio_segments_generated'] = False

            if script_to_load:
                script_path_for_messages = script_to_load
                print(f"Found script: {script_path_for_messages}")
                try:
                    with open(script_to_load, 'r') as f:
                        story_script_for_main = json.load(f)
                except Exception as e:
                    print(f"Error loading script {script_to_load}: {e}. Cannot resume.")
                    return
            else:
                print(f"No script file found in {os.path.join(resume_dir_path, '1_script')} or alternative locations. Cannot resume.")
                return

            if story_script_for_main:
                num_segments_in_script = len(story_script_for_main.get("segments", []))

                # Check for generated images (all images must exist)
                all_images_exist = True
                if num_segments_in_script > 0:
                    for i in range(num_segments_in_script):
                        image_path = os.path.join(resume_dir_path, "2_images", f"segment_{i+1}.png")
                        if not os.path.exists(image_path):
                            all_images_exist = False
                            break
                else:
                    all_images_exist = False # No segments means no images needed, or script is invalid
                resume_state['images_generated'] = all_images_exist
                resume_state['filters_applied'] = all_images_exist # Assume filters applied if all images exist

                # Check for generated segment frames (ALL segments must have frames)
                all_segment_frames_exist = True
                if num_segments_in_script > 0:
                    for i in range(num_segments_in_script):
                        segment_frames_dir = os.path.join(resume_dir_path, "3_frames", f"segment_{i+1}")
                        first_frame_in_segment = os.path.join(segment_frames_dir, "frame_0000.png")
                        if not (os.path.isdir(segment_frames_dir) and os.path.exists(first_frame_in_segment)):
                            all_segment_frames_exist = False
                            break
                else: 
                    all_segment_frames_exist = False 
                resume_state['segment_frames_generated'] = all_segment_frames_exist

                # Check for transitions (ALL transitions must exist if num_segments > 1)
                all_transitions_exist = True
                if num_segments_in_script > 1:
                    for i in range(num_segments_in_script - 1):
                        transition_dir = os.path.join(resume_dir_path, "4_transitions", f"transition_{i+1}_to_{i+2}")
                        first_frame_in_transition = os.path.join(transition_dir, "frame_0000.png")
                        if not (os.path.isdir(transition_dir) and os.path.exists(first_frame_in_transition)):
                            all_transitions_exist = False
                            break
                else: # No transitions needed for 0 or 1 segment
                    all_transitions_exist = True
                resume_state['transitions_generated'] = all_transitions_exist
            else:
                print("Script could not be loaded properly. Cannot determine resume state accurately.")
                # Set all to false to be safe if script is None
                resume_state['images_generated'] = False
                resume_state['filters_applied'] = False
                resume_state['segment_frames_generated'] = False
                resume_state['transitions_generated'] = False

            compiled_frames_dir = os.path.join(resume_dir_path, "5_final", "frames")
            resume_state['frames_compiled'] = os.path.isdir(compiled_frames_dir) and bool(os.listdir(compiled_frames_dir))
            resume_state['final_audio_created'] = os.path.exists(os.path.join(resume_dir_path, "6_audio", "final_audio.mp3"))

            print("Resume state detected:")
            for k, v in resume_state.items():
                print(f"  {k}: {'✅' if v else '❌'}")
        else:
            print(f"Invalid resume directory: {resume_dir_path_input}. Starting a new run.")

    if not resume_dir_path:
        # Get user input for the story video
        story_topic, audience, duration_minutes, num_segments = get_user_story_prompt()
        
        # Generate script using Groq API
        print(f"\n🚀 Generating your custom narrative script using Groq API...")
        print(f"📖 Topic: {story_topic}")
        print(f"👥 Audience: {audience}")
        print(f"⏱️  Duration: {duration_minutes} minute(s)")
        print(f"📊 Segments: {num_segments}")
        
        story_script_for_main = generate_story_script(story_topic, audience, duration_minutes, num_segments)
        
        timestamp = int(time.time())
        script_dir = "./generated_scripts"
        os.makedirs(script_dir, exist_ok=True)
        script_path_for_messages = f"{script_dir}/story_script_{timestamp}.json"
        
        with open(script_path_for_messages, 'w') as f:
            json.dump(story_script_for_main, f, indent=2)
        
        print(f"\n✅ Script generated and saved to {script_path_for_messages}")
        print(f"📝 Title: {story_script_for_main.get('title', 'Custom Story')}")
        print(f"🎭 Style: {story_script_for_main.get('style', 'narrative')}")
        print(f"📱 Format: {story_script_for_main.get('aspect_ratio', '9:16')} (vertical)")

    print("\n🎬 Starting video generation process...")
    print("⚠️  This will take several minutes depending on your hardware.")
    print("📊 Progress will be shown for each step.\n")
    
    # Call the main function with our custom script
    try:
        # Pass resume_state to main so it can skip completed steps
        main(
            custom_script=story_script_for_main,
            resume_base_dir=resume_dir_path,
            resume_state=resume_state
        )
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your custom narrative video is ready!")
        print("=" * 60)
        if script_path_for_messages:
            print(f"📁 Script used/generated: {script_path_for_messages}")
        print("🎥 Video file: Check current directory for final output")
        print("📱 Ready for: Instagram Reels, TikTok, YouTube Shorts")
        print("\n💡 Tips:")
        print("   • Your script is saved for future use or editing")
        print("   • Try different topics and audiences for variety")
        print("   • The video is optimized for mobile viewing")
        print("\n🙏 Thank you for using the Groq-powered Instagram Reels Generator!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
        if script_path_for_messages:
            print(f"📁 Your script (if newly generated) was saved to: {script_path_for_messages}")
        print("💡 You can resume generation later with this script.")
        
    except Exception as e:
        print(f"\n❌ Error during video generation: {e}")
        if script_path_for_messages:
            print(f"📁 Your script (if newly generated) was saved to: {script_path_for_messages}")
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
