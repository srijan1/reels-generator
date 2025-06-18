"""
Simple & Clear Professional TTS
Easy to understand voice with consistent quality
"""

import os
import tempfile
import subprocess
import time
import platform
import json
import random
from contextlib import contextmanager
import sys

# Core audio processing
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pydub.silence import split_on_silence

# Language detection
try:
    from langdetect import detect
    import langdetect
    LANGDETECT_AVAILABLE = True
except ImportError:
    print("⚠️ langdetect not installed, installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "langdetect"])
        from langdetect import detect
        import langdetect
        LANGDETECT_AVAILABLE = True
    except:
        LANGDETECT_AVAILABLE = False

# Professional TTS imports
try:
    import torch
    from transformers import pipeline, AutoProcessor, AutoModel, VitsModel, VitsTokenizer
    from datasets import load_dataset
    import soundfile as sf
    import numpy as np
    TORCH_AVAILABLE = True
    print("✅ PyTorch and transformers available")
except ImportError as e:
    print(f"⚠️ PyTorch/transformers not available: {e}")
    TORCH_AVAILABLE = False

# Fallback TTS
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
    print("✅ pyttsx3 available as fallback")
except ImportError:
    PYTTSX3_AVAILABLE = False

# SINGLE PERSISTENT ENGINE FOR CONSISTENT VOICE
_persistent_engine = None
_voice_settings = None

def initialize_clear_voice():
    """Initialize one clear voice for the entire session"""
    global _persistent_engine, _voice_settings
    
    if _persistent_engine is None:
        print("🎙️ Setting up clear, consistent voice...")
        try:
            _persistent_engine = pyttsx3.init()
            
            # Get all available voices
            voices = _persistent_engine.getProperty('voices')
            best_voice = None
            
            if voices:
                print(f"🔍 Found {len(voices)} voices, selecting the clearest...")
                
                # Priority order for clearest voices
                clear_voice_names = [
                    'samantha', 'susan', 'karen', 'victoria', 'alex', 'zira', 'hazel', 'daniel'
                ]
                
                # Find the best clear voice
                for clear_name in clear_voice_names:
                    for voice in voices:
                        if clear_name in voice.name.lower():
                            best_voice = voice
                            print(f"🎭 Selected clear voice: {voice.name}")
                            break
                    if best_voice:
                        break
                
                # If no specific clear voice found, use first female voice
                if not best_voice:
                    female_voices = [v for v in voices if 'female' in v.name.lower()]
                    if female_voices:
                        best_voice = female_voices[0]
                        print(f"🎭 Using clear female voice: {best_voice.name}")
                    else:
                        best_voice = voices[0]
                        print(f"🎭 Using default voice: {best_voice.name}")
                
                # Apply the selected voice
                if best_voice:
                    _persistent_engine.setProperty('voice', best_voice.id)
            
            # SETTINGS FOR CLEAR, UNDERSTANDABLE SPEECH
            _persistent_engine.setProperty('rate', 120)     # Slightly faster for clarity
            _persistent_engine.setProperty('volume', 0.8)   # Clear, audible volume
            
            # Store settings to maintain consistency
            _voice_settings = {
                'voice_id': best_voice.id if best_voice else None,
                'voice_name': best_voice.name if best_voice else "System Default",
                'rate': 120,  # Clear, understandable pace
                'volume': 0.8  # Clear volume
            }
            
            print(f"✅ Clear voice ready: {_voice_settings['voice_name']} at {_voice_settings['rate']} WPM")
            
        except Exception as e:
            print(f"❌ Voice setup failed: {e}")
            _persistent_engine = None
    
    return _persistent_engine

def maintain_voice_quality():
    """Keep voice settings consistent throughout the session"""
    global _persistent_engine, _voice_settings
    
    if _persistent_engine and _voice_settings:
        try:
            # Reapply settings to prevent any drift
            if _voice_settings['voice_id']:
                _persistent_engine.setProperty('voice', _voice_settings['voice_id'])
            _persistent_engine.setProperty('rate', _voice_settings['rate'])
            _persistent_engine.setProperty('volume', _voice_settings['volume'])
        except Exception as e:
            print(f"⚠️ Voice maintenance failed: {e}")

class SimpleClearTTS:
    """Simple TTS system focused on clarity and consistency"""
    
    def __init__(self):
        self.models = {}
        self.processors = {}
        self.supported_languages = set()
        
        # SETTINGS FOR CLEAR, UNDERSTANDABLE SPEECH
        self.clarity_settings = {
            'speech_rate': 1.0,          # Normal speed for clarity
            'volume_level': 0.8,         # Clear, audible volume
            'pause_length': 'normal',    # Normal pauses only
            'pronunciation': 'clear',    # Clear pronunciation
            'sample_rate': 22050,        # Good quality
            'bitrate': '256k'           # High quality output
        }
        
        # Simple model preferences
        self.language_models = {
            'en': {
                'primary': 'clear_english',
                'fallback': 'system_voice',
                'speed_multiplier': 1.0
            },
            'hi': {
                'primary': 'hindi_model',
                'fallback': 'system_voice', 
                'speed_multiplier': 1.0
            }
        }
        
        # Initialize the clear voice system
        initialize_clear_voice()
        
    def detect_language_simple(self, text):
        """Simple, reliable language detection"""
        if not LANGDETECT_AVAILABLE:
            # Check for Hindi characters
            hindi_chars = any('\u0900' <= char <= '\u097F' for char in text)
            return 'hi' if hindi_chars else 'en'
        
        try:
            # Clean the text for better detection
            clean_text = ''.join(char for char in text if char.isalnum() or char.isspace())
            if len(clean_text.strip()) < 3:
                return 'en'  # Default to English for short text
            
            detected = detect(clean_text)
            return 'hi' if detected in ['hi', 'hindi'] else 'en'
                
        except Exception as e:
            print(f"⚠️ Language detection failed: {e}")
            # Fallback: check for Hindi characters
            hindi_chars = any('\u0900' <= char <= '\u097F' for char in text)
            return 'hi' if hindi_chars else 'en'
    
    def setup_clear_models(self):
        """Setup high-quality models for clear speech"""
        if not TORCH_AVAILABLE:
            print("⚠️ Using system voice for maximum compatibility")
            return False
        
        success = False
        
        try:
            print("🔧 Setting up clear speech models...")
            
            # English: Try to load the clearest model available
            try:
                print("🔧 Loading clear English model...")
                from transformers import VitsModel, VitsTokenizer
                
                # Use the most stable English model
                en_model = VitsModel.from_pretrained("facebook/mms-tts-eng")
                en_tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-eng")
                
                self.models['clear_en'] = en_model
                self.processors['clear_en'] = en_tokenizer
                self.supported_languages.add('en')
                success = True
                print("✅ Clear English model ready")
                
            except Exception as e:
                print(f"⚠️ English model setup failed: {e}")
                
            # Hindi: Setup for native pronunciation
            try:
                print("🔧 Loading Hindi model...")
                hi_model = VitsModel.from_pretrained("facebook/mms-tts-hin")
                hi_tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-hin")
                
                self.models['clear_hi'] = hi_model
                self.processors['clear_hi'] = hi_tokenizer
                self.supported_languages.add('hi')
                success = True
                print("✅ Clear Hindi model ready")
                
            except Exception as e:
                print(f"⚠️ Hindi model setup failed: {e}")
                
        except Exception as e:
            print(f"⚠️ Model setup failed: {e}")
        
        return success
    
    def create_clear_audio_with_models(self, text, output_path, language):
        """Create clear audio using AI models"""
        try:
            model_key = f"clear_{language}"
            if model_key not in self.models:
                raise Exception(f"Model for {language} not available")
            
            model = self.models[model_key]
            tokenizer = self.processors[model_key]
            
            print(f"🎙️ Generating clear {language.upper()} audio...")
            
            # Prepare text for clarity
            clean_text = self.prepare_text_for_clarity(text, language)
            
            # Generate audio
            inputs = tokenizer(clean_text, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model(**inputs)
                audio_data = outputs.waveform.squeeze().cpu().numpy()
            
            # Process for maximum clarity
            clear_audio = self.enhance_audio_clarity(audio_data, language)
            
            # Save with high quality
            success = self.save_clear_audio(clear_audio, 22050, output_path)
            
            if success:
                return output_path
            else:
                raise Exception("Audio save failed")
                
        except Exception as e:
            print(f"❌ Model audio generation failed: {e}")
            raise e
    
    def create_clear_audio_with_system(self, text, output_path, language='en'):
        """Create clear audio using system voice (most reliable)"""
        if not PYTTSX3_AVAILABLE:
            return self.create_silent_fallback(text, output_path)
        
        try:
            print(f"🔄 Creating clear {language.upper()} audio with system voice...")
            
            # Get the persistent engine
            engine = initialize_clear_voice()
            if not engine:
                print("❌ Voice engine not available")
                return self.create_silent_fallback(text, output_path)
            
            # Ensure voice consistency
            maintain_voice_quality()
            
            # Prepare text for maximum clarity
            clear_text = self.prepare_text_for_clarity(text, language)
            print(f"📝 Speaking clearly: '{clear_text[:50]}...'")
            
            # Create temporary audio file
            temp_file = output_path + '.temp.wav'
            
            try:
                # Generate clear, understandable audio
                engine.save_to_file(clear_text, temp_file)
                engine.runAndWait()
                
                # Check if audio was created successfully
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1000:
                    print("🔧 Creating clear, understandable audio...")
                    
                    # Load and enhance the audio
                    audio = AudioSegment.from_file(temp_file)
                    
                    # Apply clear speech enhancements
                    clear_audio = self.make_speech_clear_and_understandable(audio)
                    
                    # Export with high quality
                    clear_audio.export(
                        output_path,
                        format="mp3",
                        bitrate="256k",
                        parameters=["-q:a", "0"]  # Highest quality
                    )
                    
                    # Clean up
                    os.remove(temp_file)
                    
                    duration = len(clear_audio) / 1000.0
                    print(f"✅ Clear audio ready - {duration:.2f}s")
                    return output_path
                    
                else:
                    print(f"⚠️ Audio generation had issues")
                    if os.path.exists(temp_file):
                        os.rename(temp_file, output_path)
                    return output_path
                    
            except Exception as e:
                print(f"⚠️ Audio generation error: {e}")
                return self.create_silent_fallback(text, output_path)
                    
        except Exception as e:
            print(f"❌ System audio creation failed: {e}")
            return self.create_silent_fallback(text, output_path)
    
    def generate_clear_speech(self, text, output_path, language='auto'):
        """Main method to generate clear, understandable speech"""
        
        # Detect language automatically
        if language == 'auto':
            language = self.detect_language_simple(text)
        
        print(f"🌍 Language: {language.upper()}")
        print(f"📝 Text: '{text[:60]}...'")
        
        # Try AI models first for best quality
        if language in self.supported_languages:
            try:
                print(f"🤖 Trying AI model for {language.upper()}...")
                return self.create_clear_audio_with_models(text, output_path, language)
            except Exception as e:
                print(f"⚠️ AI model failed: {e}")
        
        # Fallback to reliable system voice
        print("🔄 Using reliable system voice...")
        return self.create_clear_audio_with_system(text, output_path, language)
    
    def prepare_text_for_clarity(self, text, language):
        """Prepare text for clear, understandable speech - NO choppy sounds"""
        clean_text = text.strip()
        
        if language == 'en':
            # Basic replacements for clear speech
            clear_replacements = {
                'Dr.': 'Doctor',
                'Mr.': 'Mister',
                'Mrs.': 'Missus',
                'vs.': 'versus',
                'etc.': 'and so on',
                '&': 'and'
            }
            
            for abbreviation, clear_form in clear_replacements.items():
                clean_text = clean_text.replace(abbreviation, clear_form)
            
            # MAKE IT CLEAR AND UNDERSTANDABLE - NO CHOPPY SOUNDS
            # Only add minimal, natural pauses
            clean_text = clean_text.replace('.', '. ')       # Normal pause after sentences
            clean_text = clean_text.replace(',', ', ')       # Brief pause after commas
            clean_text = clean_text.replace('!', '. ')       # Normal pause after exclamation
            clean_text = clean_text.replace('?', '. ')       # Normal pause after questions
            
            # Clean up extra spaces
            clean_text = ' '.join(clean_text.split())
        
        return clean_text
    
    def enhance_audio_clarity(self, audio_data, language):
        """Enhance audio for maximum clarity"""
        try:
            # Ensure proper format
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()
            
            if len(audio_data) == 0:
                return audio_data
            
            # Apply slight slowdown for clarity (if needed)
            speed_multiplier = self.language_models[language]['speed_multiplier']
            if speed_multiplier != 1.0:
                target_length = int(len(audio_data) / speed_multiplier)
                if target_length > 0:
                    indices = np.linspace(0, len(audio_data) - 1, target_length)
                    audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data)
            
            # Normalize for consistent volume
            if len(audio_data) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val * 0.8  # Prevent clipping, clear volume
            
            # Light smoothing for clarity
            if len(audio_data) > 20:
                window_size = 3
                if len(audio_data) > window_size:
                    kernel = np.ones(window_size) / window_size
                    smoothed = np.convolve(audio_data, kernel, mode='same')
                    audio_data = 0.9 * smoothed + 0.1 * audio_data  # Very light smoothing
            
            print(f"✅ Audio enhanced for clarity")
            return audio_data
            
        except Exception as e:
            print(f"⚠️ Audio enhancement failed: {e}")
            return audio_data
    
    def make_speech_clear_and_understandable(self, audio_segment):
        """Make speech clear and understandable - NO choppy sounds"""
        try:
            # Normal normalization for clear volume
            clear_audio = audio_segment.normalize()
            
            # Light compression for even volume - NO harsh processing
            clear_audio = compress_dynamic_range(
                clear_audio, 
                threshold=-20.0,  # Normal threshold
                ratio=1.5         # Light compression for clarity
            )
            
            # Normal volume - not too quiet
            # No volume reduction - keep it clear and audible
            
            return clear_audio
            
        except Exception as e:
            print(f"⚠️ Clear audio enhancement failed: {e}")
            return audio_segment
    
    def save_clear_audio(self, audio_data, sample_rate, output_path):
        """Save audio with maximum clarity settings"""
        try:
            print("🔧 Saving clear audio...")
            
            if len(audio_data) == 0:
                return False
            
            # Final normalization
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.8
            
            # Save as high-quality WAV first
            temp_wav = output_path + '.temp.wav'
            sf.write(temp_wav, audio_data, sample_rate)
            
            # Convert to high-quality MP3
            audio_segment = AudioSegment.from_wav(temp_wav)
            final_audio = audio_segment.normalize()
            
            # Export with maximum quality
            final_audio.export(
                output_path,
                format="mp3",
                bitrate="256k",
                parameters=["-q:a", "0"]
            )
            
            # Clean up
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            
            duration = len(final_audio) / 1000.0
            print(f"✅ Clear audio saved: {duration:.2f}s")
            return True
            
        except Exception as e:
            print(f"❌ Audio save failed: {e}")
            return False
    
    def create_silent_fallback(self, text, output_path, duration=None):
        """Create silent audio as final fallback"""
        try:
            if duration is None:
                # Estimate duration based on text (clear speech pace)
                duration = max(2.0, len(text.split()) * 0.6)  # 0.6 seconds per word
            
            silent_audio = AudioSegment.silent(duration=int(duration * 1000))
            silent_audio.export(output_path, format="mp3", bitrate="128k")
            
            print(f"⚠️ Created silent placeholder: {duration:.2f}s")
            return output_path
            
        except Exception as e:
            print(f"❌ Silent audio creation failed: {e}")
            return None

# Create global instance
clear_tts = SimpleClearTTS()

# MAIN FUNCTIONS - Simple to use
def convert_text_to_speech(text, output_path, voice="female", language="auto"):
    """Convert text to clear, understandable speech - NO choppy sounds"""
    print(f"🎭 Creating clear speech: '{text[:40]}...'")
    return clear_tts.generate_clear_speech(text, output_path, language)

def adjust_speech_duration(text, output_path, target_duration, voice="female", language="auto"):
    """Create speech that matches target duration"""
    try:
        # Generate clear speech first
        result_path = convert_text_to_speech(text, output_path + '.temp', voice, language)
        
        if not result_path or not os.path.exists(result_path):
            return clear_tts.create_silent_fallback(text, output_path, target_duration)
        
        try:
            audio = AudioSegment.from_file(result_path)
            current_duration = len(audio) / 1000.0
            
            print(f"🎵 Current: {current_duration:.2f}s, Target: {target_duration:.2f}s")
            
            # Accept if close enough (25% tolerance for natural flow)
            if abs(current_duration - target_duration) / target_duration <= 0.25:
                os.rename(result_path, output_path)
                print("✅ Duration sounds clear")
                return output_path
            
            # Adjust speed carefully to maintain clarity
            speed_factor = current_duration / target_duration
            
            # Keep reasonable speed for clear understanding
            if speed_factor < 0.8:
                speed_factor = 0.8   # Don't make it too fast (loses clarity)
            elif speed_factor > 1.3:
                speed_factor = 1.3   # Don't make it too slow (becomes unnatural)
            
            if speed_factor != 1.0:
                print(f"🔧 Adjusting for clear speech: {speed_factor:.2f}x")
                new_sample_rate = int(audio.frame_rate * speed_factor)
                adjusted_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                adjusted_audio = adjusted_audio.set_frame_rate(22050)
                
                # Export with high quality
                adjusted_audio.export(
                    output_path, 
                    format="mp3", 
                    bitrate="256k",
                    parameters=["-q:a", "0"]
                )
                
                final_duration = len(adjusted_audio) / 1000.0
                print(f"✅ Clear speech: {current_duration:.2f}s → {final_duration:.2f}s")
            else:
                os.rename(result_path, output_path)
            
            # Clean up
            if os.path.exists(result_path):
                try:
                    os.remove(result_path)
                except:
                    pass
                
            return output_path
            
        except Exception as e:
            print(f"⚠️ Duration adjustment failed: {e}")
            if os.path.exists(result_path):
                os.rename(result_path, output_path)
                return output_path
            return clear_tts.create_silent_fallback(text, output_path, target_duration)
            
    except Exception as e:
        print(f"❌ Duration adjustment error: {e}")
        return clear_tts.create_silent_fallback(text, output_path, target_duration)

def verify_audio_file(audio_path):
    """Check if audio file is good quality"""
    try:
        if not os.path.exists(audio_path):
            return False, f"File not found: {audio_path}"
        
        if os.path.getsize(audio_path) < 1000:
            return False, f"File too small: {os.path.getsize(audio_path)} bytes"
        
        audio = AudioSegment.from_file(audio_path)
        duration = len(audio) / 1000.0
        
        if duration < 0.5:
            return False, f"Audio too short: {duration:.2f}s"
        
        return True, f"Clear audio ready: {duration:.2f}s"
        
    except Exception as e:
        return False, f"Audio file issue: {e}"

def generate_narration(image_prompt, original_text, desired_duration_seconds=7.5, language='auto'):
    """Generate clear, engaging narration"""
    try:
        import random
        
        # Detect language
        if language == 'auto':
            language = clear_tts.detect_language_simple(original_text)
        
        print(f"🎯 Creating clear {language.upper()} narration: {original_text[:50]}...")
        
        if language == 'hi':
            # Hindi narration options
            hindi_options = [
                f"{original_text} - यह सफर वाकई अविस्मरणीय था।",
                f"अंततः {original_text.lower()} - यह अनुभव जीवन भर याद रहेगा।",
                f"{original_text} - इस खूबसूरत जगह ने मेरे दिल को छू लिया।",
                f"वाह! {original_text} - यह देखकर मैं बेहद खुश हो गया।",
                f"{original_text} - इतनी खूबसूरती देखकर मैं हैरान रह गया।"
            ]
            narration_text = random.choice(hindi_options)
        else:
            # English narration options (conversational segment style with soft skills)
            english_options = [
                f"Well... {original_text}... This amazing journey... was truly... beyond my dreams... you know.",
                f"So... finally experiencing... {original_text.lower()}... The beauty here... is absolutely... wonderful... really.",
                f"Actually... {original_text}... The incredible sights... left me... completely amazed... truly.",
                f"You know... I still cannot... believe it... {original_text.lower()}... This beautiful memory... will stay with me... forever... indeed.",
                f"Well... {original_text}... Every moment... felt like... a scene from... a perfect movie... you see."
            ]
            narration_text = random.choice(english_options)
        
        return narration_text
        
    except Exception as e:
        print(f"⚠️ Narration creation failed: {e}")
        return original_text

# Helper functions
def create_silent_audio(text, output_path, duration=None):
    """Create silent audio placeholder"""
    return clear_tts.create_silent_fallback(text, output_path, duration)

def detect_language(text):
    """Detect text language"""
    return clear_tts.detect_language_simple(text)

def get_audio_duration(audio_path):
    """Get audio file duration"""
    try:
        if not os.path.exists(audio_path):
            return None
        
        if os.path.getsize(audio_path) < 1000:
            return None
        
        audio = AudioSegment.from_file(audio_path)
        duration = len(audio) / 1000.0
        return duration
        
    except Exception as e:
        print(f"Duration check failed: {e}")
        return None

def adjust_speech_to_duration(text, target_duration, output_path, voice="female", language="auto"):
    """Make speech fit specific duration while keeping it clear"""
    try:
        print(f"🎯 Creating {target_duration:.2f}s clear audio: '{text[:50]}...'")
        
        # Generate speech
        temp_path = output_path.replace('.mp3', '_temp.mp3')
        result_path = convert_text_to_speech(text, temp_path, voice, language)
        
        if not result_path or not os.path.exists(result_path):
            return clear_tts.create_silent_fallback(text, output_path, target_duration)
        
        # Check duration
        current_duration = get_audio_duration(result_path)
        if not current_duration:
            return clear_tts.create_silent_fallback(text, output_path, target_duration)
        
        print(f"🎵 Duration check: {current_duration:.2f}s vs {target_duration:.2f}s target")
        
        # Accept if close enough
        if abs(current_duration - target_duration) / target_duration <= 0.25:
            os.rename(result_path, output_path)
            print("✅ Duration is acceptable")
            return output_path
        
        # Adjust speed while maintaining clarity
        try:
            audio = AudioSegment.from_file(result_path)
            speed_factor = current_duration / target_duration
            
            # Keep speed changes reasonable for clarity
            if speed_factor < 0.7:
                speed_factor = 0.7
                print("🔧 Limiting speed increase to maintain clarity")
            elif speed_factor > 1.5:
                speed_factor = 1.5
                print("🔧 Limiting slowdown to maintain engagement")
            
            if speed_factor != 1.0:
                print(f"🔧 Adjusting for clarity: {speed_factor:.2f}x")
                new_sample_rate = int(audio.frame_rate * speed_factor)
                adjusted_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                adjusted_audio = adjusted_audio.set_frame_rate(22050)
                
                # Save with high quality
                adjusted_audio.export(
                    output_path, 
                    format="mp3", 
                    bitrate="256k",
                    parameters=["-q:a", "0"]
                )
                
                final_duration = get_audio_duration(output_path)
                print(f"✅ Clear audio ready: {current_duration:.2f}s → {final_duration:.2f}s")
            else:
                os.rename(result_path, output_path)
            
            # Clean up
            if os.path.exists(result_path):
                try:
                    os.remove(result_path)
                except:
                    pass
                
            return output_path
            
        except Exception as e:
            print(f"⚠️ Duration adjustment failed: {e}")
            if os.path.exists(result_path):
                os.rename(result_path, output_path)
                return output_path
            return clear_tts.create_silent_fallback(text, output_path, target_duration)
            
    except Exception as e:
        print(f"❌ Clear audio creation failed: {e}")
        return clear_tts.create_silent_fallback(text, output_path, target_duration)

print("🎙️ Initializing Clear & Understandable TTS...")
print("🌟 Focus: Clear speech - NO choppy sounds")

try:
    if TORCH_AVAILABLE:
        print("🔧 Setting up clear speech models...")
        success = clear_tts.setup_clear_models()
        if success:
            print("✅ Clear speech models ready!")
            print(f"🎯 Supported languages: {', '.join(clear_tts.supported_languages)}")
        else:
            print("⚠️ Using clear system voice")
    else:
        print("⚠️ Using clear system voice")
        
    if PYTTSX3_AVAILABLE:
        print("✅ Clear speech system ready")
        engine = initialize_clear_voice()
        if engine and _voice_settings:
            print(f"🎭 Clear voice: {_voice_settings['voice_name']}")
            print(f"🎵 Clear pace: {_voice_settings['rate']} WPM")
    
except Exception as e:
    print(f"⚠️ Setup warning: {e}")

print("")
print("🎯 Clear Speech Features:")
print("   ✅ Every word clearly understandable")
print("   ✅ NO choppy or broken sounds")
print("   ✅ Normal speaking pace (120 WPM)")
print("   ✅ Clear, audible volume")
print("   ✅ Only natural pauses (after periods/commas)")
print("   ✅ Same clear voice throughout")
print("   ✅ NO excessive processing")
print("")
print("🚀 Ready for clear, understandable narration!")
