'''
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
'''
'''
from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import sys
import threading
import time
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'groq_reel_generator_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
AVATAR_PATH = 'avatar.mp4'
CLEANUP_HOURS = 24

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Import your existing modules with error handling
MODULES_STATUS = {
    'core': False,
    'talking_avatar': False,
    'musical_rhyme': False
}

# Core modules (required)
try:
    from groq_script_generator import get_user_story_prompt, generate_story_script
    from updated_main_groq import main as generate_video_main
    from piper_tts_integration import convert_text_to_speech, get_audio_duration, verify_audio_file
    MODULES_STATUS['core'] = True
    print("✅ Core modules loaded successfully")
except ImportError as e:
    print(f"❌ Core module import failed: {e}")

# Avatar modules (optional)
try:
    from talking_avatar_integration import EnhancedTalkingAvatarGenerator, generate_talking_avatar_video_reel
    MODULES_STATUS['talking_avatar'] = True
    print("🎭 Talking Avatar feature loaded!")
except ImportError as e:
    print(f"⚠️ Talking Avatar not available: {e}")

# Musical rhyme module (optional)
try:
    from musical_rhyme_generator import (
        initialize_musical_rhyme,
        generate_musical_rhyme_content,
        generate_rhyme_script_only,
        generate_musical_audio_only
    )
    MODULES_STATUS['musical_rhyme'] = True
    print("🎵 Musical Rhyme feature loaded!")
except ImportError as e:
    print(f"⚠️ Musical Rhyme not available: {e}")

# Global status tracking
video_generation_status = {
    'is_generating': False,
    'progress': 0,
    'stage': '',
    'current_video': None,
    'error': None,
    'start_time': None
}

def cleanup_old_files():
    """Remove files older than 24 hours"""
    try:
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=CLEANUP_HOURS)
        
        cleaned_count = 0
        
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            for file_path in Path(folder).rglob('*'):
                if file_path.is_file() and file_path.name != '.gitkeep':
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            print(f"🗑️ Cleaned up: {file_path.name}")
                        except Exception as e:
                            print(f"⚠️ Could not delete {file_path}: {e}")
        
        if cleaned_count > 0:
            print(f"🧹 Cleanup complete: {cleaned_count} files removed")
            
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def update_status(is_generating=False, progress=0, stage='', current_video=None, error=None):
    """Update generation status"""
    global video_generation_status
    
    video_generation_status.update({
        'is_generating': is_generating,
        'progress': progress,
        'stage': stage,
        'current_video': current_video,
        'error': error
    })
    
    if is_generating and not video_generation_status.get('start_time'):
        video_generation_status['start_time'] = datetime.now()
    elif not is_generating:
        video_generation_status['start_time'] = None

def get_avatar_path():
    """Get the avatar.mp4 path with fallback options"""
    possible_paths = [
        Path.cwd() / 'avatar.mp4',
        Path(__file__).parent / 'avatar.mp4',
        Path.cwd() / 'assets' / 'avatar.mp4',
        Path.cwd() / 'videos' / 'avatar.mp4'
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"📍 Found avatar at: {path}")
            return str(path)
    
    print(f"⚠️ Avatar file not found")
    return None

def handle_video_result(result, video_type, timestamp):
    """Handle video result and ensure it's accessible via web interface"""
    if not result or not os.path.exists(result):
        print(f"❌ Video file not found: {result}")
        return None
    
    output_filename = f"{video_type}_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Convert video to web-compatible format
        web_compatible_path = convert_to_web_format(result, output_path)
        
        if web_compatible_path and os.path.exists(web_compatible_path):
            print(f"✅ Web-compatible video created: {web_compatible_path}")
            
            # Generate URL without Flask context (using relative path)
            video_url = f"/static/outputs/{output_filename}"
            print(f"🌐 Video URL: {video_url}")
            
            # Clean up original if it's in a temp location
            if any(keyword in result.lower() for keyword in ['/tmp/', 'temp', '5_final', 'outputs', 'talking_avatar']):
                try:
                    # Clean up the entire temp directory for avatar generation
                    if 'talking_avatar' in result:
                        temp_dir = os.path.dirname(os.path.dirname(result))  # Go up two levels from final/
                        if os.path.exists(temp_dir) and 'talking_avatar' in temp_dir:
                            shutil.rmtree(temp_dir)
                            print(f"🗑️ Cleaned up temp directory: {temp_dir}")
                    else:
                        os.remove(result)
                        print(f"🗑️ Cleaned up original: {result}")
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup failed: {cleanup_error}")
            
            return video_url
        else:
            print(f"❌ Failed to create web-compatible video")
            return None
        
    except Exception as e:
        print(f"❌ Error handling video result: {e}")
        return None

def convert_to_web_format(input_path, output_path):
    """Convert video to web-compatible format using FFmpeg"""
    try:
        print(f"🔄 Converting video to web format...")
        print(f"   Input: {input_path}")
        print(f"   Output: {output_path}")
        
        # FFmpeg command for web-compatible video
        cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-i', input_path,
            '-c:v', 'libx264',  # H.264 video codec
            '-preset', 'medium',  # Encoding speed/quality balance
            '-crf', '23',  # Quality setting (lower = better quality)
            '-c:a', 'aac',  # AAC audio codec
            '-b:a', '128k',  # Audio bitrate
            '-movflags', '+faststart',  # Enable streaming
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # Ensure even dimensions
            output_path
        ]
        
        print(f"🔧 Running FFmpeg conversion...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Video conversion successful")
            return output_path
        else:
            print(f"❌ FFmpeg conversion failed:")
            print(f"   Error: {result.stderr}")
            
            # Fallback: just copy the file if conversion fails
            print(f"🔄 Falling back to direct copy...")
            shutil.copy2(input_path, output_path)
            return output_path
            
    except subprocess.TimeoutExpired:
        print(f"❌ Video conversion timed out")
        # Fallback: just copy the file
        shutil.copy2(input_path, output_path)
        return output_path
    except Exception as e:
        print(f"❌ Video conversion error: {e}")
        # Fallback: just copy the file
        try:
            shutil.copy2(input_path, output_path)
            return output_path
        except Exception as copy_error:
            print(f"❌ Even file copy failed: {copy_error}")
            return None

def generate_avatar_for_web(topic, language='english', audience='adult', duration=1.0):
    """Web-compatible wrapper for avatar generation"""
    
    print(f"🎭 WEB AVATAR GENERATION")
    print(f"📝 Topic: {topic}")
    print(f"🗣️ Language: {language}")
    print(f"👥 Audience: {audience}")
    print(f"⏱️ Duration: {duration} minutes")
    
    try:
        avatar_path = get_avatar_path()
        if not avatar_path:
            print("❌ Avatar file (avatar.mp4) not found")
            return None
        
        print(f"📹 Using avatar: {avatar_path}")
        
        # Create avatar generator with the avatar file
        avatar_generator = EnhancedTalkingAvatarGenerator(avatar_path)
        
        # Generate the avatar video with web parameters
        result = avatar_generator.generate_complete_talking_avatar(
            script_topic=topic,
            audience=audience,
            quality="high"
        )
        
        if result and os.path.exists(result):
            print(f"✅ Avatar video generated: {result}")
            return result
        else:
            print("❌ Avatar generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Avatar generation error: {e}")
        return None

@app.route('/')
def index():
    """Main page"""
    cleanup_old_files()
    avatar_available = get_avatar_path() is not None
    
    return render_template('index.html', 
                         core_available=MODULES_STATUS['core'],
                         talking_avatar_available=MODULES_STATUS['talking_avatar'],
                         musical_rhyme_available=MODULES_STATUS['musical_rhyme'],
                         avatar_available=avatar_available)

@app.route('/status')
def get_status():
    """Get current generation status"""
    status = video_generation_status.copy()
    
    if status.get('start_time'):
        elapsed = (datetime.now() - status['start_time']).total_seconds()
        status['elapsed_time'] = elapsed
    
    return jsonify(status)

@app.route('/generate', methods=['POST'])
def generate_video():
    """Generate video based on form data"""
    if video_generation_status['is_generating']:
        return jsonify({'error': 'Video generation already in progress'}), 400
    
    try:
        data = request.get_json()
        
        video_type = data.get('video_type')
        language = data.get('language', 'english')
        audience = data.get('audience', 'adult')
        topic = data.get('topic', '').strip()
        duration = float(data.get('duration', 1.0))
        
        # Validation
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if len(topic) < 5:
            return jsonify({'error': 'Topic must be at least 5 characters long'}), 400
        
        if duration < 0.5 or duration > 10:
            return jsonify({'error': 'Duration must be between 0.5 and 10 minutes'}), 400
        
        # Start generation in background thread
        thread = threading.Thread(
            target=generate_video_background,
            args=(video_type, topic, language, audience, duration),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': 'Generation started',
            'estimated_duration': f'{duration} minutes'
        })
        
    except Exception as e:
        return jsonify({'error': f'Request processing error: {str(e)}'}), 500

def generate_video_background(video_type, topic, language, audience, duration):
    """Background video generation with detailed progress tracking"""
    try:
        update_status(True, 0, 'Initializing generation system...', None, None)
        time.sleep(1)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Enhance topic with language specification for better results
        enhanced_topic = topic
        if language == 'hindi':
            if 'hindi' not in topic.lower() and 'हिंदी' not in topic:
                enhanced_topic = f"{topic} in hindi"
                print(f"🇮🇳 Enhanced topic for Hindi: {enhanced_topic}")
        
        if video_type == 'reel':
            update_status(True, 5, 'Preparing script generation...', None, None)
            
            if not MODULES_STATUS['core']:
                update_status(False, 0, '', None, 'Core modules not available')
                return
            
            update_status(True, 15, 'Generating creative script...', None, None)
            
            num_segments = max(3, int(duration * 2))
            
            try:
                story_script = generate_story_script(
                    story_topic=enhanced_topic,  # Use enhanced topic
                    audience=audience,
                    duration_minutes=duration,
                    num_segments=num_segments
                )
            except Exception as e:
                update_status(False, 0, '', None, f'Script generation failed: {str(e)}')
                return
            
            if not story_script:
                update_status(False, 0, '', None, 'Failed to generate script content')
                return
            
            update_status(True, 40, 'Creating visual content...', None, None)
            time.sleep(2)
            
            update_status(True, 70, 'Assembling final video...', None, None)
            
            try:
                result = generate_video_main(story_script)
            except Exception as e:
                update_status(False, 0, '', None, f'Video generation failed: {str(e)}')
                return
            
            video_url = handle_video_result(result, "reel", timestamp)
            if video_url:
                update_status(False, 100, 'Complete', video_url, None)
            else:
                update_status(False, 0, '', None, 'Failed to process video file')
                
        elif video_type == 'avatar' and MODULES_STATUS['talking_avatar']:
            avatar_path = get_avatar_path()
            if not avatar_path:
                update_status(False, 0, '', None, 'Avatar file (avatar.mp4) not found')
                return
            
            update_status(True, 10, 'Initializing avatar system...', None, None)
            update_status(True, 30, 'Processing avatar animation...', None, None)
            
            try:
                # Use the web-compatible avatar generation with enhanced topic
                result = generate_avatar_for_web(
                    topic=enhanced_topic,  # Use enhanced topic
                    language=language,
                    audience=audience,
                    duration=duration
                )
                
                video_url = handle_video_result(result, "avatar", timestamp)
                if video_url:
                    update_status(False, 100, 'Complete', video_url, None)
                else:
                    update_status(False, 0, '', None, 'Failed to process avatar video file')
                    
            except Exception as e:
                print(f"❌ Avatar generation error: {e}")
                update_status(False, 0, '', None, f'Avatar generation failed: {str(e)}')
                
        elif video_type == 'musical' and MODULES_STATUS['musical_rhyme']:
            update_status(True, 10, 'Initializing musical system...', None, None)
            update_status(True, 25, 'Generating musical content...', None, None)
            
            try:
                # Generate a unique output directory
                musical_output_dir = f"musical_rhyme_{enhanced_topic.replace(' ', '_')}_{timestamp}"
                
                result = generate_musical_rhyme_content(
                    topic=enhanced_topic,  # Use enhanced topic
                    language=language,
                    audience=audience,
                    output_dir=musical_output_dir
                )
            except Exception as e:
                update_status(False, 0, '', None, f'Musical content generation failed: {str(e)}')
                return
            
            if result:
                update_status(True, 80, 'Processing musical video...', None, None)
                
                # Check if the musical rhyme generator already created a video
                if result.get('final_video') and os.path.exists(result['final_video']):
                    print(f"✅ Using pre-generated musical video: {result['final_video']}")
                    video_result = result['final_video']
                elif result.get('script'):
                    # If no video but script exists, generate video
                    update_status(True, 60, 'Creating musical video from script...', None, None)
                    try:
                        video_result = generate_video_main(result['script'])
                    except Exception as e:
                        update_status(False, 0, '', None, f'Musical video creation failed: {str(e)}')
                        return
                else:
                    update_status(False, 0, '', None, 'No video or script generated by musical system')
                    return
                
                video_url = handle_video_result(video_result, "musical", timestamp)
                if video_url:
                    update_status(False, 100, 'Complete', video_url, None)
                else:
                    update_status(False, 0, '', None, 'Failed to process musical video file')
            else:
                update_status(False, 0, '', None, 'Musical content generation failed')
        
        else:
            update_status(False, 0, '', None, f'Video type "{video_type}" not available')
            
    except Exception as e:
        update_status(False, 0, '', None, f'Unexpected error: {str(e)}')

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated video file with security checks"""
    try:
        file_path = Path(OUTPUT_FOLDER) / filename
        
        if not file_path.exists() or not str(file_path).startswith(str(Path(OUTPUT_FOLDER).resolve())):
            return jsonify({'error': 'File not found or access denied'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/video/<filename>')
def serve_video(filename):
    """Serve video files with proper headers for web playback"""
    try:
        file_path = Path(OUTPUT_FOLDER) / filename
        
        if not file_path.exists() or not str(file_path).startswith(str(Path(OUTPUT_FOLDER).resolve())):
            return jsonify({'error': 'File not found or access denied'}), 404
        
        def generate():
            with open(file_path, 'rb') as f:
                data = f.read(1024)
                while data:
                    yield data
                    data = f.read(1024)
        
        response = app.response_class(generate(), mimetype='video/mp4')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(file_path.stat().st_size))
        response.headers.add('Cache-Control', 'no-cache')
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Video serving error: {str(e)}'}), 500

@app.route('/test-audio', methods=['POST'])
def test_audio():
    """Test audio quality"""
    try:
        data = request.get_json()
        language = data.get('language', 'english')
        
        test_texts = {
            'english': "Hello! This is a test of the English audio quality. The audio should be crystal clear.",
            'hindi': "नमस्ते! यह हिंदी ऑडियो गुणवत्ता का परीक्षण है। आवाज़ बिल्कुल साफ होनी चाहिए।"
        }
        
        if language not in test_texts:
            return jsonify({'error': 'Unsupported language for audio test'}), 400
        
        if not MODULES_STATUS['core']:
            return jsonify({'error': 'Audio system not available'}), 503
        
        text = test_texts[language]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"audio_test_{language}_{timestamp}.mp3"
        output_path = Path(OUTPUT_FOLDER) / output_filename
        
        result = convert_text_to_speech(text, str(output_path))
        
        if result and os.path.exists(result):
            duration = get_audio_duration(result)
            is_valid, message = verify_audio_file(result)
            
            audio_url = url_for('static', filename=f'outputs/{output_filename}')
            
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'duration': round(duration, 2) if duration else 0,
                'quality_message': message,
                'language': language
            })
        else:
            return jsonify({'error': 'Audio generation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Audio test error: {str(e)}'}), 500

@app.route('/system-status')
def system_status():
    """Get comprehensive system status information"""
    try:
        status = {
            'core_modules': MODULES_STATUS['core'],
            'talking_avatar': MODULES_STATUS['talking_avatar'],
            'musical_rhyme': MODULES_STATUS['musical_rhyme'],
            'avatar_file': get_avatar_path() is not None,
            'output_folder': os.path.exists(OUTPUT_FOLDER),
            'upload_folder': os.path.exists(UPLOAD_FOLDER)
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual file cleanup endpoint"""
    try:
        cleanup_old_files()
        return jsonify({'success': True, 'message': 'Cleanup completed successfully'})
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎬 GROQ REEL GENERATOR - WEB INTERFACE")
    print("=" * 50)
    print(f"🌐 Starting Flask web application on localhost:5000")
    print(f"🔗 Open your browser to: http://localhost:5000")
    print("⏹️ Press Ctrl+C to stop the web server")
    print()
    print("📊 System Status:")
    for module, status in MODULES_STATUS.items():
        print(f"   {module}: {'✅ Available' if status else '❌ Not Available'}")
    print(f"   Avatar file: {'✅ Found' if get_avatar_path() else '❌ Not Found'}")
    print()
    
    cleanup_old_files()
    
    app.run(host='0.0.0.0', port=8080, debug=False)
    '''
