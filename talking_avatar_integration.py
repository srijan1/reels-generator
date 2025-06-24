import os
import time
import subprocess
import shutil
import json
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

try:
    from piper_tts_integration import adjust_speech_to_duration
    from groq_script_generator import generate_story_script
    from enhanced_captions import create_subtitle_frame
    HAS_DEPENDENCIES = True
except ImportError as e:
    print(f"❌ Required dependencies missing: {e}")
    HAS_DEPENDENCIES = False

class EnhancedTalkingAvatarGenerator:
    def __init__(self, avatar_video_path: str):
        self.avatar_video_path = avatar_video_path
        
        if not os.path.exists(avatar_video_path):
            raise FileNotFoundError(f"Avatar video not found: {avatar_video_path}")
        
        self.avatar_duration = self.get_video_duration(avatar_video_path)
        print(f"✅ Avatar loaded: {os.path.basename(avatar_video_path)} ({self.avatar_duration:.2f}s)")
    
    def get_video_duration(self, video_path):
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data['format']['duration'])
            return 10.0
        except:
            return 10.0
    
    def get_audio_duration(self, audio_path):
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data['format']['duration'])
            return None
        except:
            return None
    
    def create_continuous_audio_track(self, segments, base_dir):
        print("🎙️ Creating continuous audio from all segments...")
        
        audio_segments = []
        segment_timings = []
        current_time = 0.0
        
        for i, segment in enumerate(segments):
            segment_text = segment.get("text", "")
            segment_duration = segment.get("duration_seconds", 7.5)
            
            import re
            clean_text = re.sub(r'[^\w\s\.,!?-]', '', segment_text)
            clean_text = ' '.join(clean_text.split())
            
            print(f"🎙️ Segment {i+1}: {clean_text[:50]}... ({segment_duration:.1f}s)")
            
            audio_path = f"{base_dir}/audio/segment_{i+1}.mp3"
            
            try:
                audio_result = adjust_speech_to_duration(clean_text, segment_duration, audio_path)
                
                if audio_result and os.path.exists(audio_result):
                    actual_duration = self.get_audio_duration(audio_result)
                    if actual_duration:
                        segment_timings.append({
                            'start': current_time,
                            'end': current_time + actual_duration,
                            'text': clean_text,
                            'audio': audio_result,
                            'actual_duration': actual_duration
                        })
                        current_time += actual_duration
                        audio_segments.append(audio_result)
                        print(f"✅ Generated: {actual_duration:.2f}s")
                    else:
                        break
                else:
                    break
            except Exception as e:
                print(f"❌ Audio error: {e}")
                break
        
        if not audio_segments:
            return None, []
        
        continuous_audio_path = f"{base_dir}/audio/continuous_audio.mp3"
        
        if len(audio_segments) == 1:
            shutil.copy(audio_segments[0], continuous_audio_path)
        else:
            self.concatenate_audio_segments(audio_segments, continuous_audio_path)
        
        final_duration = self.get_audio_duration(continuous_audio_path)
        print(f"✅ Total audio: {final_duration:.2f}s from {len(segment_timings)} segments")
        
        return continuous_audio_path, segment_timings
    
    def concatenate_audio_segments(self, audio_files, output_path):
        try:
            list_file = output_path.replace('.mp3', '_list.txt')
            
            with open(list_file, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{os.path.abspath(audio_file)}'\n")
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c:a', 'mp3',
                '-b:a', '128k',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True)
            
            if os.path.exists(list_file):
                os.remove(list_file)
        except:
            pass
    
    def create_avatar_loop(self, target_duration, output_path):
        print(f"🔄 Creating {target_duration:.1f}s avatar loop...")
        
        try:
            if target_duration <= self.avatar_duration:
                cmd = [
                    'ffmpeg', '-y',
                    '-i', self.avatar_video_path,
                    '-t', str(target_duration),
                    '-c:v', 'libx264', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '128k',
                    output_path
                ]
            else:
                num_loops = math.ceil(target_duration / self.avatar_duration)
                
                cmd = [
                    'ffmpeg', '-y',
                    '-stream_loop', str(num_loops - 1),
                    '-i', self.avatar_video_path,
                    '-t', str(target_duration),
                    '-c:v', 'libx264', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '128k',
                    output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Avatar loop created: {target_duration:.1f}s")
                return output_path
            else:
                print(f"⚠️ Loop error, trying basic copy...")
                return self.create_basic_copy(target_duration, output_path)
        except:
            return self.create_basic_copy(target_duration, output_path)
    
    def create_basic_copy(self, target_duration, output_path):
        try:
            actual_duration = min(target_duration, self.avatar_duration)
            
            cmd = [
                'ffmpeg', '-y',
                '-i', self.avatar_video_path,
                '-t', str(actual_duration),
                '-c', 'copy',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True)
            return output_path
        except:
            return None
    
    def add_enhanced_captions(self, video_path, segment_timings, output_path):
        print("✨ Adding captions with perfect sync...")
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_count / fps
                
                current_text = ""
                for timing in segment_timings:
                    if timing['start'] <= current_time < timing['end']:
                        current_text = timing['text']
                        break
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                if current_text:
                    try:
                        captioned_image = create_subtitle_frame(pil_image, current_text)
                    except:
                        captioned_image = self.add_simple_caption(pil_image, current_text)
                else:
                    captioned_image = pil_image
                
                captioned_frame = cv2.cvtColor(np.array(captioned_image), cv2.COLOR_RGB2BGR)
                out.write(captioned_frame)
                
                frame_count += 1
                
                if frame_count % fps == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"📝 Progress: {progress:.0f}%")
            
            cap.release()
            out.release()
            
            print("✅ Captions added successfully")
            return output_path
            
        except Exception as e:
            print(f"⚠️ Caption error: {e}")
            shutil.copy(video_path, output_path)
            return output_path
    
    def add_simple_caption(self, pil_image, text):
        try:
            draw = ImageDraw.Draw(pil_image)
            width, height = pil_image.size
            
            font_size = int(height * 0.04)
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                text_width = draw.textlength(test_line, font=font) if hasattr(draw, 'textlength') else len(test_line) * 10
                
                if text_width <= width * 0.8:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            wrapped_text = '\n'.join(lines)
            
            text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = height - text_height - 40
            
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), wrapped_text, fill=(0, 0, 0), font=font)
            
            draw.text((x, y), wrapped_text, fill=(255, 255, 255), font=font)
            
            return pil_image
        except:
            return pil_image
    
    def add_audio_to_video(self, video_path, audio_path, output_path):
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            return output_path if result.returncode == 0 else video_path
        except:
            return video_path
    
    def generate_complete_talking_avatar(self, script_topic, audience="adult", quality="high"):
        print("🎭 COMPLETE TALKING AVATAR GENERATOR")
        print("="*50)
        print(f"📝 Topic: {script_topic}")
        print(f"🎯 Audience: {audience}")
        print(f"🎬 Quality: {quality}")
        print("="*50)
        
        if not HAS_DEPENDENCIES:
            print("❌ Required dependencies not available")
            return None
        
        print("📝 Generating complete script...")
        story_script = generate_story_script(
            story_topic=script_topic,
            audience=audience,
            duration_minutes=1.0,
            num_segments=8
        )
        
        if not story_script or 'segments' not in story_script:
            print("❌ Script generation failed")
            return None
        
        segments = story_script['segments']
        print(f"✅ Script generated: {len(segments)} segments")
        
        timestamp = int(time.time())
        base_dir = f"./talking_avatar_{timestamp}"
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(f"{base_dir}/audio", exist_ok=True)
        os.makedirs(f"{base_dir}/final", exist_ok=True)
        
        print("\n🎙️ Creating audio...")
        continuous_audio, segment_timings = self.create_continuous_audio_track(segments, base_dir)
        
        if not continuous_audio:
            print("❌ Audio creation failed")
            return None
        
        total_duration = segment_timings[-1]['end'] if segment_timings else 60.0
        
        print(f"\n🎭 Creating {total_duration:.1f}s avatar video...")
        temp_avatar = f"{base_dir}/avatar_loop.mp4"
        avatar_video = self.create_avatar_loop(total_duration, temp_avatar)
        
        if not avatar_video:
            print("❌ Avatar video creation failed")
            return None
        
        print("\n✨ Adding captions...")
        temp_captioned = f"{base_dir}/captioned_avatar.mp4"
        captioned_video = self.add_enhanced_captions(avatar_video, segment_timings, temp_captioned)
        
        print("\n🎵 Adding audio...")
        final_video = f"{base_dir}/final/talking_avatar_complete.mp4"
        result = self.add_audio_to_video(captioned_video, continuous_audio, final_video)
        
        for temp_file in [temp_avatar, temp_captioned]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        if result and os.path.exists(result):
            print(f"\n🎉 SUCCESS! Complete talking avatar generated!")
            print("="*50)
            print(f"📹 Final video: {result}")
            print(f"⏱️ Duration: {total_duration:.1f} seconds")
            print(f"📊 Segments: {len(segments)}")
            print("✨ Features:")
            print("   🎭 Complete script from groq_script_generator.py")
            print("   🎙️ Continuous voice throughout")
            print("   ✨ Professional captions")
            print("   📱 Social media ready")
            print("="*50)
            return result
        else:
            print("❌ Final video creation failed")
            return None

