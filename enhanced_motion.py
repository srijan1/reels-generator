"""
Enhanced motion effects with improved audio synchronization and caption integration.
"""

import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from tqdm import tqdm
import math
from enhanced_captions import add_improved_text_overlay, create_subtitle_frame

def format_timecode(seconds):
    """Format seconds into MM:SS timecode format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def create_motion_frames(image_path, output_dir, duration, zoom_direction, text="", text_overlay=False, 
                         text_style="modern", emoji=None, audio_duration=None, subtitle_mode=False):
    """
    Create frames with dynamic motion effects for a segment with audio synchronization
    
    Parameters:
    - image_path: Path to input image
    - output_dir: Directory to save frames
    - duration: Visual duration in seconds
    - zoom_direction: Type of camera motion
    - text: Text overlay content
    - text_overlay: Whether to show text overlay
    - text_style: Style of text overlay
    - emoji: Optional emoji to include
    - audio_duration: Duration of accompanying audio (for sync)
    - subtitle_mode: Whether to use subtitles instead of text overlay
    """
    # Load base image
    try:
        base_img = Image.open(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        # Create a blank image as fallback
        base_img = Image.new('RGB', (576, 1024), color=(0, 0, 0))
    
    base_array = np.array(base_img)
    h, w = base_array.shape[:2]

    # Frame rate - using 30fps for smooth motion
    fps = 30
    
    # Use audio duration if provided, otherwise use the specified duration
    if audio_duration is not None:
        # Sync frames to audio
        actual_duration = audio_duration
        print(f"Syncing {duration}s of visuals to {audio_duration}s of audio")
    else:
        actual_duration = duration
    
    num_frames = int(actual_duration * fps)
    
    # Pre-calculate motion parameters to ensure smooth movement
    motion_params = []
    
    # Generate smooth motion curve parameters
    for j in range(num_frames):
        progress = j / (num_frames - 1) if num_frames > 1 else 0  # 0 to 1
        
        # Apply easing functions for smoother motion
        if zoom_direction in ["in", "forward_push", "gentle_zoom_out"]:
            # Use cubic easing for zoom
            eased_progress = progress * progress * (3 - 2 * progress)
        elif zoom_direction in ["slow_pan", "looking_up"]:
            # Use sine wave for panning motions
            eased_progress = 0.5 * (1 - np.cos(progress * np.pi))
        elif zoom_direction == "gentle_pulse":
            # Keep progress as is for pulse effect
            eased_progress = progress
        else:
            # Linear for other motions
            eased_progress = progress

        # Initialize transformation matrix
        M = np.float32([[1, 0, 0], [0, 1, 0]])

        if zoom_direction == "in":
            # Standard zoom in - VERY SUBTLE
            zoom_factor = 1.0 + (0.05 * eased_progress)  # Reduced from 0.15
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "forward_push":
            # Forward motion effect with subtle acceleration - REDUCED
            zoom_factor = 1.0 + (0.04 * eased_progress)  # Reduced from 0.12
            offset_y = int(h * 0.02 * eased_progress)  # Reduced from 0.05
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2 - offset_y]
            ])
        elif zoom_direction == "slow_pan":
            # Horizontal pan with smoother motion - VERY SUBTLE
            offset_x = int(w * 0.03 * np.sin(eased_progress * np.pi))  # Reduced from 0.08
            M = np.float32([
                [1, 0, offset_x],
                [0, 1, 0]
            ])
        elif zoom_direction == "gentle_zoom_out":
            # Zoom out with easing - REDUCED
            zoom_factor = 1.05 - (0.05 * eased_progress)  # Reduced from 1.15-0.15
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "looking_up":
            # Tilt up effect with subtle acceleration - REDUCED
            offset_y = int(h * 0.03 * eased_progress)  # Reduced from 0.08
            zoom_factor = 1.0 + (0.02 * eased_progress)  # Reduced from 0.05
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2 + offset_y]
            ])
        elif zoom_direction == "focus_in":
            # Focus effect with slight zoom - REDUCED
            zoom_factor = 1.0 + (0.03 * np.sin(eased_progress * np.pi))  # Reduced from 0.08
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "drift":
            # Slow drift across the image (diagonal) - VERY SUBTLE
            max_drift = min(w, h) * 0.02  # Reduced from 0.06
            drift_x = int(max_drift * np.sin(eased_progress * np.pi * 0.5))
            drift_y = int(max_drift * np.sin(eased_progress * np.pi * 0.7))
            M = np.float32([
                [1, 0, drift_x],
                [0, 1, drift_y]
            ])
        elif zoom_direction == "gentle_pulse":
            # Subtle breathing/pulsing effect - VERY REDUCED
            pulse = 0.008 * np.sin(eased_progress * np.pi * 2)  # Reduced from 0.02
            zoom_factor = 1.0 + pulse
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        
        motion_params.append({
            'matrix': M,
            'progress': progress,
            'eased_progress': eased_progress
        })

    # Generate frames with the pre-calculated motion
    for j, params in enumerate(tqdm(motion_params, desc="Creating motion frames")):
        progress = params['progress']
        M = params['matrix']
        
        # Apply transformation to create the motion effect on the base image
        frame = cv2.warpAffine(base_array, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
        # Create frame as PIL Image
        frame_pil = Image.fromarray(frame)
        
        # Calculate the frame's position in audio timeline (for subtitle timing)
        frame_time_seconds = (j / fps)
        frame_timecode = format_timecode(frame_time_seconds)
        
        # Add text overlay AFTER motion effects have been applied
        # This ensures captions remain in fixed position regardless of image motion
        if text_overlay and text:
            if subtitle_mode:
                # Use professional subtitle style with FIXED captions
                # Apply caption AFTER motion effects to keep it in fixed position
                frame_pil = create_subtitle_frame(
                    frame_pil,
                    text,
                    timecode=frame_timecode,
                    progress=1.0,  # Always fully visible
                    word_progress=None  # No word highlighting
                )
            else:
                # Use Instagram-style text overlay
                frame_pil = add_improved_text_overlay(
                    frame_pil,
                    text,
                    style=text_style,
                    progress=1.0,  # Always fully visible
                    emoji=emoji
                )
        
        # Add very subtle lighting/color variation (significantly reduced)
        # This is now almost imperceptible for a more professional look
        brightness = ImageEnhance.Brightness(frame_pil)
        frame_pil = brightness.enhance(1 + np.sin(progress * np.pi) * 0.005)  # Reduced from 0.02
        
        # Save frame
        frame_path = f"{output_dir}/frame_{j:04d}.png"
        frame_pil.save(frame_path)
    
    print(f"Generated {num_frames} frames with {zoom_direction} motion effect")
    return num_frames

def add_camera_shake(frame, intensity=0.5):
    """
    Add extremely subtle camera shake effect for professional results
    
    Parameters:
    - frame: PIL Image
    - intensity: Shake intensity (0-1)
    
    Returns: PIL Image with shake effect
    
    Note: This should be applied BEFORE adding captions to ensure
    captions remain fixed in position.
    """
    # Convert to numpy for transformations
    frame_array = np.array(frame)
    h, w = frame_array.shape[:2]
    
    # Calculate random offsets with extremely controlled magnitude
    # This is now 5 times more subtle than before
    max_offset = max(0, int(min(w, h) * 0.001 * intensity))  # Very subtle for professional look
    
    # If max_offset is 0, return the frame unchanged
    if max_offset <= 0:
        return frame
    
    # Use a smoother oscillation pattern instead of pure random
    # This creates more of a gentle drift than a shake
    progress = np.random.random()  # Random position in the oscillation
    x_offset = int(max_offset * np.sin(progress * np.pi * 2))
    y_offset = int(max_offset * np.cos(progress * np.pi * 2))
    
    # Create transformation matrix
    M = np.float32([
        [1, 0, x_offset],
        [0, 1, y_offset]
    ])
    
    # Apply the transformation
    shifted = cv2.warpAffine(frame_array, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    
    return Image.fromarray(shifted)

def add_film_grain(frame, amount=5):
    """
    Add subtle film grain for cinematic effect
    
    Parameters:
    - frame: PIL Image
    - amount: Grain intensity (1-20)
    
    Returns: PIL Image with film grain
    """
    # Convert to numpy for pixel manipulation
    img_array = np.array(frame).astype(np.float32)
    h, w = img_array.shape[:2]
    
    # Generate noise - but make it much more subtle
    actual_amount = min(3, amount)  # Cap at 3 for subtlety
    noise = np.random.normal(0, actual_amount, (h, w, 3))
    
    # Make noise more professional by reducing it in shadows and highlights
    # This mimics how real film grain behaves
    luminance = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
    shadows_mask = luminance < 30
    highlights_mask = luminance > 220
    
    # Reduce noise in shadows and highlights
    noise[shadows_mask] *= 0.4
    noise[highlights_mask] *= 0.4
    
    # Add noise to image
    img_array += noise
    img_array = np.clip(img_array, 0, 255)
    
    return Image.fromarray(np.uint8(img_array))

def create_enhanced_motion_frames(image_path, output_dir, duration, narration_text, audio_duration=None, 
                                 style="professional", motion_type="gentle_pan", subtitle=True):
    """
    Create professional-quality frames with motion and synchronized captions
    
    Parameters:
    - image_path: Path to input image
    - output_dir: Directory to save frames
    - duration: Visual duration in seconds
    - narration_text: Text for narration/caption
    - audio_duration: Duration of narration audio (for sync)
    - style: Visual style ("professional", "dramatic", "cinematic")
    - motion_type: Camera motion type
    - subtitle: Whether to use subtitle-style captions
    
    Note: Captions are applied AFTER motion effects to ensure they remain in a fixed,
    consistent position throughout the video, regardless of image motion effects.
    """
    # Apply professional presets based on style
    if style == "dramatic":
        text_style = "dramatic"
        zoom_direction = motion_type if motion_type else "forward_push"
        film_grain = 5  # Reduced from 10
        camera_shake = 0.1  # Significantly reduced from 0.3
    elif style == "cinematic":
        text_style = "modern"
        zoom_direction = motion_type if motion_type else "slow_pan"
        film_grain = 3  # Reduced from 7
        camera_shake = 0.05  # Significantly reduced from 0.2
    else:  # professional is default
        text_style = "modern"
        zoom_direction = motion_type if motion_type else "gentle_pulse"
        film_grain = 2  # Reduced from 3
        camera_shake = 0.03  # Significantly reduced from 0.1
    
    # Use audio duration for perfect sync if available
    actual_duration = audio_duration if audio_duration is not None else duration
    
    # Generate basic motion frames
    create_motion_frames(
        image_path,
        output_dir,
        duration,
        zoom_direction,
        text=narration_text,
        text_overlay=True,
        text_style=text_style,
        audio_duration=actual_duration,
        subtitle_mode=subtitle
    )
    
    # Apply additional effects to each frame if desired
    if film_grain > 0 or camera_shake > 0:
        print("Applying finishing touches...")
        frame_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
        
        for frame_file in tqdm(frame_files, desc="Adding cinematic effects"):
            frame_path = os.path.join(output_dir, frame_file)
            frame = Image.open(frame_path)
            
            # Extract caption first (if any)
            # This lets us apply effects to the image but keep caption untouched
            has_caption = False
            caption_area = None
            
            # Extract the bottom area where caption would be (approx. bottom 15% of image)
            h = frame.height
            caption_y = int(h * 0.85)
            if caption_y < h:
                caption_area = frame.crop((0, caption_y, frame.width, h))
                has_caption = True
            
            # Apply film grain to the image (but not to caption area)
            if film_grain > 0:
                frame = add_film_grain(frame, amount=film_grain)
            
            # Apply camera shake (but not to caption area)
            if camera_shake > 0:
                frame = add_camera_shake(frame, intensity=camera_shake)
            
            # Restore caption area if we extracted it
            if has_caption and caption_area:
                frame.paste(caption_area, (0, caption_y))
            
            # Save enhanced frame
            frame.save(frame_path)
    
    # Count frames to verify
    frame_count = len([f for f in os.listdir(output_dir) if f.endswith('.png')])
    return frame_count
                                     