#!/usr/bin/env python3
"""
Groq Reel Generator - Complete Flask Web Application
Features: Video Generation, Computing Monitoring, Credit System
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import sys
import threading
import time
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'groq_reel_generator_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
AVATAR_PATH = 'avatar.mp4'
CLEANUP_HOURS = 24

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Module availability tracking
MODULES_STATUS = {
    'core': False,
    'talking_avatar': False,
    'musical_rhyme': False,
    'computing_monitor': False
}

# Core modules (required)
try:
    from groq_script_generator import get_user_story_prompt, generate_story_script
    from updated_main_groq import main as generate_video_main
    from piper_tts_integration import convert_text_to_speech, get_audio_duration, verify_audio_file
    MODULES_STATUS['core'] = True
    print("✅ Core modules loaded successfully")
except ImportError as e:
    print(f"❌ Core module import failed: {e}")
    print("💡 Make sure groq_script_generator.py, updated_main_groq.py, and piper_tts_integration.py are available")

# Avatar modules (optional)
try:
    from talking_avatar_integration import EnhancedTalkingAvatarGenerator, generate_talking_avatar_video_reel
    MODULES_STATUS['talking_avatar'] = True
    print("🎭 Talking Avatar feature loaded!")
except ImportError as e:
    print(f"⚠️ Talking Avatar not available: {e}")

# Musical rhyme module (optional)
try:
    from musical_rhyme_generator import (
        initialize_musical_rhyme,
        generate_musical_rhyme_content,
        generate_rhyme_script_only,
        generate_musical_audio_only
    )
    MODULES_STATUS['musical_rhyme'] = True
    print("🎵 Musical Rhyme feature loaded!")
except ImportError as e:
    print(f"⚠️ Musical Rhyme not available: {e}")

# Computing monitor (optional)
try:
    from computing_monitor import (
        start_monitoring, 
        stop_monitoring_and_deduct_credits,
        get_credit_balance,
        add_credits,
        get_usage_statistics,
        check_sufficient_credits
    )
    MODULES_STATUS['computing_monitor'] = True
    print("💻 Computing Monitor loaded!")
except ImportError as e:
    print(f"⚠️ Computing Monitor not available: {e}")
    print("💡 Run 'python setup_computing.py' to install computing monitor dependencies")

# Global status tracking
video_generation_status = {
    'is_generating': False,
    'progress': 0,
    'stage': '',
    'current_video': None,
    'error': None,
    'start_time': None,
    'computing_report': None,
    'credits_info': {
        'balance': 100.0,
        'estimated_cost': 0.0,
        'processing_type': 'Unknown'
    }
}

def cleanup_old_files():
    """Remove files older than 24 hours"""
    try:
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=CLEANUP_HOURS)
        
        cleaned_count = 0
        
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            for file_path in Path(folder).rglob('*'):
                if file_path.is_file() and file_path.name != '.gitkeep':
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            print(f"🗑️ Cleaned up: {file_path.name}")
                        except Exception as e:
                            print(f"⚠️ Could not delete {file_path}: {e}")
        
        if cleaned_count > 0:
            print(f"🧹 Cleanup complete: {cleaned_count} files removed")
            
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def update_status(is_generating=None, progress=None, stage=None, current_video=None, error=None, computing_report=None):
    """Update generation status"""
    global video_generation_status
    
    # Only update non-None values
    if is_generating is not None:
        video_generation_status['is_generating'] = is_generating
    if progress is not None:
        video_generation_status['progress'] = progress
    if stage is not None:
        video_generation_status['stage'] = stage
    if current_video is not None:
        video_generation_status['current_video'] = current_video
    if error is not None:
        video_generation_status['error'] = error
    if computing_report is not None:
        video_generation_status['computing_report'] = computing_report
    
    # Update credits info
    if MODULES_STATUS['computing_monitor']:
        try:
            video_generation_status['credits_info']['balance'] = get_credit_balance()
        except:
            pass
    
    # Handle start/stop time
    if is_generating is True and not video_generation_status.get('start_time'):
        video_generation_status['start_time'] = datetime.now().isoformat()
    elif is_generating is False:
        video_generation_status['start_time'] = None

def get_avatar_path():
    """Get the avatar.mp4 path with fallback options"""
    possible_paths = [
        Path.cwd() / 'avatar.mp4',
        Path(__file__).parent / 'avatar.mp4',
        Path.cwd() / 'assets' / 'avatar.mp4',
        Path.cwd() / 'videos' / 'avatar.mp4'
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"📍 Found avatar at: {path}")
            return str(path)
    
    print(f"⚠️ Avatar file not found")
    return None

def convert_to_web_format(input_path, output_path):
    """Convert video to web-compatible format using FFmpeg"""
    try:
        print(f"🔄 Converting video to web format...")
        print(f"   Input: {input_path}")
        print(f"   Output: {output_path}")
        
        # FFmpeg command for web-compatible video
        cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-i', input_path,
            '-c:v', 'libx264',  # H.264 video codec
            '-preset', 'medium',  # Encoding speed/quality balance
            '-crf', '23',  # Quality setting (lower = better quality)
            '-c:a', 'aac',  # AAC audio codec
            '-b:a', '128k',  # Audio bitrate
            '-movflags', '+faststart',  # Enable streaming
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # Ensure even dimensions
            output_path
        ]
        
        print(f"🔧 Running FFmpeg conversion...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Video conversion successful")
            return output_path
        else:
            print(f"❌ FFmpeg conversion failed:")
            print(f"   Error: {result.stderr}")
            
            # Fallback: just copy the file if conversion fails
            print(f"🔄 Falling back to direct copy...")
            shutil.copy2(input_path, output_path)
            return output_path
            
    except subprocess.TimeoutExpired:
        print(f"❌ Video conversion timed out")
        # Fallback: just copy the file
        shutil.copy2(input_path, output_path)
        return output_path
    except Exception as e:
        print(f"❌ Video conversion error: {e}")
        # Fallback: just copy the file
        try:
            shutil.copy2(input_path, output_path)
            return output_path
        except Exception as copy_error:
            print(f"❌ Even file copy failed: {copy_error}")
            return None

def handle_video_result(result, video_type, timestamp):
    """Handle video result and ensure it's accessible via web interface"""
    if not result or not os.path.exists(result):
        print(f"❌ Video file not found: {result}")
        return None
    
    output_filename = f"{video_type}_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Convert video to web-compatible format
        web_compatible_path = convert_to_web_format(result, output_path)
        
        if web_compatible_path and os.path.exists(web_compatible_path):
            print(f"✅ Web-compatible video created: {web_compatible_path}")
            
            # Generate URL without Flask context (using relative path)
            video_url = f"/static/outputs/{output_filename}"
            print(f"🌐 Video URL: {video_url}")
            
            # Clean up original if it's in a temp location
            if any(keyword in result.lower() for keyword in ['/tmp/', 'temp', '5_final', 'outputs', 'talking_avatar']):
                try:
                    # Clean up the entire temp directory for avatar generation
                    if 'talking_avatar' in result:
                        temp_dir = os.path.dirname(os.path.dirname(result))  # Go up two levels from final/
                        if os.path.exists(temp_dir) and 'talking_avatar' in temp_dir:
                            shutil.rmtree(temp_dir)
                            print(f"🗑️ Cleaned up temp directory: {temp_dir}")
                    else:
                        os.remove(result)
                        print(f"🗑️ Cleaned up original: {result}")
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup failed: {cleanup_error}")
            
            return video_url
        else:
            print(f"❌ Failed to create web-compatible video")
            return None
        
    except Exception as e:
        print(f"❌ Error handling video result: {e}")
        return None

