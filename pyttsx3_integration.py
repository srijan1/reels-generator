"""
Functions for text-to-speech using pyttsx3 with enhanced macOS support.
This module handles TTS generation and audio timing synchronization.
"""
# Note: FFMPEG path modification should be handled by the main calling script.
import pyttsx3
import tempfile
import subprocess
import os
import json
import random
import time
import platform
from contextlib import contextmanager
from pydub import AudioSegment, effects # For CommercialAudioProcessor
import numpy as np # For CommercialAudioProcessor
from scipy import signal # For CommercialAudioProcessor
import re # For CommercialSSMLProcessor
from typing import Dict, List, Tuple # For CommercialSSMLProcessor

def generate_narration(image_prompt, original_text, desired_duration_seconds=7):
    """Generate more detailed narration content based on image prompt and original text"""
    try:
        # Create slightly enhanced versions of the original text
        # This simulates what Grok API would have done
        # enhancements = [
        #     f"As I {random.choice(['wandered', 'strolled', 'explored'])}, {original_text.lower()}",
        #     f"{original_text} The {random.choice(['sights', 'atmosphere', 'experience'])} left me speechless.",
        #     f"I couldn't believe it - {original_text.lower()} The memory will stay with me forever.",
        #     f"Finally experiencing {original_text.lower().replace('finally', '')} was everything I'd hoped for.",
        #     f"{original_text} Every moment felt like a scene from a movie."
        # ]
        
        # narration_text = random.choice(enhancements)
        narration_text = original_text
        print(f"Generated narration: {narration_text}")
        return narration_text
    
    except Exception as e:
        print(f"Error generating content: {e}")
        # Fallback to original text if anything fails
        return original_text

# --- Start of New/Modified Commercial Grade Functions ---

def initialize_commercial_engine():
    """Initialize pyttsx3 with optimal settings for commercial use"""
    engine = None
    # Platform-specific engine selection
    if platform.system() == "Windows":
        try:
            engine = pyttsx3.init('sapi5')  # Best quality on Windows
        except Exception as e:
            print(f"Warning: Failed to init sapi5, trying default: {e}")
            engine = pyttsx3.init()
    elif platform.system() == "Darwin":
        try:
            engine = pyttsx3.init('nsss')   # macOS native
        except Exception as e:
            print(f"Warning: Failed to init nsss, trying default: {e}")
            engine = pyttsx3.init()
    else:
        try:
            engine = pyttsx3.init('espeak') # Linux fallback
        except Exception as e:
            print(f"Warning: Failed to init espeak, trying default: {e}")
            engine = pyttsx3.init()
    
    if engine is None: # Should not happen if pyttsx3.init() works
        raise RuntimeError("Failed to initialize pyttsx3 engine.")

    # Commercial-optimized settings
    try:
        selected_voice_name = select_optimal_voice(engine) # This will set the voice
        print(f"Selected optimal voice: {selected_voice_name}")
    except Exception as e:
        print(f"Could not select optimal voice, using default: {e}")
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

    engine.setProperty('rate', 160)    # Slightly faster than default
    engine.setProperty('volume', 0.95) # Near maximum for clear delivery
    
    return engine

def select_optimal_voice(engine):
    """Select the best available voice for commercial use and set it on the engine."""
    voices = engine.getProperty('voices')
    if not voices:
        print("No voices found.")
        return "N/A (No voices)"

    # Voice quality ranking criteria (lower index = higher preference)
    quality_indicators = [
        'Neural', 'Premium',  # Highest quality
        'Enhanced', 
        'Zira', 'David', 'Hazel', # High-quality Microsoft voices
        'Mobile', # Often good quality, but can be less natural than Neural/Premium
        # Add other known good voice names or keywords
    ]
    
    scored_voices = []
    for voice in voices:
        score = 0
        # Assign a base score to ensure voices not matching indicators still get considered
        # We want to maximize the score, so indicators found earlier get higher points.
        # Max possible points for an indicator is len(quality_indicators).
        # We reverse the list for scoring: higher score for earlier items.
        reversed_quality_indicators = quality_indicators[::-1]
        for i, indicator in enumerate(reversed_quality_indicators):
            if indicator.lower() in voice.name.lower():
                score += (i + 1) # Higher score for better indicators
                # Optional: give a big boost for top-tier indicators
                if indicator in ['Neural', 'Premium']:
                    score += len(quality_indicators) # Extra boost
        
        # Consider gender preference if no strong indicators found (e.g., female often higher quality by default)
        if score == 0: # Only if no keywords matched
            if 'female' in voice.name.lower():
                score += 0.5 # Slight preference for female if no other indicators

        scored_voices.append((voice, score))
    
    if not scored_voices:
        print("No voices could be scored.")
        return "N/A (Scoring failed)"

    # Select highest-scoring voice
    scored_voices.sort(key=lambda x: x[1], reverse=True)
    best_voice_obj = scored_voices[0][0]
    
    engine.setProperty('voice', best_voice_obj.id)
    return best_voice_obj.name


