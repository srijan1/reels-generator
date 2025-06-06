"""
Functions for creating transitions between segments in the Instagram Reels video.
"""

import os
import numpy as np
import cv2
from PIL import Image
import shutil

def create_slide_transition(img1, img2, progress, direction="left"):
    """Create slide transition effect"""
    width, height = img1.size
    result = Image.new("RGB", (width, height))

    if direction == "left":
        # Slide from right to left
        offset = int(width * (1 - progress))
        result.paste(img1, (-width + offset, 0))
        result.paste(img2, (offset, 0))
    elif direction == "right":
        # Slide from left to right
        offset = int(width * progress)
        result.paste(img1, (offset, 0))
        result.paste(img2, (offset - width, 0))
    elif direction == "up":
        # Slide from bottom to top
        offset = int(height * (1 - progress))
        result.paste(img1, (0, -height + offset))
        result.paste(img2, (0, offset))
    elif direction == "down":
        # Slide from top to bottom
        offset = int(height * progress)
        result.paste(img1, (0, offset))
        result.paste(img2, (0, offset - height))

    return result

def create_rain_wipe_transition(img1, img2, progress, raindrops=30):
    """Create rain drop transition effect"""
    width, height = img1.size
    result = Image.new("RGB", (width, height))

    # Start by copying the first image
    result.paste(img1)
    result_array = np.array(result)

    # Define raindrop parameters
    max_radius = int(height * 0.2)  # Maximum raindrop size

    if progress < 0.1:
        # Just start with img1
        return result
    elif progress > 0.9:
        # End with img2
        return img2

    # Calculate adjusted progress
    adj_progress = (progress - 0.1) / 0.8

    # Create raindrop mask
    mask = np.zeros((height, width), dtype=np.float32)

    # Generate random raindrop positions (but keep them consistent)
    np.random.seed(42)  # Fixed seed for consistent positions
    drop_positions = []

    for _ in range(raindrops):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        start_time = np.random.rand() * 0.7  # When this drop starts (0-0.7)
        drop_positions.append((x, y, start_time))

    # Draw each raindrop
    img2_array = np.array(img2)

    for x, y, start_time in drop_positions:
        if adj_progress < start_time:
            continue

        # Calculate drop radius based on progress
        drop_progress = min(1.0, (adj_progress - start_time) / 0.3)
        radius = int(max_radius * drop_progress)

        if radius <= 0:
            continue

        # Create circular mask for this drop
        y_indices, x_indices = np.ogrid[:height, :width]
        dist_from_center = np.sqrt((x_indices - x)**2 + (y_indices - y)**2)
        circle_mask = dist_from_center <= radius

        # Use the second image for this area
        result_array[circle_mask] = img2_array[circle_mask]

    # For later in the transition, start general crossfade
    if adj_progress > 0.6:
        fade_factor = (adj_progress - 0.6) / 0.4  # 0 to 1 in the last 40% of transition
        result_array = cv2.addWeighted(result_array, 1 - fade_factor, img2_array, fade_factor, 0)

    return Image.fromarray(result_array)

