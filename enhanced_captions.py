"""
Enhanced functions for text overlays and captions that fit well in the video.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import textwrap
import os
import math

def add_improved_text_overlay(image, text, style="modern", progress=0, emoji=None, font_path=None, max_width_chars=26):
    """
    Add Instagram-style text overlay to image with improved text wrapping and styling
    
    Parameters:
    - image: PIL Image object
    - text: Text to overlay
    - style: Text style ("modern", "bold", "left", "right", "dramatic", "call")
    - progress: Animation progress (0-1)
    - emoji: Optional emoji to add
    - font_path: Path to TTF font file (optional)
    - max_width_chars: Maximum characters per line for wrapping
    """
    img_pil = image.copy()
    width, height = img_pil.size

    # Create transparent overlay
    overlay = Image.new('RGBA', img_pil.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Determine appropriate font size based on image dimensions
    base_font_size = int(height * 0.035)  # Proportional to image height
    
    # Try to load font, fall back to default if not available
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, base_font_size)
        else:
            # Try some common system fonts
            for potential_font in ["Arial.ttf", "Helvetica.ttf", "DejaVuSans.ttf", "FreeSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
                try:
                    font = ImageFont.truetype(potential_font, base_font_size)
                    break
                except:
                    continue
            else:
                font = ImageFont.load_default()
                base_font_size = 16  # Reset for default font
    except:
        font = ImageFont.load_default()
        base_font_size = 16  # Reset for default font
    
    # Wrap text to fit width
    wrapped_text = textwrap.fill(text, width=max_width_chars)
    
    # Calculate text size for positioning
    try:
        # For newer PIL versions
        text_box = overlay_draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
    except:
        # Fallback for older PIL versions
        text_width = overlay_draw.textlength(wrapped_text, font=font) if hasattr(overlay_draw, 'textlength') else width * 0.8
        # Estimate height based on line count
        line_count = len(wrapped_text.split('\n'))
        text_height = base_font_size * line_count * 1.2
    
    # Position at bottom with proper padding
    y_pos = int(height * 0.85)  # Fixed position near bottom
    overlay_height = text_height + int(height * 0.08)  # Text height plus padding
    
    # Create semi-transparent background - consistent for all styles
    alpha = 150  # More transparent background
    
    # Draw background with rounded corners
    bg_x1 = max(0, (width - text_width) // 2 - int(width * 0.03))
    bg_y1 = y_pos
    bg_x2 = min(width, bg_x1 + text_width + int(width * 0.06))
    bg_y2 = min(height, bg_y1 + overlay_height)
    
    overlay_draw.rounded_rectangle(
        [(bg_x1, bg_y1), (bg_x2, bg_y2)],
        radius=8,  # Smaller radius for professional look
        fill=(0, 0, 0, alpha)
    )
    
    # Calculate text position - centered
    text_x = (width - text_width) // 2
    text_y = y_pos + (overlay_height - text_height) // 2
    
    # Add emoji if provided
    if emoji:
        display_text = f"{wrapped_text} {emoji}"
    else:
        display_text = wrapped_text
    
    # Draw text with slight shadow for better readability
    shadow_offset = 1
    overlay_draw.text(
        (text_x + shadow_offset, text_y + shadow_offset),
        display_text,
        fill=(0, 0, 0, 160),  # Shadow color
        font=font
    )
    
    # Draw main text - always white and bold
    overlay_draw.text(
        (text_x, text_y),
        display_text,
        fill=(255, 255, 255, 230),  # White text with slight transparency
        font=font
    )
    
    # Composite the overlay onto the original image
    if img_pil.mode != 'RGBA':
        img_pil = img_pil.convert('RGBA')
    
    result = Image.alpha_composite(img_pil, overlay)
    return result.convert('RGB')  # Convert back to RGB

def create_subtitle_frame(image, caption, timecode=None, progress=0.0, word_progress=None):
    """
    Add professional closed caption style subtitles to an image
    
    Parameters:
    - image: PIL Image object
    - caption: Text to display as subtitle
    - timecode: Optional timecode to display (e.g. "00:12")
    - progress: Animation progress (0-1)
    - word_progress: Optional float (0-1) for word-by-word highlighting
    """
    img_pil = image.copy()
    width, height = img_pil.size
    
    # Create transparent overlay for subtitles
    overlay = Image.new('RGBA', img_pil.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Font settings - REDUCED SIZE for more professional look
    try:
        font_size = int(height * 0.032)  # Smaller size (was 0.035)
        # Try to load a clean sans-serif font
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Wrap text to fit width (shorter width for captions)
    max_width_chars = 32  # Allow slightly more characters per line
    wrapped_text = textwrap.fill(caption, width=max_width_chars)
    
    # Calculate text dimensions
    try:
        text_box = overlay_draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
    except:
        # Fallback for older PIL versions
        text_width = width * 0.8  # Estimate
        line_count = len(wrapped_text.split('\n'))
        text_height = font_size * line_count * 1.2
    
    # Position at bottom with padding - FIXED POSITION, NOT MOVING
    bottom_padding = int(height * 0.05)
    text_y = height - text_height - bottom_padding
    
    # Create caption background
    # Calculate background dimensions with padding
    padding_x = int(width * 0.02)
    padding_y = int(height * 0.015)
    bg_x1 = max(0, (width - text_width) // 2 - padding_x)
    bg_y1 = max(0, text_y - padding_y)
    bg_x2 = min(width, bg_x1 + text_width + padding_x * 2)
    bg_y2 = min(height, bg_y1 + text_height + padding_y * 2)
    
    # Draw semi-transparent black background with rounded corners
    # INCREASED TRANSPARENCY for more professional look
    overlay_draw.rounded_rectangle(
        [bg_x1, bg_y1, bg_x2, bg_y2],
        radius=8,  # Slightly smaller radius
        fill=(0, 0, 0, 150)  # More transparent background (was 180)
    )
    
    # Calculate text position (centered horizontally)
    text_x = (width - text_width) // 2
    
    # Draw main text - NO ANIMATION, ALWAYS FULLY VISIBLE
    # Use white bold text (white with slight shadow for readability)
    
    # Draw shadow for better readability (simulating bold)
    shadow_offset = 1
    shadow_color = (0, 0, 0, 180)
    overlay_draw.text(
        (text_x + shadow_offset, text_y + shadow_offset),
        wrapped_text,
        fill=shadow_color,
        font=font
    )
    
    # Draw main text - ALWAYS WHITE, no word-level highlighting
    text_color = (255, 255, 255, 255)  # Bright white, fully opaque
    overlay_draw.text(
        (text_x, text_y),
        wrapped_text,
        fill=text_color,
        font=font
    )
    
    # Add timecode if provided - SIMPLIFIED, NO BACKGROUND
    if timecode:
        timecode_font_size = int(font_size * 0.7)  # Even smaller timecode
        try:
            timecode_font = ImageFont.truetype("Arial.ttf", timecode_font_size)
        except:
            timecode_font = font
        
        # Position timecode in top right - FIXED POSITION
        timecode_padding = int(height * 0.02)
        timecode_x = width - timecode_padding - overlay_draw.textlength(timecode, font=timecode_font) \
                    if hasattr(overlay_draw, 'textlength') else width - int(width * 0.1)
        timecode_y = timecode_padding
        
        # Draw timecode with slight shadow but no background - more professional
        overlay_draw.text(
            (timecode_x + 1, timecode_y + 1),
            timecode,
            fill=(0, 0, 0, 150),  # Shadow
            font=timecode_font
        )
        
        overlay_draw.text(
            (timecode_x, timecode_y),
            timecode,
            fill=(255, 255, 255, 200),  # White text
            font=timecode_font
        )
    
    # Composite the overlay onto the original image
    if img_pil.mode != 'RGBA':
        img_pil = img_pil.convert('RGBA')
    
    result = Image.alpha_composite(img_pil, overlay)
    return result.convert('RGB')  # Convert back to RGB

def create_caption_styles():
    """Return a dictionary of caption style presets for easy reuse"""
    return {
        "default": {
            "position": "bottom",
            "background_opacity": 150,
            "text_color": (255, 255, 255),
            "animation": "none"
        },
        "minimal": {
            "position": "bottom",
            "background_opacity": 130,
            "text_color": (255, 255, 255),
            "animation": "none"
        },
        "cinematic": {
            "position": "bottom",
            "background_opacity": 150,
            "text_color": (255, 255, 255),
            "text_shadow": True,
            "animation": "none"
        },
        "professional": {
            "position": "bottom",
            "background_opacity": 150,
            "text_color": (255, 255, 255),
            "rounded_corners": True,
            "animation": "none"
        }
    }
    
