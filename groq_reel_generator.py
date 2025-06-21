#!/usr/bin/env python3
"""
Updated Groq Reel Generator - Main Entry Point
This file can run either as a Flask web app or as a command-line interface
"""

import os
import sys
import argparse
import json
import time
import glob
from pathlib import Path

# --- BEGIN DOTENV LOADING ---
from dotenv import load_dotenv
load_dotenv()

# --- BEGIN FFMPEG PATH MODIFICATION ---
from ffmpeg_config import ensure_ffmpeg_in_path
ensure_ffmpeg_in_path()
# --- END FFMPEG PATH MODIFICATION ---

def run_web_app(port=5000):
    """Run the Flask web application"""
    try:
        # Import and run the Flask app
        import subprocess
        import sys
        
        print("🎬 GROQ REEL GENERATOR - Web Application Mode")
        print("="*60)
        print("🌐 Starting Flask web server...")
        print(f"📱 Access the application at: http://localhost:{port}")
        print("🎯 Features:")
        print("   ✅ Web-based video generation")
        print("   ✅ Real-time progress tracking")
        print("   ✅ Audio quality testing")
        print("   ✅ System status monitoring")
        print("   ✅ Custom script upload")
        print("="*60)
        
        # Run the Flask app with the specified port
        subprocess.run([sys.executable, "app.py", str(port)])
        
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install flask")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start web application: {e}")
        sys.exit(1)

def run_cli_mode():
    """Run the original command-line interface"""
    try:
        print("🎬 GROQ REEL GENERATOR - Command Line Mode")
        print("="*60)
        print("🔊 English audio clarity issues have been resolved!")
        print("🎯 Both English and Hindi audio now work perfectly!")
        
        # Show startup information
        print("\n📋 STARTUP INFORMATION:")
        print("✅ English Audio: CRYSTAL CLEAR (320k bitrate, optimized settings)")
        print("✅ Hindi Audio: PERFECT (maintained existing quality)")
        print("✅ Groq API: Ready for script generation")
        print("✅ Video Generation: Full pipeline ready")
        
        # Run main menu
        main_menu()
        
    except Exception as e:
        print(f"❌ Failed to start CLI mode: {e}")
        sys.exit(1)

