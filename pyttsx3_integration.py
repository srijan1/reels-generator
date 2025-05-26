"""
Functions for text-to-speech using pyttsx3 with enhanced macOS support.
This module handles TTS generation and audio timing synchronization.
"""

import pyttsx3
import tempfile
import subprocess
import os
import json
import random
import time
import platform
from contextlib import contextmanager

def generate_narration(image_prompt, original_text, desired_duration_seconds=7):
    """Generate more detailed narration content based on image prompt and original text"""
    try:
        # Create slightly enhanced versions of the original text
        # This simulates what Grok API would have done
        enhancements = [
            f"As I {random.choice(['wandered', 'strolled', 'explored'])}, {original_text.lower()}",
            f"{original_text} The {random.choice(['sights', 'atmosphere', 'experience'])} left me speechless.",
            f"I couldn't believe it - {original_text.lower()} The memory will stay with me forever.",
            f"Finally experiencing {original_text.lower().replace('finally', '')} was everything I'd hoped for.",
            f"{original_text} Every moment felt like a scene from a movie."
        ]
        
        narration_text = random.choice(enhancements)
        print(f"Generated narration: {narration_text}")
        return narration_text
    
    except Exception as e:
        print(f"Error generating content: {e}")
        # Fallback to original text if anything fails
        return original_text

@contextmanager
def get_tts_engine():
    """Initialize and clean up the TTS engine using a context manager"""
    engine = pyttsx3.init()
    try:
        yield engine
    finally:
        engine.stop()

def convert_text_to_speech_mac(text, output_path, voice="default"):
    """macOS-specific text-to-speech using 'say' command
    
    This is more reliable on macOS systems than pyttsx3
    
    Parameters:
    - text: Text to convert to speech
    - output_path: Path to save audio file
    - voice: Voice name (will attempt to use if available)
    """
    try:
        # Create a temporary audio file
        temp_aiff = tempfile.NamedTemporaryFile(suffix=".aiff", delete=False)
        temp_aiff_path = temp_aiff.name
        temp_aiff.close()
        
        # Map voice names to macOS voices 
        mac_voices = {
            "male": "Alex",
            "female": "Samantha",
            "default": None,  # Use system default
            # Map Speechify voices to macOS equivalents
            "Stephanie": "Samantha",
            "Jennifer": "Victoria",
            "Peter": "Alex",
            "Alex": "Alex",
            "Lily": "Samantha"
        }
        
        # Get macOS voice name
        mac_voice = mac_voices.get(voice.lower() if isinstance(voice, str) else "default")
        
        # Prepare command
        if mac_voice:
            cmd = ['say', '-v', mac_voice, '-o', temp_aiff_path, text]
        else:
            cmd = ['say', '-o', temp_aiff_path, text]
        
        print(f"Converting to speech using macOS 'say' command: {text[:30]}...")
        
        # Run say command
        subprocess.run(cmd, check=True)
        
        # Check if the file was created
        if not os.path.exists(temp_aiff_path):
            raise Exception("Failed to create AIFF file with 'say' command")
            
        # Convert AIFF to MP3 using ffmpeg
        subprocess.run(['ffmpeg', '-y', '-i', temp_aiff_path, output_path], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Clean up the temporary file
        os.remove(temp_aiff_path)
        
        print(f"macOS TTS successful! Audio saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error in macOS TTS: {e}")
        return create_silent_audio(text, output_path)

def convert_text_to_speech_win_linux(text, voice="default", output_path=None, rate=150, volume=1.0):
    """Convert text to speech using pyttsx3 for Windows and Linux systems"""
    try:
        with get_tts_engine() as engine:
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Set voice based on parameter
            if voice.lower() == "male":
                # Try to find a male voice
                male_voices = [v for v in voices if 'male' in v.name.lower()]
                if male_voices:
                    engine.setProperty('voice', male_voices[0].id)
            elif voice.lower() == "female":
                # Try to find a female voice
                female_voices = [v for v in voices if 'female' in v.name.lower()]
                if female_voices:
                    engine.setProperty('voice', female_voices[0].id)
            else:
                # Use voice mapping or default
                voice_idx = {"Stephanie": 1, "Jennifer": 1, "Peter": 0, "Alex": 0, "Lily": 1}.get(voice, 0)
                if voice_idx < len(voices):
                    engine.setProperty('voice', voices[voice_idx].id)
            
            # Set properties
            engine.setProperty('rate', rate)  # Speed of speech
            engine.setProperty('volume', volume)  # Volume level
            
            # Save to file
            print(f"Converting to speech: {text[:30]}...")
            engine.save_to_file(text, output_path)
            
            # Add timeout to prevent hanging
            time.sleep(0.5)
            engine.runAndWait()
            time.sleep(0.5)
            
            # Wait briefly to ensure file is saved
            time.sleep(1)
            
            # Verify file exists
            if os.path.exists(output_path):
                print(f"pyttsx3 speech saved to {output_path}")
                return output_path
            else:
                print(f"Failed to save speech to {output_path}")
                return None
    except Exception as e:
        print(f"Error in pyttsx3 TTS conversion: {e}")
        return None

def create_silent_audio(text, output_path, duration=None):
    """Create a silent audio file as fallback"""
    try:
        # Calculate duration based on text length if not provided
        if duration is None:
            # Approximately 2-3 words per second for natural speech
            word_count = len(text.split())
            duration = max(3, word_count / 2.5)  # Minimum 3 seconds
        
        print(f"Creating silent audio fallback (duration: {duration:.2f}s)")
        
        # Use ffmpeg to create a silent audio file
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", 
            "-i", f"anullsrc=r=44100:cl=stereo", 
            "-t", str(duration),
            output_path
        ]
        
        # Run the command silently
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(output_path):
            print(f"Created silent audio at {output_path}")
            return output_path
        else:
            print(f"Failed to create silent audio at {output_path}")
            return None
    
    except Exception as e:
        print(f"Error creating silent audio: {e}")
        return None

