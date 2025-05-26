"""
Professional transition types for use in the video generator.
Import these functions into the transitions.py file.
"""

import numpy as np
from PIL import Image
import cv2

def professional_crossfade(img1, img2, progress):
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

def professional_fade_black(img1, img2, progress):
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

def professional_dissolve(img1, img2, progress):
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

def professional_smooth_slide(img1, img2, progress, direction="right"):
    """
    Create a smooth slide transition that feels professional
    
    Parameters:
    - img1: First image (from)
    - img2: Second image (to)
    - progress: Transition progress (0-1)
    - direction: Slide direction ("right", "left", "up", "down")
    
    Returns: PIL Image with smooth slide effect
    """
    width, height = img1.size
    result = Image.new("RGB", (width, height))
    
    # Apply easing function for smoother movement
    eased_progress = progress * progress * (3 - 2 * progress)
    
    if direction == "left":
        # Slide from right to left (smoother motion)
        offset = int(width * (1 - eased_progress))
        result.paste(img1, (-width + offset, 0))
        result.paste(img2, (offset, 0))
    elif direction == "right":
        # Slide from left to right (smoother motion)
        offset = int(width * eased_progress)
        result.paste(img1, (offset, 0))
        result.paste(img2, (offset - width, 0))
    elif direction == "up":
        # Slide from bottom to top (smoother motion)
        offset = int(height * (1 - eased_progress))
        result.paste(img1, (0, -height + offset))
        result.paste(img2, (0, offset))
    elif direction == "down":
        # Slide from top to bottom (smoother motion)
        offset = int(height * eased_progress)
        result.paste(img1, (0, offset))
        result.paste(img2, (0, offset - height))
    
    return result