def generate_talking_avatar_video_reel():
    try:
        print("\n🎭 TALKING AVATAR VIDEO GENERATOR")
        print("="*40)
        print("Uses complete script from groq_script_generator.py")
        print("="*40)
        
        avatar_video_path = input("Enter path to your avatar video: ").strip().strip('"').strip("'")
        
        if not os.path.exists(avatar_video_path):
            print("❌ Avatar video not found!")
            return
        
        script_topic = input("Enter video topic: ").strip()
        if not script_topic:
            script_topic = "interesting topic"
        
        audience = input("Audience (adult/children/general) [adult]: ").strip().lower()
        if audience not in ['adult', 'children', 'general']:
            audience = 'adult'
        
        quality = input("Quality (high/medium/fast) [high]: ").strip().lower()
        if quality not in ['high', 'medium', 'fast']:
            quality = 'high'
        
        print(f"\n🚀 Starting generation...")
        print(f"📝 Topic: {script_topic}")
        print(f"🎯 Audience: {audience}")
        print(f"🎬 Quality: {quality}")
        
        try:
            avatar_generator = EnhancedTalkingAvatarGenerator(avatar_video_path)
            
            result = avatar_generator.generate_complete_talking_avatar(
                script_topic=script_topic,
                audience=audience,
                quality=quality
            )
            
            if result:
                open_folder = input("\nOpen output folder? (y/n): ").strip().lower()
                if open_folder in ['y', 'yes']:
                    try:
                        import subprocess
                        import platform
                        
                        folder_path = os.path.dirname(result)
                        if platform.system() == "Windows":
                            subprocess.run(['explorer', folder_path])
                        elif platform.system() == "Darwin":
                            subprocess.run(['open', folder_path])
                        else:
                            subprocess.run(['xdg-open', folder_path])
                    except:
                        print(f"📁 Output folder: {os.path.dirname(result)}")
            else:
                print("❌ Generation failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")

TalkingAvatarGenerator = EnhancedTalkingAvatarGenerator

if __name__ == "__main__":
    print("🎭 TALKING AVATAR GENERATOR")
    print("="*30)
    print("✅ Uses complete groq_script_generator.py output")
    print("✅ Professional captions with enhanced_captions.py")
    print("✅ Continuous audio with piper_tts_integration.py")
    print("="*30)
    
    generate_talking_avatar_video_reel()