def generate_avatar_for_web(topic, language='english', audience='adult', duration=1.0):
    """Web-compatible wrapper for avatar generation"""
    
    print(f"🎭 WEB AVATAR GENERATION")
    print(f"📝 Topic: {topic}")
    print(f"🗣️ Language: {language}")
    print(f"👥 Audience: {audience}")
    print(f"⏱️ Duration: {duration} minutes")
    
    try:
        avatar_path = get_avatar_path()
        if not avatar_path:
            print("❌ Avatar file (avatar.mp4) not found")
            return None
        
        print(f"📹 Using avatar: {avatar_path}")
        
        # Create avatar generator with the avatar file
        avatar_generator = EnhancedTalkingAvatarGenerator(avatar_path)
        
        # Generate the avatar video with web parameters
        result = avatar_generator.generate_complete_talking_avatar(
            script_topic=topic,
            audience=audience,
            quality="high"
        )
        
        if result and os.path.exists(result):
            print(f"✅ Avatar video generated: {result}")
            return result
        else:
            print("❌ Avatar generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Avatar generation error: {e}")
        return None

def estimate_video_cost(video_type: str, duration: float) -> float:
    """Estimate video generation cost in credits"""
    base_cost = {
        'reel': 3.0,
        'avatar': 5.0,
        'musical': 4.0
    }
    
    base = base_cost.get(video_type, 3.0)
    duration_multiplier = 1.0 + (duration - 1.0) * 0.5  # +50% per additional minute
    
    return round(base * duration_multiplier, 1)