class CommercialSSMLProcessor:
    """Process SSML-like markup for enhanced pyttsx3 output"""
    
    def __init__(self, engine):
        self.engine = engine
        self.base_rate = engine.getProperty('rate')
        self.base_volume = engine.getProperty('volume')
    
    def parse_ssml_text(self, text: str) -> List[Dict]:
        segments = []
        current_pos = 0
        emphasis_pattern = r'<emphasis level="(strong|moderate|reduced)">(.*?)</emphasis>'
        break_pattern = r'<break time="(\d+)ms"/>'
        
        tags = []
        for match in re.finditer(emphasis_pattern, text, re.DOTALL):
            tags.append({'type': 'emphasis', 'start': match.start(), 'end': match.end(), 'level': match.group(1), 'content': match.group(2)})
        for match in re.finditer(break_pattern, text, re.DOTALL):
            tags.append({'type': 'break', 'start': match.start(), 'end': match.end(), 'time_ms': int(match.group(1))})
        tags.sort(key=lambda t: t['start'])
        
        for tag in tags:
            if tag['start'] > current_pos:
                segments.append({'text': text[current_pos:tag['start']], 'rate': self.base_rate, 'volume': self.base_volume})
            if tag['type'] == 'emphasis':
                level, content = tag['level'], tag['content']
                rate_multiplier = {'strong': 0.9, 'moderate': 0.95, 'reduced': 1.1}[level]
                volume_multiplier = {'strong': 1.1, 'moderate': 1.05, 'reduced': 0.9}[level]
                inner_segments = self._process_text_for_breaks(content, int(self.base_rate * rate_multiplier), min(1.0, self.base_volume * volume_multiplier))
                segments.extend(inner_segments)
            elif tag['type'] == 'break':
                segments.append({'pause_ms': tag['time_ms']})
            current_pos = tag['end']
        if current_pos < len(text):
            segments.append({'text': text[current_pos:], 'rate': self.base_rate, 'volume': self.base_volume})
        return [s for s in segments if ('text' in s and s['text'].strip()) or 'pause_ms' in s]

    def _process_text_for_breaks(self, text_content: str, current_rate: int, current_volume: float) -> List[Dict]:
        sub_segments = []
        current_sub_pos = 0
        break_pattern = r'<break time="(\d+)ms"/>'
        for match in re.finditer(break_pattern, text_content, re.DOTALL):
            if match.start() > current_sub_pos:
                sub_segments.append({'text': text_content[current_sub_pos:match.start()], 'rate': current_rate, 'volume': current_volume})
            sub_segments.append({'pause_ms': int(match.group(1))})
            current_sub_pos = match.end()
        if current_sub_pos < len(text_content):
            sub_segments.append({'text': text_content[current_sub_pos:], 'rate': current_rate, 'volume': current_volume})
        return [s for s in sub_segments if ('text' in s and s['text'].strip()) or 'pause_ms' in s]

    def speak_ssml_to_file(self, marked_text: str, output_filepath: str) -> str:
        segments_props = self.parse_ssml_text(marked_text)
        if not segments_props:
            self.engine.setProperty('rate', self.base_rate)
            self.engine.setProperty('volume', self.base_volume)
            self.engine.save_to_file(marked_text, output_filepath)
            self.engine.runAndWait()
            return output_filepath

        final_audio = AudioSegment.empty()
        temp_files = []
        for i, props in enumerate(segments_props):
            temp_segment_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            temp_files.append(temp_segment_file)
            if 'text' in props and props['text']:
                self.engine.setProperty('rate', props['rate'])
                self.engine.setProperty('volume', props['volume'])
                self.engine.save_to_file(props['text'], temp_segment_file)
                self.engine.runAndWait()
                time.sleep(0.2) 
                try:
                    segment_audio = AudioSegment.from_wav(temp_segment_file)
                    final_audio += segment_audio
                except Exception as e:
                    print(f"Warning: Could not load/process segment {temp_segment_file}: {e}")
            elif 'pause_ms' in props:
                if props['pause_ms'] > 0:
                    final_audio += AudioSegment.silent(duration=props['pause_ms'])
        final_audio.export(output_filepath, format="wav")
        for temp_file in temp_files:
            try: os.remove(temp_file)
            except OSError: pass
        return output_filepath


