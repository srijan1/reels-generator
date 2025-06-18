"""
Enhanced Motion with Hindi Caption Skip - VIBRATION FIXED
This version removes all vibrating effects for professional smooth motion
"""

import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from tqdm import tqdm
import math
from enhanced_captions import add_improved_text_overlay, create_subtitle_frame

def detect_hindi_text(text):
    """Detect if text contains Hindi characters"""
    hindi_chars = set('अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहािीुूृॄेैोौंःँ़ऽ।॥०१२३४५६७८९')
    hindi_count = sum(1 for char in text if char in hindi_chars)
    
    # If more than 15% of characters are Hindi, consider it Hindi text
    if len(text) > 0 and (hindi_count / len(text)) > 0.15:
        return True
    
    return False

def format_timecode(seconds):
    """Format seconds into MM:SS timecode format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def create_smooth_motion_curve(progress, motion_type="gentle_pulse"):
    """
    Create smooth motion curves using easing functions to eliminate vibration
    Returns scale, offset_x, offset_y values
    """
    
    # Smooth easing functions
    def ease_in_out_cubic(t):
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    def ease_in_out_sine(t):
        return -(math.cos(math.pi * t) - 1) / 2
    
    def ease_out_back(t):
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    # Apply easing based on motion type
    if motion_type == "forward_push":
        # Smooth forward zoom with easing
        eased_progress = ease_in_out_cubic(progress)
        scale = 1.0 + (eased_progress * 0.25)  # Reduced from 0.3 to 0.25
        offset_x = -int(576 * eased_progress * 0.12)  # Smoother offset
        offset_y = -int(1024 * eased_progress * 0.12)
        
    elif motion_type == "gentle_pulse":
        # Super smooth pulsing effect - NO sine wave jumps
        pulse_progress = ease_in_out_sine(progress)
        pulse = pulse_progress * 0.06  # Reduced from 0.1 to 0.06
        scale = 1.0 + pulse
        offset_x = -int(576 * pulse * 0.3)  # Smooth offset
        offset_y = -int(1024 * pulse * 0.3)
        
    elif motion_type == "slow_pan":
        # Ultra smooth horizontal pan
        eased_progress = ease_in_out_cubic(progress)
        scale = 1.15  # Slight zoom, fixed value
        offset_x = -int(576 * eased_progress * 0.08)  # Reduced movement
        offset_y = -int(1024 * 0.08)  # Fixed vertical offset
        
    elif motion_type == "ken_burns":
        # Smooth Ken Burns effect
        eased_progress = ease_in_out_cubic(progress)
        scale = 1.0 + (eased_progress * 0.18)  # Reduced from 0.2
        offset_x = -int(576 * eased_progress * 0.08)
        offset_y = -int(1024 * eased_progress * 0.08)
        
    else:  # "static" or default - NO MOTION AT ALL
        scale = 1.0
        offset_x = 0
        offset_y = 0
    
    return scale, offset_x, offset_y

def create_motion_frames(image_path, output_dir, duration, zoom_direction, text="", text_overlay=False, 
                         text_style="modern", emoji=None, audio_duration=None, subtitle_mode=False):
    """
    Create frames with SMOOTH motion effects - NO VIBRATION
    MODIFIED: Automatically skips captions for Hindi text and eliminates all jittery motion
    """
    
    # HINDI DETECTION: Skip captions entirely for Hindi content
    is_hindi = detect_hindi_text(text)
    if is_hindi:
        print(f"🚫 Hindi text detected - SKIPPING captions: '{text[:50]}...'")
        text_overlay = False
        subtitle_mode = False
    else:
        print(f"🔤 English text detected - captions enabled: '{text[:50]}...'")
    
    # Load base image
    try:
        base_img = Image.open(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        base_img = Image.new('RGB', (576, 1024), color=(0, 0, 0))
    
    base_array = np.array(base_img)
    h, w = base_array.shape[:2]

    # Frame rate - using 30fps for smooth motion
    fps = 30
    
    # Use audio duration if provided
    if audio_duration is not None:
        actual_duration = audio_duration
        print(f"Syncing {duration}s of visuals to {audio_duration}s of audio")
    else:
        actual_duration = duration
    
    num_frames = int(actual_duration * fps)
    
    # CRITICAL: Pre-calculate ALL motion parameters to ensure perfectly smooth movement
    print(f"Pre-calculating {num_frames} smooth motion frames...")
    motion_params = []
    
    for j in range(num_frames):
        progress = j / (num_frames - 1) if num_frames > 1 else 0
        scale, offset_x, offset_y = create_smooth_motion_curve(progress, zoom_direction)
        motion_params.append((scale, offset_x, offset_y))
    
    print(f"Generating {num_frames} frames with SMOOTH {zoom_direction} motion...")
    
    # Generate frames with SMOOTH motion effects
    for j in tqdm(range(num_frames), desc="Creating smooth motion frames"):
        scale, offset_x, offset_y = motion_params[j]
        progress = j / (num_frames - 1) if num_frames > 1 else 0
        
        # Apply motion transformation with HIGH QUALITY interpolation
        if scale != 1.0 or offset_x != 0 or offset_y != 0:
            # Calculate new dimensions
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Use LANCZOS4 for highest quality, smoothest scaling
            resized_img = cv2.resize(base_array, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Create frame canvas
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            
            # Calculate crop region with SMOOTH boundaries
            start_x = max(0, offset_x)
            start_y = max(0, offset_y)
            end_x = min(new_w, w + offset_x)
            end_y = min(new_h, h + offset_y)
            
            # Calculate destination region
            dest_start_x = max(0, -offset_x)
            dest_start_y = max(0, -offset_y)
            dest_end_x = dest_start_x + (end_x - start_x)
            dest_end_y = dest_start_y + (end_y - start_y)
            
            # Copy the cropped region with bounds checking
            if end_x > start_x and end_y > start_y:
                frame[dest_start_y:dest_end_y, dest_start_x:dest_end_x] = resized_img[start_y:end_y, start_x:end_x]
        else:
            frame = base_array.copy()
        
        # Convert to PIL Image
        frame_pil = Image.fromarray(frame)
        
        # Calculate frame timing for subtitles
        frame_time_seconds = (j / fps)
        frame_timecode = format_timecode(frame_time_seconds)
        
        # Add text overlay ONLY if not Hindi
        if text_overlay and text:
            if subtitle_mode:
                frame_pil = create_subtitle_frame(
                    frame_pil,
                    text,
                    timecode=frame_timecode,
                    progress=1.0,
                    word_progress=None
                )
            else:
                frame_pil = add_improved_text_overlay(
                    frame_pil,
                    text,
                    style=text_style,
                    progress=1.0,
                    emoji=emoji
                )
        
        # REMOVED: ALL brightness variation - causes flickering
        # REMOVED: ALL random effects that cause vibration
        
        # Save frame with consistent quality
        frame_path = f"{output_dir}/frame_{j:04d}.png"
        frame_pil.save(frame_path, format="PNG", optimize=False)  # No optimization to prevent artifacts
    
    print(f"✅ Generated {num_frames} SMOOTH frames with {zoom_direction} motion")
    if is_hindi:
        print("✅ Hindi content - NO CAPTIONS added")
    else:
        print("✅ English content - captions added")
    
    return num_frames

def create_enhanced_motion_frames(image_path, output_dir, duration, narration_text, audio_duration=None, 
                                 style="professional", motion_type="gentle_pulse", subtitle=True):
    """
    Create professional-quality frames with SMOOTH motion - NO VIBRATION
    MODIFIED: Removes ALL sources of vibration and jitter
    """
    
    # HINDI DETECTION: Override subtitle setting for Hindi
    is_hindi = detect_hindi_text(narration_text)
    if is_hindi:
        print(f"🚫 Hindi detected - disabling ALL captions for: '{narration_text[:50]}...'")
        subtitle = False
        text_overlay = False
    else:
        print(f"🔤 English detected - captions enabled for: '{narration_text[:50]}...'")
        text_overlay = True
    
    # PROFESSIONAL PRESETS - ALL VIBRATION SOURCES REMOVED
    if style == "dramatic":
        text_style = "dramatic"
        zoom_direction = motion_type if motion_type else "forward_push"
        # REMOVED: film_grain and camera_shake
    elif style == "cinematic":
        text_style = "modern"
        zoom_direction = motion_type if motion_type else "slow_pan"
        # REMOVED: film_grain and camera_shake
    else:  # professional is default
        text_style = "modern"
        zoom_direction = motion_type if motion_type else "gentle_pulse"
        # REMOVED: film_grain and camera_shake
    
    # Use audio duration for perfect sync
    actual_duration = audio_duration if audio_duration is not None else duration
    
    # Generate SMOOTH motion frames (with Hindi caption detection built-in)
    frame_count = create_motion_frames(
        image_path,
        output_dir,
        duration,
        zoom_direction,
        text=narration_text,
        text_overlay=text_overlay,
        text_style=text_style,
        audio_duration=actual_duration,
        subtitle_mode=subtitle
    )
    
    # REMOVED: All post-processing effects that cause vibration
    # REMOVED: film_grain application
    # REMOVED: camera_shake application
    # REMOVED: random noise effects
    
    print(f"🎯 VIBRATION-FREE motion complete!")
    
    if is_hindi:
        print(f"✅ {frame_count} SMOOTH frames generated for HINDI content (NO captions)")
    else:
        print(f"✅ {frame_count} SMOOTH frames generated for ENGLISH content (WITH captions)")
    
    return frame_count

# REMOVED: add_camera_shake function - source of vibration
# REMOVED: add_film_grain function - source of random noise

def add_static_enhancement(frame, enhancement_type="subtle_vignette"):
    """
    Add STATIC (non-random) enhancements that don't cause vibration
    These effects are consistent across all frames
    """
    if enhancement_type == "subtle_vignette":
        # Add a very subtle vignette effect (same for all frames)
        img_array = np.array(frame).astype(np.float32)
        h, w = img_array.shape[:2]
        
        # Create consistent vignette mask
        Y, X = np.ogrid[:h, :w]
        center_x, center_y = w // 2, h // 2
        
        # Distance from center
        distance = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
        max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
        
        # Normalize distance
        normalized_distance = distance / max_distance
        
        # Create vignette effect (subtle)
        vignette = 1 - (normalized_distance * 0.1)  # Very subtle 10% darkening at edges
        vignette = np.clip(vignette, 0.9, 1.0)  # Limit the effect
        
        # Apply vignette to all channels
        for i in range(3):
            img_array[:, :, i] *= vignette
        
        img_array = np.clip(img_array, 0, 255)
        return Image.fromarray(np.uint8(img_array))
    
    return frame

# Test function
def test_hindi_detection():
    """Test the Hindi detection function"""
    test_cases = [
        ("Hello world, this is English", False),
        ("नमस्ते दुनिया, यह हिंदी है", True),
        ("Finally I made it to Japan 🇯🇵", False),
        ("अंततः मैं जापान पहुंच गया।", True),
        ("Mixed text with some हिंदी words", True),
        ("Mostly English with one word: नमस्ते", False),
    ]
    
    print("🧪 Testing Hindi detection...")
    for text, expected in test_cases:
        result = detect_hindi_text(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:30]}...' -> Hindi: {result} (expected: {expected})")
    
    return True

def test_smooth_motion():
    """Test smooth motion curve generation"""
    print("🧪 Testing smooth motion curves...")
    
    motion_types = ["gentle_pulse", "forward_push", "slow_pan", "ken_burns", "static"]
    
    for motion_type in motion_types:
        print(f"\n📊 Testing {motion_type}:")
        for i in range(0, 11, 2):  # Test at 0%, 20%, 40%, 60%, 80%, 100%
            progress = i / 10.0
            scale, offset_x, offset_y = create_smooth_motion_curve(progress, motion_type)
            print(f"  Progress {progress:.1f}: scale={scale:.3f}, offset=({offset_x}, {offset_y})")

if __name__ == "__main__":
    # Run tests when script is executed directly
    test_hindi_detection()
    test_smooth_motion()
    print("🎯 Enhanced motion system ready - VIBRATION ELIMINATED! ✨")