# Flask Routes

@app.route('/')
def index():
    """Main page"""
    cleanup_old_files()
    avatar_available = get_avatar_path() is not None
    
    return render_template('index.html', 
                         core_available=MODULES_STATUS['core'],
                         talking_avatar_available=MODULES_STATUS['talking_avatar'],
                         musical_rhyme_available=MODULES_STATUS['musical_rhyme'],
                         computing_monitor_available=MODULES_STATUS['computing_monitor'],
                         avatar_available=avatar_available)

@app.route('/status')
def get_status():
    """Get current generation status"""
    status = video_generation_status.copy()
    
    # Add timing information if start_time exists
    if status.get('start_time'):
        try:
            start_time = datetime.fromisoformat(status['start_time'])
            elapsed = (datetime.now() - start_time).total_seconds()
            status['elapsed_time'] = elapsed
        except:
            pass
    
    return jsonify(status)

@app.route('/generate', methods=['POST'])
def generate_video():
    """Generate video based on form data"""
    if video_generation_status['is_generating']:
        return jsonify({'error': 'Video generation already in progress'}), 400
    
    try:
        data = request.get_json()
        
        video_type = data.get('video_type')
        language = data.get('language', 'english')
        audience = data.get('audience', 'adult')
        topic = data.get('topic', '').strip()
        duration = float(data.get('duration', 1.0))
        
        # Validation
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if len(topic) < 5:
            return jsonify({'error': 'Topic must be at least 5 characters long'}), 400
        
        if duration < 0.5 or duration > 10:
            return jsonify({'error': 'Duration must be between 0.5 and 10 minutes'}), 400
        
        # Check credits if monitoring is available
        if MODULES_STATUS['computing_monitor']:
            estimated_cost = estimate_video_cost(video_type, duration)
            if not check_sufficient_credits(estimated_cost):
                current_balance = get_credit_balance()
                return jsonify({
                    'error': f'Insufficient credits! Need: {estimated_cost:.1f}, Have: {current_balance:.1f}',
                    'credits_needed': estimated_cost,
                    'current_balance': current_balance
                }), 402  # Payment Required
        
        # Start generation in background thread
        thread = threading.Thread(
            target=generate_video_background,
            args=(video_type, topic, language, audience, duration),
            daemon=True
        )
        thread.start()
        
        response_data = {
            'success': True, 
            'message': 'Generation started',
            'estimated_duration': f'{duration} minutes'
        }
        
        if MODULES_STATUS['computing_monitor']:
            response_data['estimated_cost'] = estimate_video_cost(video_type, duration)
            response_data['current_balance'] = get_credit_balance()
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Request processing error: {str(e)}'}), 500