class CommercialAudioProcessor:
    """Enhance pyttsx3 output with commercial-grade post-processing"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
    def enhance_tts_audio(self, input_file: str, output_file: str) -> str:
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            print(f"Error: Input audio file {input_file} is missing or empty. Skipping enhancement.")
            AudioSegment.silent(duration=100).export(output_file, format="wav")
            return output_file
        try:
            audio = AudioSegment.from_file(input_file)
        except Exception as e:
            print(f"Error loading audio file {input_file}: {e}. Skipping enhancement.")
            AudioSegment.silent(duration=100).export(output_file, format="wav")
            return output_file
        
        audio = audio.set_frame_rate(self.sample_rate).set_channels(1)
        audio = effects.normalize(audio, headroom=0.1)
        audio = self.apply_noise_gate(audio, threshold_db=-45)
        audio = audio.high_pass_filter(80).low_pass_filter(12000)
        audio = self.apply_commercial_compression(audio)
        audio = self.enhance_vocal_presence(audio)
        audio = audio.fade_in(50).fade_out(100)
        audio.export(output_file, format="wav", parameters=["-ac", "1", "-ar", str(self.sample_rate)])
        return output_file
    
    def apply_noise_gate(self, audio: AudioSegment, threshold_db: float) -> AudioSegment:
        if audio.frame_width == 0 or audio.frame_rate == 0: return audio
        samples = np.array(audio.get_array_of_samples())
        if samples.size == 0: return audio
        window_size = max(1, int(0.02 * audio.frame_rate))
        samples_float = samples.astype(np.float32) if samples.dtype not in [np.float32, np.float64] else samples
        if len(samples_float) < window_size:
            rms_val = np.sqrt(np.mean(samples_float**2))
            rms = np.full_like(samples_float, rms_val)
        else:
            rms_squared = np.convolve(samples_float**2, np.ones(window_size)/window_size, mode='same')
            rms = np.sqrt(np.maximum(rms_squared, 0))
        max_rms = np.max(rms) if rms.size > 0 else 0
        if max_rms == 0: return audio
        threshold_linear = 10**(threshold_db/20) * max_rms 
        gate_mask = rms > threshold_linear
        gated_samples = samples * gate_mask
        return audio._spawn(gated_samples.astype(samples.dtype))
    
    def apply_commercial_compression(self, audio: AudioSegment) -> AudioSegment:
        return effects.compress_dynamic_range(audio, threshold=-20.0, ratio=4.0, attack=5.0, release=100.0)
    
    def enhance_vocal_presence(self, audio: AudioSegment) -> AudioSegment:
        if audio.frame_width == 0 or audio.frame_rate == 0: return audio
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        if samples.size == 0: return audio
        nyquist = audio.frame_rate / 2.0
        low_f, high_f = 2000.0, 5000.0
        if high_f >= nyquist: high_f = nyquist * 0.99
        if low_f >= high_f: low_f = high_f * 0.8
        if low_f <= 0: low_f = 1.0
        low_cut, high_cut = low_f / nyquist, high_f / nyquist
        if low_cut >= high_cut or high_cut >= 1.0 or low_cut <= 0.0:
            print(f"Warning: Invalid filter band ({low_cut}, {high_cut}). Skipping vocal presence enhancement.")
            return audio
        try:
            sos = signal.butter(2, [low_cut, high_cut], btype='bandpass', output='sos')
            boosted_signal = signal.sosfilt(sos, samples)
            enhanced_samples = samples * 0.85 + boosted_signal * 0.15
            return audio._spawn(enhanced_samples.astype(np.int16))
        except Exception as e:
            print(f"Error during vocal presence enhancement with SciPy: {e}. Returning original audio.")
            return audio

# --- End of New/Modified Commercial Grade Functions ---

@contextmanager
def get_tts_engine(): # Modified to use initialize_commercial_engine
    """Initialize and clean up the TTS engine using a context manager"""
    engine = initialize_commercial_engine()
    try:
        yield engine
    finally:
        # It's good practice to ensure engine.stop() is called,
        # but pyttsx3 engines are often meant to be long-lived.
        # If runAndWait() is used, stop might not be strictly necessary after each call.
        # However, for a context manager, cleaning up is good.
        try:
            engine.stop()
        except RuntimeError as e:
            # Can happen if engine is already stopped or in a bad state.
            print(f"Note: Error stopping engine (might be already stopped): {e}")
        del engine # Help with garbage collection

def convert_text_to_speech_mac(text, output_path, voice="default"):
    """macOS-specific text-to-speech using 'say' command
    
    This is more reliable on macOS systems than pyttsx3
    
    Parameters:
    - text: Text to convert to speech
    - output_path: Path to save audio file
    - voice: Voice name (will attempt to use if available)
    """
    raw_output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name # Ensure WAV for processor
    
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
        # enhancements = [
        #     f"As I {random.choice(['wandered', 'strolled', 'explored'])}, {original_text.lower()}",
        #     f"{original_text} The {random.choice(['sights', 'atmosphere', 'experience'])} left me speechless.",
        #     f"I couldn't believe it - {original_text.lower()} The memory will stay with me forever.",
        #     f"Finally experiencing {original_text.lower().replace('finally', '')} was everything I'd hoped for.",
        #     f"{original_text} Every moment felt like a scene from a movie."
        # ]
        
        # narration_text = random.choice(enhancements)
        narration_text = original_text
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
        