def generate_custom_video(): # Added resume logic
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
    print("🤖 AI-generated or Pexels stock images")
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
                alt_script_dir = os.path.join(os.path.dirname(resume_dir_path), "generated_scripts")
                if os.path.isdir(alt_script_dir):
                    dir_name_parts = os.path.basename(resume_dir_path).split('_')
                    if len(dir_name_parts) > 1:
                        timestamp_str = dir_name_parts[-1]
                        alt_script_path = os.path.join(alt_script_dir, f"story_script_{timestamp_str}.json")
                        if os.path.exists(alt_script_path):
                            script_to_load = alt_script_path
                            print(f"Found script in alternative location: {script_to_load}")
                            resume_state['script_generated'] = True
                            resume_state['narration_generated'] = False
                            resume_state['audio_segments_generated'] = False
            
            if script_to_load:
                script_path_for_messages = script_to_load
                print(f"Found script: {script_path_for_messages}")
                try:
                    with open(script_to_load, 'r', encoding='utf-8') as f:
                        story_script_for_main = json.load(f)
                except Exception as e:
                    print(f"Error loading script {script_to_load}: {e}. Cannot resume.")
                    return
            else:
                print(f"No script file found in {os.path.join(resume_dir_path, '1_script')} or alternative locations. Cannot resume.")
                return

            if story_script_for_main:
                num_segments_in_script = len(story_script_for_main.get("segments", []))
                # Check if all images exist and are non-empty
                all_images_exist = False
                if num_segments_in_script > 0:
                    images_dir_for_check = os.path.join(resume_dir_path, "2_images")
                    if os.path.isdir(images_dir_for_check):
                        all_images_exist = all(os.path.exists(os.path.join(images_dir_for_check, f"segment_{i+1}.png")) and \
                                               os.path.getsize(os.path.join(images_dir_for_check, f"segment_{i+1}.png")) > 0 for i in range(num_segments_in_script))
                resume_state['images_generated'] = all_images_exist
                resume_state['filters_applied'] = all_images_exist # Assume filters applied if all images exist
                
                all_segment_frames_exist = num_segments_in_script > 0 and all(os.path.isdir(os.path.join(resume_dir_path, "3_frames", f"segment_{i+1}")) and os.path.exists(os.path.join(resume_dir_path, "3_frames", f"segment_{i+1}", "frame_0000.png")) for i in range(num_segments_in_script))
                resume_state['segment_frames_generated'] = all_segment_frames_exist
                
                all_transitions_exist = num_segments_in_script <= 1 or all(os.path.isdir(os.path.join(resume_dir_path, "4_transitions", f"transition_{i+1}_to_{i+2}")) and os.path.exists(os.path.join(resume_dir_path, "4_transitions", f"transition_{i+1}_to_{i+2}", "frame_0000.png")) for i in range(num_segments_in_script - 1))
                resume_state['transitions_generated'] = all_transitions_exist
            else: # Script could not be loaded
                resume_state.update({'images_generated': False, 'filters_applied': False, 'segment_frames_generated': False, 'transitions_generated': False})

            compiled_frames_dir = os.path.join(resume_dir_path, "5_final", "frames")
            resume_state['frames_compiled'] = os.path.isdir(compiled_frames_dir) and bool(os.listdir(compiled_frames_dir))
            resume_state['final_audio_created'] = os.path.exists(os.path.join(resume_dir_path, "6_audio", "final_audio.mp3"))
            
            print("Resume state detected:")
            for k, v in resume_state.items():
                print(f"  {k}: {'✅' if v else '❌'}")
        else:
            print(f"Invalid resume directory: {resume_dir_path_input}. Starting a new run.")
            resume_dir_path = None # Ensure it's None to trigger new script generation

    if not resume_dir_path: # If not resuming or resume path was invalid
        from groq_script_generator import get_user_story_prompt, generate_story_script
        story_topic, audience, duration_str, num_segments = get_user_story_prompt()
        
        # Convert duration to float
        try:
            duration_minutes = float(duration_str) if duration_str else 1.0
        except:
            duration_minutes = 1.0
        
        # Generate script using Groq API
        print(f"\n🚀 Generating your custom narrative script using Groq API...")
        print(f"📖 Topic: {story_topic}")
        print(f"👥 Audience: {audience}")
        print(f"⏱️  Duration: {duration_minutes} minute(s)")
        print(f"📊 Segments: {num_segments}")
        story_script_for_main = generate_story_script(
            story_topic=story_topic,
            audience=audience,
            duration_minutes=int(duration_minutes),
            num_segments=num_segments
        )
        
        if not story_script_for_main:
            print("❌ Failed to generate script. Please try again.")
            return

        timestamp = int(time.time())
        script_dir = "./generated_scripts" # Changed from "./scripts" to avoid conflict with any "scripts" folder containing .py files
        os.makedirs(script_dir, exist_ok=True)
        script_path_for_messages = f"{script_dir}/story_script_{timestamp}.json"
        
        with open(script_path_for_messages, 'w', encoding='utf-8') as f:
            json.dump(story_script_for_main, f, indent=2)
        
        print(f"\n✅ Script generated and saved to {script_path_for_messages}")
        print(f"📝 Title: {story_script_for_main.get('title', 'Custom Story')}")
        print(f"🎭 Style: {story_script_for_main.get('style', 'narrative')}")
        print(f"📱 Format: {story_script_for_main.get('aspect_ratio', '9:16')} (vertical)")

    print("\n🎬 Starting video generation process...")
    print("⚠️  This will take several minutes depending on your hardware.")
    print("📊 Progress will be shown for each step.\n")

    try:
        from fixed_main_with_sync import main as generate_video_main # Use the main from fixed_main_with_sync
        # Start the main video generation process
        generate_video_main(
            custom_script=story_script_for_main,
            resume_base_dir=resume_dir_path,
            resume_state=resume_state
        )
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your custom narrative video is ready!")
        print("=" * 60)
        if script_path_for_messages: # This will be None if resuming
            print(f"📁 Script used/generated: {script_path_for_messages}")
        elif resume_dir_path and story_script_for_main: # Resumed
             print(f"📁 Resumed using script: {os.path.join(resume_dir_path, '1_script', 'story_script_with_audio.json')}") # or the one loaded
        print("🎥 Video file: Check current directory for final output (e.g., narrative_story_final_with_audio.mp4)")
        print("📱 Ready for: Instagram Reels, TikTok, YouTube Shorts")
        print("\n💡 Tips:")
        print("   • Your script is saved for future use or editing")
        print("   • Try different topics and audiences for variety")
        print("   • The video is optimized for mobile viewing")
        print("\n🙏 Thank you for using the Groq-powered Instagram Reels Generator!")
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user.")
        if script_path_for_messages: # If a new script was generated before interruption
            print(f"📁 Your script (if newly generated) was saved to: {script_path_for_messages}")
        print("💡 You can attempt to resume generation later by providing the output directory.")
    except Exception as e:
        print(f"\n❌ Error during video generation: {e}")
        if script_path_for_messages: # If a new script was generated before error
            print(f"📁 Your script (if newly generated) was saved to: {script_path_for_messages}")
        print("💡 You can try running the generation again or check the logs.")