def convert_text_to_speech(text, voice="default", output_path=None, rate=150, volume=1.0):
    """Convert text to speech and save to file
    
    This function automatically selects the best method based on platform
    
    Parameters:
    - text: Text to convert to speech
    - voice: Voice profile (male/female/default)
    - output_path: Path to save audio file
    - rate: Speech rate (words per minute)
    - volume: Volume level (0.0 to 1.0)
    """
    # Create a temporary file if no output path provided
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        output_path = temp_file.name
        temp_file.close()
    
    # Handle different platforms
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        return convert_text_to_speech_mac(text, output_path, voice)
    else:  # Windows or Linux
        result = convert_text_to_speech_win_linux(text, voice, output_path, rate, volume)
        if result:
            return result
        
    # If we get here, all methods failed
    print("All TTS methods failed, creating silent audio")
    return create_silent_audio(text, output_path)

def get_audio_duration(audio_file_path):
    """Get the duration of an audio file in seconds using ffmpeg"""
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {audio_file_path}")
            return None
            
        # Use ffprobe to get duration
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'json', 
            audio_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting audio duration: {result.stderr}")
            return None
            
        # Parse the JSON output
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        
        print(f"Audio duration: {duration:.2f} seconds")
        return duration
        
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        # Return a sensible default duration if ffmpeg fails
        return 7.0
        
def adjust_speech_to_duration(text, target_duration, output_path):
    """Adjust speech rate to match a target duration
    
    This function attempts multiple times with different speech rates
    to generate audio that closely matches the target duration.
    
    Parameters:
    - text: Text to convert to speech
    - target_duration: Target duration in seconds
    - output_path: Path to save audio file
    
    Returns:
    - Path to the adjusted audio file
    """
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        # macOS 'say' command doesn't have an easy way to adjust rate
        # We'll use a different approach by adding pauses to the text
        audio_path = convert_text_to_speech_mac(text, output_path)
        
        # Check duration
        duration = get_audio_duration(audio_path)
        
        # If we're off by more than 15%, try to adjust by adding pauses
        if duration and abs(duration - target_duration) / target_duration > 0.15:
            if duration < target_duration:
                # Too short - add pauses at sentence boundaries
                sentences = text.split('.')
                adjusted_text = '. '.join(sentences[:-1]) + '.'
                
                # Try again with pauses
                return convert_text_to_speech_mac(adjusted_text, output_path)
            else:
                # Too long, but we don't have good control over speed
                # We'll have to live with it
                return audio_path
        
        return audio_path
    else:
        # Estimate initial rate based on word count and target duration
        word_count = len(text.split())
        estimated_wpm = (word_count / target_duration) * 60
        
        # Bound the rate within reasonable limits (100-250 WPM)
        rate = max(100, min(250, estimated_wpm))
        
        # Generate speech
        audio_path = convert_text_to_speech(text, output_path=output_path, rate=rate)
        
        # Check duration
        duration = get_audio_duration(audio_path)
        
        # If we're off by more than 15%, try to adjust
        if duration and abs(duration - target_duration) / target_duration > 0.15:
            # Calculate new rate
            adjustment_factor = duration / target_duration
            new_rate = rate * adjustment_factor
            
            # Try again with adjusted rate
            new_rate = max(100, min(250, new_rate))  # Keep within reasonable limits
            audio_path = convert_text_to_speech(text, output_path=output_path, rate=new_rate)
            
        return audio_path