def create_whip_pan_transition(img1, img2, progress, direction="horizontal"):
    """Create a motion blur whip pan transition"""
    width, height = img1.size
    result = Image.new("RGB", (width, height))

    if progress < 0.2:
        # Starting image with increasing motion blur
        blur_amount = int(30 * (progress / 0.2))
        if blur_amount > 0:
            if direction == "horizontal":
                kernel = np.zeros((3, blur_amount))
                kernel[1, :] = 1.0 / blur_amount
            else:  # vertical
                kernel = np.zeros((blur_amount, 3))
                kernel[:, 1] = 1.0 / blur_amount

            img1_array = np.array(img1)
            blurred = cv2.filter2D(img1_array, -1, kernel)
            result = Image.fromarray(blurred)
        else:
            result = img1

    elif progress < 0.5:
        # Peak motion blur - full white or line streaks
        streak_progress = (progress - 0.2) / 0.3  # 0 to 1 during this phase

        # Create extreme motion streak
        img1_array = np.array(img1)
        img2_array = np.array(img2)

        # Create strong directional blur
        blur_amount = 100
        if direction == "horizontal":
            kernel = np.zeros((5, blur_amount))
            kernel[2, :] = 1.0 / blur_amount
        else:  # vertical
            kernel = np.zeros((blur_amount, 5))
            kernel[:, 2] = 1.0 / blur_amount

        # Apply to both images and blend
        blur1 = cv2.filter2D(img1_array, -1, kernel)
        blur2 = cv2.filter2D(img2_array, -1, kernel)

        # Blend with white at the peak
        white = np.ones_like(img1_array) * 255
        blend_with_white = min(1.0, streak_progress * 2) if streak_progress < 0.5 else min(1.0, (1 - streak_progress) * 2)

        # First blend each blurred image with white
        blend1 = cv2.addWeighted(blur1, 1 - blend_with_white, white, blend_with_white, 0)
        blend2 = cv2.addWeighted(blur2, 1 - blend_with_white, white, blend_with_white, 0)

        # Then blend between the two blurred images
        blend_factor = max(0, min(1, (streak_progress - 0.3) * 5))
        final_blend = cv2.addWeighted(blend1, 1 - blend_factor, blend2, blend_factor, 0)

        result = Image.fromarray(final_blend.astype(np.uint8))

    elif progress <= 1.0:
        # Ending image with decreasing motion blur
        blur_amount = int(30 * (1 - (progress - 0.5) / 0.5))
        if blur_amount > 0:
            if direction == "horizontal":
                kernel = np.zeros((3, blur_amount))
                kernel[1, :] = 1.0 / blur_amount
            else:  # vertical
                kernel = np.zeros((blur_amount, 3))
                kernel[:, 1] = 1.0 / blur_amount

            img2_array = np.array(img2)
            blurred = cv2.filter2D(img2_array, -1, kernel)
            result = Image.fromarray(blurred)
        else:
            result = img2

    return result

def create_gradient_wipe_transition(img1, img2, progress, direction="left-to-right"):
    """Create a smooth gradient wipe transition"""
    width, height = img1.size

    # Create gradient mask
    mask = np.zeros((height, width), dtype=np.float32)

    if direction == "left-to-right":
        # Create horizontal gradient
        for x in range(width):
            mask[:, x] = x / width

    elif direction == "right-to-left":
        # Create horizontal gradient (reversed)
        for x in range(width):
            mask[:, x] = 1 - (x / width)

    elif direction == "top-to-bottom":
        # Create vertical gradient
        for y in range(height):
            mask[y, :] = y / height

    elif direction == "bottom-to-top":
        # Create vertical gradient (reversed)
        for y in range(height):
            mask[y, :] = 1 - (y / height)

    elif direction == "radial":
        # Create radial gradient from center
        center_x, center_y = width // 2, height // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)

        for y in range(height):
            for x in range(width):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                mask[y, x] = dist / max_dist

    # Adjust mask based on progress
    # Make gradient steeper for a sharper edge
    gradient_width = 0.3  # Width of the gradient as a fraction of the image
    adjusted_mask = (mask - (progress - gradient_width/2)) / gradient_width
    adjusted_mask = np.clip(adjusted_mask, 0, 1)

    # Apply mask
    img1_array = np.array(img1)
    img2_array = np.array(img2)

    # Expand mask to 3 channels
    mask_3channel = np.stack([adjusted_mask] * 3, axis=2)

    # Blend images using the mask
    blended = img1_array * (1 - mask_3channel) + img2_array * mask_3channel

    return Image.fromarray(np.uint8(blended))