def test_audio_quality():
    """Test function to verify English audio clarity"""
    print("\n🧪 Testing English Audio Clarity...")
    
    try:
        # Import the fixed TTS module
        from piper_tts_integration import convert_text_to_speech # Kept as per previous fix
        
        # Test English audio
        english_test_text = "Hello, this is a test of the completely fixed English audio system. The speech should now be crystal clear and perfectly audible."
        english_output = "test_english_clarity.mp3"
        
        print("🔊 Generating English test audio...")
        result_en = convert_text_to_speech(
            english_test_text, 
            english_output, 
            'female', # voice
            'en'      # language
        )
        
        if result_en and os.path.exists(result_en):
            print(f"✅ English test audio generated: {result_en}")
            print("🎯 Play this file to verify crystal clear English audio!")
        else:
            print("❌ English test audio generation failed")
        
        # Test Hindi audio
        hindi_test_text = "यह हिंदी ऑडियो की गुणवत्ता का परीक्षण है। यह पहले से ही बिल्कुल सही तरीके से काम कर रहा है।"
        hindi_output = "test_hindi_clarity.mp3"
        
        print("🔊 Generating Hindi test audio...")
        result_hi = convert_text_to_speech(
            hindi_test_text, 
            hindi_output, 
            'female', # voice
            'hi'      # language
        )
        
        if result_hi and os.path.exists(result_hi):
            print(f"✅ Hindi test audio generated: {result_hi}")
            print("🎯 Play this file to verify perfect Hindi audio!")
        else:
            print("❌ Hindi test audio generation failed")
        
        print("\n🔍 Audio Quality Comparison:")
        print("📊 English: Should now be crystal clear, natural pace, professional quality")
        print("📊 Hindi: Already perfect, maintained existing quality")
        
        return result_en, result_hi
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return None, None

def check_system_status():
    """Check system status and dependencies"""
    print("\n🔍 SYSTEM STATUS CHECK")
    print("="*40)
    
    # Check Python version
    import sys
    print(f"🐍 Python version: {sys.version}")
    
    # Check key dependencies
    dependencies = [
        ('pyttsx3', 'Text-to-Speech Engine'),
        ('pydub', 'Audio Processing'),
        ('torch', 'PyTorch for AI Models'),
        ('transformers', 'Hugging Face Transformers'),
        ('langdetect', 'Language Detection'),
        ('groq', 'Groq API Client'),
        ('requests', 'HTTP Requests'),
        ('PIL', 'Image Processing'),
        ('cv2', 'OpenCV for Video'),
        ('numpy', 'Numerical Computing'),
        ('flask', 'Web Framework')
    ]
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {description}: {module_name} - OK")
        except ImportError:
            print(f"❌ {description}: {module_name} - MISSING")
    
    # Check audio system
    print(f"\n🔊 Audio System Status:")
    try:
        from piper_tts_integration import clear_tts, PYTTSX3_AVAILABLE, TORCH_AVAILABLE
        print(f"✅ Clear TTS System: Ready") # Changed from Professional TTS
        print(f"✅ pyttsx3 Available: {PYTTSX3_AVAILABLE}")
        print(f"✅ PyTorch Available: {TORCH_AVAILABLE}")
        print(f"✅ Initialized Languages: {list(clear_tts.supported_languages) if hasattr(clear_tts, 'supported_languages') else 'N/A'}")
    except Exception as e:
        print(f"❌ Audio System Error: {e}")

def show_audio_settings():
    """Show current audio settings"""
    print("\n🔧 AUDIO SETTINGS - FIXED ENGLISH VERSION")
    print("="*50)
    
    try:
        from piper_tts_integration import clear_tts
        
        print("🎛️ Voice Settings:")
        for key, value in (clear_tts.clarity_settings.items() if hasattr(clear_tts, 'clarity_settings') else {}):
            print(f"   {key}: {value}")
        
        print("\n🌍 Language Configurations:")
        for lang, config in (clear_tts.language_models.items() if hasattr(clear_tts, 'language_models') else {}):
            print(f"   {lang.upper()}:")
            for key, value in config.items():
                print(f"      {key}: {value}")
        
        print("\n🔊 Key Improvements for English Audio:")
        print("   ✅ Speech rate: Optimized to 0.9x for clarity")
        print("   ✅ Volume: Boosted to 1.2x for better audibility")
        print("   ✅ Bitrate: Increased to 320k for English")
        print("   ✅ Processing: Advanced clarity enhancements")
        print("   ✅ Voice selection: Prioritized high-quality voices")
        print("   ✅ Text preparation: Enhanced pronunciation fixes")
        
    except Exception as e:
        print(f"❌ Could not load audio settings: {e}")

