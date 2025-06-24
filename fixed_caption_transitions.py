"""
Enhanced functions for transitions with fixed caption positioning.
"""

import os
import numpy as np
import cv2
from PIL import Image
import shutil
from enhanced_captions import create_subtitle_frame

def preserve_caption_area(img1, img2):
    """
    Extract caption areas from two images to ensure they remain fixed during transitions
    
    Parameters:
    - img1: First PIL Image
    - img2: Second PIL Image
    
    Returns: tuple (img1_without_caption, img2_without_caption, caption_area)
    """
    width, height = img1.size
    
    # Standard caption area position (approx. bottom 15% of image)
    caption_y = int(height * 0.85)
    caption_height = height - caption_y
    
    # Check if images have the same dimensions
    if img1.size != img2.size:
        # Resize if needed
        img2 = img2.resize(img1.size, Image.BICUBIC)
    
    # Create copies to avoid modifying originals
    img1_copy = img1.copy()
    img2_copy = img2.copy()
    
    # Extract caption area from the second image (which has the caption that will be visible)
    caption_area = img2.crop((0, caption_y, width, height))
    
    # Create versions of both images with a blank caption area
    blank_caption = Image.new('RGB', (width, caption_height), (0, 0, 0))
    
    img1_copy.paste(blank_caption, (0, caption_y))
    img2_copy.paste(blank_caption, (0, caption_y))
    
    return img1_copy, img2_copy, caption_area

def create_professional_crossfade(img1, img2, progress):
    """
    Create a highly professional crossfade transition
    
    Parameters:
    - img1: First image (from)
    - img2: Second image (to)
    - progress: Transition progress (0-1)
    
    Returns: PIL Image with smooth crossfade
    """
    # Apply a subtle ease curve to make it feel more natural
    # This creates a slightly faster middle transition and gentler start/end
    eased_progress = progress * progress * (3 - 2 * progress)
    
    # Create the crossfade
    return Image.blend(img1, img2, eased_progress)

def create_professional_fade_through_black(img1, img2, progress):
    """
    Create a professional fade-through-black transition
    
    Parameters:
    - img1: First image (from)
    - img2: Second image (to)
    - progress: Transition progress (0-1)
    
    Returns: PIL Image with fade through black
    """
    black_img = Image.new("RGB", img1.size, (0, 0, 0))
    
    if progress < 0.5:
        # Fade to black with easing
        fade_progress = progress * 2  # 0->1 during first half
        # Apply easing for smoother feel
        fade_progress = fade_progress * fade_progress * (3 - 2 * fade_progress)
        return Image.blend(img1, black_img, fade_progress)
    else:
        # Fade from black with easing
        fade_progress = (progress - 0.5) * 2  # 0->1 during second half
        # Apply easing for smoother feel
        fade_progress = fade_progress * fade_progress * (3 - 2 * fade_progress)
        return Image.blend(black_img, img2, fade_progress)

def create_professional_dissolve(img1, img2, progress):
    """
    Create a professional dissolve transition with subtle randomized pixels
    
    Parameters:
    - img1: First image (from)
    - img2: Second image (to)
    - progress: Transition progress (0-1)
    
    Returns: PIL Image with dissolve effect
    """
    # Start with a cross-fade base
    result = Image.blend(img1, img2, progress)
    
    # Add a subtle dissolve effect
    if 0.2 < progress < 0.8:
        # Only add dissolve during middle portion of transition
        dissolve_intensity = min(0.1, max(0.0, 
                                 0.1 * (1 - abs(progress - 0.5) * 4)))
        
        # Convert to numpy for pixel manipulation
        result_array = np.array(result).astype(np.float32)
        
        # Create a random mask of pixels
        h, w = result_array.shape[:2]
        random_mask = np.random.random((h, w)) < dissolve_intensity
        
        # For those pixels, use either image1 or image2
        img1_array = np.array(img1).astype(np.float32)
        img2_array = np.array(img2).astype(np.float32)
        
        # Split mask randomly between the two images
        use_img1 = np.random.random((h, w)) < 0.5
        img1_mask = random_mask & use_img1
        img2_mask = random_mask & ~use_img1
        
        # Apply masks
        for i in range(3):  # RGB channels
            result_array[:,:,i][img1_mask] = img1_array[:,:,i][img1_mask]
            result_array[:,:,i][img2_mask] = img2_array[:,:,i][img2_mask]
        
        result = Image.fromarray(np.uint8(result_array))
    
    return result

# Now create wrapper functions for each transition type
def create_slide_transition_fixed_captions(img1, img2, progress, direction="left"):
    """Create slide transition effect with fixed captions"""
    from transitions import create_slide_transition
    return create_transition_with_fixed_captions(create_slide_transition, img1, img2, progress, direction)

def create_color_pulse_transition_fixed_captions(img1, img2, progress):
    """Create color pulse transition with fixed captions"""
    # This is a custom implementation since we need to handle the white flash specially
    width, height = img1.size
    caption_y = int(height * 0.85)
    caption_area = img2.crop((0, caption_y, width, height))
    
    # Create the basic transition
    if progress < 0.4:
        # Fade to white
        white_img = Image.new("RGB", img1.size, (255, 255, 255))
        transition_frame = Image.blend(img1, white_img, progress * 2.5)
    else:
        # Fade from white
        white_img = Image.new("RGB", img2.size, (255, 255, 255))
        transition_frame = Image.blend(white_img, img2, (progress - 0.4) * 1.67)
    
    # Restore caption
    result = transition_frame.copy()
    result.paste(caption_area, (0, caption_y))
    
    return result

def apply_fixed_caption_to_frame(frame, caption_text, timecode=None):
    """Apply a fixed caption to a transition frame"""
    return create_subtitle_frame(
        frame,
        caption_text,
        timecode=timecode,
        progress=1.0  # Always fully visible
    )

# This function can be imported and used in the transitions.py file
def preserve_captions_during_transitions(base_dir, transition_dir, segment_num, caption_text=None):
    """
    Post-process transition frames to ensure captions remain fixed
    
    Parameters:
    - base_dir: Base directory
    - transition_dir: Transition frames directory
    - segment_num: Segment number (for to_segment)
    - caption_text: Optional text for caption
    """
    frames = sorted([f for f in os.listdir(transition_dir) if f.endswith('.png')])
    
    if not frames:
        return
    
    # Get caption from the destination segment's first frame if not provided
    if caption_text is None:
        next_segment_dir = f"{base_dir}/3_frames/segment_{segment_num}"
        next_frames = sorted([f for f in os.listdir(next_segment_dir) if f.endswith('.png')])
        
        if next_frames:
            # Load the first frame of the next segment which should have the caption
            next_frame_path = os.path.join(next_segment_dir, next_frames[0])
            next_frame = Image.open(next_frame_path)
            
            # Extract caption area
            width, height = next_frame.size
            caption_y = int(height * 0.85)
            caption_area = next_frame.crop((0, caption_y, width, height))
            
            # Apply caption to all transition frames
            for frame_file in frames:
                frame_path = os.path.join(transition_dir, frame_file)
                frame = Image.open(frame_path)
                
                # Paste the caption
                frame.paste(caption_area, (0, caption_y))
                frame.save(frame_path)
    else:
        # Apply text caption to all frames
        for frame_file in frames:
            frame_path = os.path.join(transition_dir, frame_file)
            frame = Image.open(frame_path)
            
            # Apply caption
            frame_with_caption = create_subtitle_frame(
                frame,
                caption_text,
                progress=1.0  # Always fully visible
            )
            
            frame_with_caption.save(frame_path)
