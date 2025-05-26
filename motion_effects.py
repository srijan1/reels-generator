"""
Functions for creating motion effects and dynamic frames from static images.
"""

import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from tqdm import tqdm
from image_effects import add_text_overlay

def create_motion_frames(image_path, output_dir, duration, zoom_direction, text="", text_overlay=False, text_style="modern", emoji=None):
    """Create frames with dynamic motion effects for a segment"""
    
    # Load base image
    base_img = Image.open(image_path)
    base_array = np.array(base_img)
    h, w = base_array.shape[:2]

    # Frame rate - using 30fps for smooth motion
    fps = 30
    num_frames = int(duration * fps)

    # Generate frames with the specified motion effect
    for j in tqdm(range(num_frames)):
        progress = j / (num_frames - 1)  # 0 to 1

        # Initialize transformation matrix
        M = np.float32([[1, 0, 0], [0, 1, 0]])

        if zoom_direction == "in":
            # Standard zoom in
            zoom_factor = 1.0 + (0.15 * progress)
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "forward_push":
            # Forward motion effect
            zoom_factor = 1.0 + (0.12 * progress)
            offset_y = int(h * 0.05 * progress)  # Slight upward motion
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2 - offset_y]
            ])
        elif zoom_direction == "slow_pan":
            # Horizontal pan
            offset_x = int(w * 0.1 * np.sin(progress * np.pi))
            M = np.float32([
                [1, 0, offset_x],
                [0, 1, 0]
            ])
        elif zoom_direction == "gentle_zoom_out":
            # Zoom out effect
            zoom_factor = 1.15 - (0.15 * progress)
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "looking_up":
            # Tilt up effect
            offset_y = int(h * 0.08 * progress)
            zoom_factor = 1.0 + (0.05 * progress)
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2 + offset_y]
            ])
        elif zoom_direction == "focus_in":
            # Focus effect with slight zoom
            zoom_factor = 1.0 + (0.1 * np.sin(progress * np.pi))
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "slow_zoom_out":
            # Slow zoom out
            zoom_factor = 1.1 - (0.1 * progress)
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])
        elif zoom_direction == "gentle_pulse":
            # Subtle breathing/pulsing effect
            pulse = 0.03 * np.sin(progress * np.pi * 2)
            zoom_factor = 1.0 + pulse
            M = np.float32([
                [zoom_factor, 0, (1-zoom_factor)*w/2],
                [0, zoom_factor, (1-zoom_factor)*h/2]
            ])

        # Apply transformation
        frame = cv2.warpAffine(base_array, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        # Create frame as PIL Image
        frame_pil = Image.fromarray(frame)

        # Add text overlay if specified
        if text_overlay:
            frame_pil = add_text_overlay(
                frame_pil,
                text,
                style=text_style,
                progress=progress,
                emoji=emoji
            )

        # Add subtle lighting/color variation for dynamic feel
        brightness = ImageEnhance.Brightness(frame_pil)
        frame_pil = brightness.enhance(1 + np.sin(progress * np.pi) * 0.03)

        # Save frame
        frame_path = f"{output_dir}/frame_{j:04d}.png"
        frame_pil.save(frame_path)

    print(f"Generated {num_frames} frames with {zoom_direction} motion effect")
    return num_frames