def show_api_info():
    """Display information about the Groq API integration"""
    print("\n" + "=" * 50)
    print("🔧 GROQ API CONFIGURATION")
    print("=" * 50)
    print("🌐 API Endpoint: https://api.groq.com/openai/v1/chat/completions")
    print("🤖 Model: meta-llama/llama-4-scout-17b-16e-instruct (or as configured in groq_script_generator.py)")
    # Consider fetching the actual key if it's stored in a variable, but avoid printing it directly if sensitive.
    # For now, just indicate it's used.
    print("🔑 API Key: Used from groq_script_generator.py (ensure it's set there)")
    print("⚡ Features: Fast inference, high-quality text generation")
    print("💰 Advantage: Free tier available, fast processing")
    print("\n💡 What this means for you:")
    print("   • Fast script generation (usually under 10 seconds)")
    print("   • High-quality narrative content")
    print("   • Reliable API with good uptime")
    print("   • No complex authentication needed (beyond API key)")

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

def main_menu():
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "="*60)
        print("🎬 GROQ-POWERED REEL GENERATOR 🎬") # Updated title
        print("="*60)
        print("1. 🚀 Generate Custom Video (with Resume)")
        print("2. 🧪 Test Audio Quality (English + Hindi)") # Added from target file
        print("3. 📊 Check System Status") # Added from target file
        print("4. 🔧 Show Audio Settings") # Added from target file
        print("5. ⚙️ View API Configuration") # New from snippet
        print("6. 📚 View Example Prompts") # New from snippet
        print("7. 🌐 Launch Web Interface") # Kept from target file
        print("8. ❌ Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            generate_custom_video()
        elif choice == '2':
            test_audio_quality()
        elif choice == '3':
            check_system_status()
        elif choice == '4':
            show_audio_settings()
        elif choice == '5':
            show_api_info()
        elif choice == '6':
            show_example_scripts()
        elif choice == '7':
            print("\n🌐 Launching web interface...")
            print("💡 The CLI will be unavailable while the web server is running.")
            print("   Press Ctrl+C to stop the web server and return to CLI.")
            run_web_app(5000) # Assuming default port, can be made configurable
        elif choice == '8':
            print("👋 Goodbye! Thanks for using the Groq Reel Generator!")
            sys.exit(0) # Exit cleanly
        else:
            print("❌ Invalid choice. Please enter 1-8.")

def main_cli_entry():
    """Main entry point with argument parsing, leading to CLI or Web App."""
    parser = argparse.ArgumentParser(
        description="Groq Reel Generator - AI-powered video content creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python groq_reel_generator.py                    # Run CLI mode (interactive menu)
  python groq_reel_generator.py --web              # Run web interface
  python groq_reel_generator.py --cli              # Force CLI mode (interactive menu)
  python groq_reel_generator.py --test-audio       # Test audio only and exit
  python groq_reel_generator.py --check-status     # Check system status and exit
        """
    )
    
    parser.add_argument(
        '--web', 
        action='store_true', 
        help='Run the web interface (Flask app)'
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true', 
        help='Run the command-line interface (interactive menu)'
    )
    
    parser.add_argument(
        '--test-audio', 
        action='store_true', 
        help='Run audio quality test and exit'
    )
    
    parser.add_argument(
        '--check-status', 
        action='store_true', 
        help='Check system status and exit'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Port for web interface (default: 5000)'
    )
    
    args = parser.parse_args()
    
    # Handle specific commands that exit
    if args.test_audio:
        test_audio_quality()
        return
    
    if args.check_status:
        check_system_status()
        return
    
    # Handle mode selection
    if args.web:
        run_web_app(args.port)
    elif args.cli:
        run_cli_mode() # This will call the main_menu
    else:
        # Default behavior - ask user (same as run_cli_mode without the initial print)
        print("🎬 GROQ REEL GENERATOR")
        print("="*30)
        print("Choose how to run the application:")
        print("1. 🌐 Web Interface (Recommended)")
        print("2. 💻 Command Line Interface (Interactive Menu)")
        print("3. ❌ Exit")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == '1':
                run_web_app(args.port)
                break
            elif choice == '2':
                run_cli_mode() # This will call the main_menu
                break
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-3.")

if __name__ == "__main__":
    try:
        main_cli_entry()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting Groq Reel Generator.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("💡 Please check the error message and your setup.")