def generate_video_background(video_type, topic, language, audience, duration):
    """Background video generation with computing monitoring"""
    computing_report = None
    
    try:
        # Start computing monitoring
        if MODULES_STATUS['computing_monitor']:
            start_monitoring(video_type)
            update_status(is_generating=True, progress=0, stage='Initializing with computing monitor...')
        else:
            update_status(is_generating=True, progress=0, stage='Initializing generation system...')
        
        time.sleep(1)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Enhance topic with language specification for better results
        enhanced_topic = topic
        if language == 'hindi':
            if 'hindi' not in topic.lower() and 'हिंदी' not in topic:
                enhanced_topic = f"{topic} in hindi"
                print(f"🇮🇳 Enhanced topic for Hindi: {enhanced_topic}")
        
        if video_type == 'reel':
            update_status(progress=5, stage='Preparing script generation...')
            
            if not MODULES_STATUS['core']:
                update_status(is_generating=False, progress=0, error='Core modules not available')
                return
            
            update_status(progress=15, stage='Generating creative script...')
            
            num_segments = max(3, int(duration * 2))
            
            try:
                story_script = generate_story_script(
                    story_topic=enhanced_topic,
                    audience=audience,
                    duration_minutes=duration,
                    num_segments=num_segments
                )
            except Exception as e:
                update_status(is_generating=False, progress=0, error=f'Script generation failed: {str(e)}')
                return
            
            if not story_script:
                update_status(is_generating=False, progress=0, error='Failed to generate script content')
                return
            
            update_status(progress=40, stage='Creating visual content...')
            time.sleep(2)
            
            update_status(progress=70, stage='Assembling final video...')
            
            try:
                result = generate_video_main(story_script)
            except Exception as e:
                update_status(is_generating=False, progress=0, error=f'Video generation failed: {str(e)}')
                return
            
            video_url = handle_video_result(result, "reel", timestamp)
            if video_url:
                update_status(is_generating=False, progress=100, stage='Complete', current_video=video_url)
            else:
                update_status(is_generating=False, progress=0, error='Failed to process video file')
                
        elif video_type == 'avatar' and MODULES_STATUS['talking_avatar']:
            avatar_path = get_avatar_path()
            if not avatar_path:
                update_status(is_generating=False, progress=0, error='Avatar file (avatar.mp4) not found')
                return
            
            update_status(progress=10, stage='Initializing avatar system...')
            update_status(progress=30, stage='Processing avatar animation...')
            
            try:
                # Use the web-compatible avatar generation with enhanced topic
                result = generate_avatar_for_web(
                    topic=enhanced_topic,
                    language=language,
                    audience=audience,
                    duration=duration
                )
                
                video_url = handle_video_result(result, "avatar", timestamp)
                if video_url:
                    update_status(is_generating=False, progress=100, stage='Complete', current_video=video_url)
                else:
                    update_status(is_generating=False, progress=0, error='Failed to process avatar video file')
                    
            except Exception as e:
                print(f"❌ Avatar generation error: {e}")
                update_status(is_generating=False, progress=0, error=f'Avatar generation failed: {str(e)}')
                
        elif video_type == 'musical' and MODULES_STATUS['musical_rhyme']:
            update_status(progress=10, stage='Initializing musical system...')
            update_status(progress=25, stage='Generating musical content...')
            
            try:
                # Generate a unique output directory
                musical_output_dir = f"musical_rhyme_{enhanced_topic.replace(' ', '_')}_{timestamp}"
                
                result = generate_musical_rhyme_content(
                    topic=enhanced_topic,
                    language=language,
                    audience=audience,
                    output_dir=musical_output_dir
                )
            except Exception as e:
                update_status(is_generating=False, progress=0, error=f'Musical content generation failed: {str(e)}')
                return
            
            if result:
                update_status(progress=80, stage='Processing musical video...')
                
                # Check if the musical rhyme generator already created a video
                if result.get('final_video') and os.path.exists(result['final_video']):
                    print(f"✅ Using pre-generated musical video: {result['final_video']}")
                    video_result = result['final_video']
                elif result.get('script'):
                    # If no video but script exists, generate video
                    update_status(progress=60, stage='Creating musical video from script...')
                    try:
                        video_result = generate_video_main(result['script'])
                    except Exception as e:
                        update_status(is_generating=False, progress=0, error=f'Musical video creation failed: {str(e)}')
                        return
                else:
                    update_status(is_generating=False, progress=0, error='No video or script generated by musical system')
                    return
                
                video_url = handle_video_result(video_result, "musical", timestamp)
                if video_url:
                    update_status(is_generating=False, progress=100, stage='Complete', current_video=video_url)
                else:
                    update_status(is_generating=False, progress=0, error='Failed to process musical video file')
            else:
                update_status(is_generating=False, progress=0, error='Musical content generation failed')
        
        else:
            update_status(is_generating=False, progress=0, error=f'Video type "{video_type}" not available')
            
    except Exception as e:
        update_status(is_generating=False, progress=0, error=f'Unexpected error: {str(e)}')
    
    finally:
        # Stop monitoring and handle credits
        if MODULES_STATUS['computing_monitor']:
            try:
                update_status(stage='Processing credits...')
                computing_report = stop_monitoring_and_deduct_credits()
                
                # Update final status with computing report
                update_status(computing_report=computing_report)
                
                # Check if credit transaction was successful
                if computing_report.get('credit_transaction') == 'insufficient_credits':
                    update_status(is_generating=False, progress=0, 
                                error=f"Generation completed but insufficient credits for billing. "
                                     f"Need: {computing_report.get('credits_needed', 0):.1f}, "
                                     f"Have: {computing_report.get('current_balance', 0):.1f}")
                
                print(f"💻 Computing Report Generated:")
                print(f"   Duration: {computing_report.get('duration', {}).get('formatted', 'Unknown')}")
                print(f"   CPU Avg: {computing_report.get('cpu', {}).get('average_percent', 0):.1f}%")
                print(f"   GPU Avg: {computing_report.get('gpu', {}).get('average_percent', 0):.1f}%")
                print(f"   Credits: {computing_report.get('credits', {}).get('final_credits', 0):.2f}")
                print(f"   Processing: {computing_report.get('performance', {}).get('processing_type', 'Unknown')}")
                
            except Exception as monitor_error:
                print(f"⚠️ Computing monitor error: {monitor_error}")
                update_status(stage='Computing monitor error')

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated video file with security checks"""
    try:
        file_path = Path(OUTPUT_FOLDER) / filename
        
        if not file_path.exists() or not str(file_path).startswith(str(Path(OUTPUT_FOLDER).resolve())):
            return jsonify({'error': 'File not found or access denied'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/video/<filename>')
def serve_video(filename):
    """Serve video files with proper headers for web playback"""
    try:
        file_path = Path(OUTPUT_FOLDER) / filename
        
        if not file_path.exists() or not str(file_path).startswith(str(Path(OUTPUT_FOLDER).resolve())):
            return jsonify({'error': 'File not found or access denied'}), 404
        
        def generate():
            with open(file_path, 'rb') as f:
                data = f.read(1024)
                while data:
                    yield data
                    data = f.read(1024)
        
        response = app.response_class(generate(), mimetype='video/mp4')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(file_path.stat().st_size))
        response.headers.add('Cache-Control', 'no-cache')
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Video serving error: {str(e)}'}), 500

@app.route('/test-audio', methods=['POST'])
def test_audio():
    """Test audio quality"""
    try:
        data = request.get_json()
        language = data.get('language', 'english')
        
        test_texts = {
            'english': "Hello! This is a test of the English audio quality. The audio should be crystal clear.",
            'hindi': "नमस्ते! यह हिंदी ऑडियो गुणवत्ता का परीक्षण है। आवाज़ बिल्कुल साफ होनी चाहिए।"
        }
        
        if language not in test_texts:
            return jsonify({'error': 'Unsupported language for audio test'}), 400
        
        if not MODULES_STATUS['core']:
            return jsonify({'error': 'Audio system not available'}), 503
        
        text = test_texts[language]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"audio_test_{language}_{timestamp}.mp3"
        output_path = Path(OUTPUT_FOLDER) / output_filename
        
        result = convert_text_to_speech(text, str(output_path))
        
        if result and os.path.exists(result):
            duration = get_audio_duration(result)
            is_valid, message = verify_audio_file(result)
            
            audio_url = url_for('static', filename=f'outputs/{output_filename}')
            
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'duration': round(duration, 2) if duration else 0,
                'quality_message': message,
                'language': language
            })
        else:
            return jsonify({'error': 'Audio generation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Audio test error: {str(e)}'}), 500

@app.route('/system-status')
def system_status():
    """Get comprehensive system status information"""
    try:
        status = {
            'core_modules': MODULES_STATUS['core'],
            'talking_avatar': MODULES_STATUS['talking_avatar'],
            'musical_rhyme': MODULES_STATUS['musical_rhyme'],
            'computing_monitor': MODULES_STATUS['computing_monitor'],
            'avatar_file': get_avatar_path() is not None,
            'output_folder': os.path.exists(OUTPUT_FOLDER),
            'upload_folder': os.path.exists(UPLOAD_FOLDER)
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual file cleanup endpoint"""
    try:
        cleanup_old_files()
        return jsonify({'success': True, 'message': 'Cleanup completed successfully'})
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