def create_transition_frames(base_dir, from_segment, to_segment, transition_type, segment_duration, width, height):
    """Create transition frames between two segments"""
    
    transition_dir = f"{base_dir}/4_transitions/transition_{from_segment}_to_{to_segment}"
    os.makedirs(transition_dir, exist_ok=True)

    # Calculate last frame number based on segment duration
    last_frame_num = int(segment_duration * 30) - 1
    
    # Get last frame of current segment and first frame of next segment
    last_frame_path = f"{base_dir}/3_frames/segment_{from_segment}/frame_{last_frame_num:04d}.png"
    first_frame_path = f"{base_dir}/3_frames/segment_{to_segment}/frame_0000.png"
    
    # Check if the frame files exist
    if not os.path.exists(last_frame_path):
        print(f"Warning: Last frame not found at {last_frame_path}")
        # Find the last available frame in the directory
        segment_dir = f"{base_dir}/3_frames/segment_{from_segment}"
        available_frames = sorted([f for f in os.listdir(segment_dir) if f.endswith('.png')])
        if available_frames:
            last_frame_path = os.path.join(segment_dir, available_frames[-1])
            print(f"Using alternative last frame: {last_frame_path}")
        else:
            # Create a black frame if no frames exist
            print(f"No frames found in {segment_dir}, creating blank frame")
            last_frame = Image.new('RGB', (width, height), color=(0, 0, 0))
            
    if not os.path.exists(first_frame_path):
        print(f"Warning: First frame not found at {first_frame_path}")
        # Find the first available frame in the directory
        segment_dir = f"{base_dir}/3_frames/segment_{to_segment}"
        available_frames = sorted([f for f in os.listdir(segment_dir) if f.endswith('.png')])
        if available_frames:
            first_frame_path = os.path.join(segment_dir, available_frames[0])
            print(f"Using alternative first frame: {first_frame_path}")
        else:
            # Create a black frame if no frames exist
            print(f"No frames found in {segment_dir}, creating blank frame")
            first_frame = Image.new('RGB', (width, height), color=(0, 0, 0))
    
    # Load the frames
    if 'last_frame' not in locals():  # Only load if not already created as a blank frame
        last_frame = Image.open(last_frame_path)
    if 'first_frame' not in locals():  # Only load if not already created as a blank frame
        first_frame = Image.open(first_frame_path)

    # Number of transition frames
    transition_frames = 15  # 0.5 second at 30fps - longer for more dramatic transitions

    print(f"Creating {transition_type} transition from segment {from_segment} to {to_segment}...")

    # Generate transition frames based on type
    for j in range(transition_frames):
        progress = j / (transition_frames - 1)  # 0 to 1

        if transition_type == "smooth_fade":
            # Simple crossfade
            transition_frame = Image.blend(last_frame, first_frame, progress)

        elif transition_type == "slide_up":
            # Slide from bottom to top
            transition_frame = create_slide_transition(last_frame, first_frame, progress, direction="up")

        elif transition_type == "slide_left":
            # Slide from right to left
            transition_frame = create_slide_transition(last_frame, first_frame, progress, direction="left")

        elif transition_type == "color_pulse":
            # Fade through white
            if progress < 0.4:
                # Fade to white
                white_img = Image.new("RGB", last_frame.size, (255, 255, 255))
                transition_frame = Image.blend(last_frame, white_img, progress * 2.5)
            else:
                # Fade from white
                white_img = Image.new("RGB", first_frame.size, (255, 255, 255))
                transition_frame = Image.blend(white_img, first_frame, (progress - 0.4) * 1.67)

        elif transition_type == "rain_wipe":
            # Raindrop transition effect
            transition_frame = create_rain_wipe_transition(last_frame, first_frame, progress)

        elif transition_type == "whip_pan":
            # Fast motion blur transition
            transition_frame = create_whip_pan_transition(last_frame, first_frame, progress)

        elif transition_type == "gradient_wipe":
            # Gradient wipe transition
            transition_frame = create_gradient_wipe_transition(last_frame, first_frame, progress, direction="bottom-to-top")

        else:  # "none" or default
            # Simple cut, just progress between frames
            transition_frame = last_frame if progress < 0.5 else first_frame

        # Save transition frame
        transition_path = f"{transition_dir}/frame_{j:04d}.png"
        transition_frame.save(transition_path)

    print(f"Generated {transition_frames} transition frames")
    return transition_frames
    