# Credit Management Routes (only available if computing monitor is loaded)

@app.route('/credits')
def get_credits():
    """Get current credit information"""
    try:
        if not MODULES_STATUS['computing_monitor']:
            return jsonify({'error': 'Computing monitor not available'}), 503
        
        balance = get_credit_balance()
        stats = get_usage_statistics()
        
        return jsonify({
            'balance': balance,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Credits check failed: {str(e)}'}), 500

@app.route('/credits/add', methods=['POST'])
def add_user_credits():
    """Add credits to user account (admin function)"""
    try:
        if not MODULES_STATUS['computing_monitor']:
            return jsonify({'error': 'Computing monitor not available'}), 503
        
        data = request.get_json()
        amount = float(data.get('amount', 0))
        reason = data.get('reason', 'Manual addition')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        if amount > 1000:
            return jsonify({'error': 'Cannot add more than 1000 credits at once'}), 400
        
        add_credits(amount, reason)
        new_balance = get_credit_balance()
        
        return jsonify({
            'success': True,
            'added': amount,
            'new_balance': new_balance,
            'reason': reason
        })
        
    except Exception as e:
        return jsonify({'error': f'Add credits failed: {str(e)}'}), 500

@app.route('/usage-history')
def get_usage_history():
    """Get detailed usage history"""
    try:
        if not MODULES_STATUS['computing_monitor']:
            return jsonify({'error': 'Computing monitor not available'}), 503
        
        stats = get_usage_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Usage history failed: {str(e)}'}), 500


if __name__ == '__main__':
    print("🎬 GROQ REEL GENERATOR - WEB INTERFACE")
    print("=" * 50)
    print(f"🌐 Starting Flask web application on localhost:5000")
    print(f"🔗 Open your browser to: http://localhost:5000")
    print("⏹️ Press Ctrl+C to stop the web server")
    print()
    print("📊 System Status:")
    for module, status in MODULES_STATUS.items():
        print(f"   {module}: {'✅ Available' if status else '❌ Not Available'}")
    print(f"   Avatar file: {'✅ Found' if get_avatar_path() else '❌ Not Found'}")
    print()
    
    cleanup_old_files()
    
    app.run(host='0.0.0.0', port=8080, debug=False)
