"""
Functions for applying Instagram-style filters and effects to images.
"""

import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

def add_vignette(image, intensity=0.8):
    """Add a subtle vignette effect to image"""
    img_array = np.array(image).astype(np.float64)
    height, width = img_array.shape[:2]

    # Create a radial gradient
    x, y = np.meshgrid(np.linspace(-1, 1, width), np.linspace(-1, 1, height))
    radius = np.sqrt(x**2 + y**2)
    radius = radius / np.max(radius)

    # Create vignette mask
    mask = 1 - intensity * radius
    mask = np.clip(mask, 0, 1)

    # Apply mask to each color channel
    for i in range(3):
        img_array[:,:,i] = img_array[:,:,i] * mask

    return Image.fromarray(np.uint8(img_array))

def add_film_grain(image, amount=15):
    """Add film grain effect to image"""
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # Generate noise
    noise = np.random.normal(0, amount, (height, width, 3))

    # Add noise to image
    img_array = img_array.astype(np.float64)
    img_array += noise
    img_array = np.clip(img_array, 0, 255)

    return Image.fromarray(np.uint8(img_array))

def apply_natural_filter(image):
    """Apply natural look filter"""
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.1)
    saturation = ImageEnhance.Color(image)
    image = saturation.enhance(1.05)
    return image

def apply_warm_travel_filter(image):
    """Apply warm travel look filter"""
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.2)
    saturation = ImageEnhance.Color(image)
    image = saturation.enhance(1.15)

    # Add warm tone
    image_array = np.array(image)
    image_array[:,:,0] = np.clip(image_array[:,:,0] * 0.9, 0, 255)  # Reduce blue
    image_array[:,:,2] = np.clip(image_array[:,:,2] * 1.08, 0, 255)  # Enhance red
    return Image.fromarray(image_array)

def apply_moody_filter(image):
    """Apply moody atmospheric look filter"""
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.3)
    saturation = ImageEnhance.Color(image)
    image = saturation.enhance(0.9)

    # Add teal/orange toning (cinematic look)
    image_array = np.array(image)
    # Enhance blues in shadows
    blue_mask = image_array.mean(axis=2) < 100  # Shadow areas
    image_array[blue_mask, 0] = np.clip(image_array[blue_mask, 0] * 1.1, 0, 255)
    # Enhance oranges in highlights
    orange_mask = image_array.mean(axis=2) > 150  # Highlight areas
    image_array[orange_mask, 2] = np.clip(image_array[orange_mask, 2] * 1.1, 0, 255)
    image = Image.fromarray(image_array)

    # Add vignette
    image = add_vignette(image, intensity=0.3)
    return image

def apply_nostalgic_filter(image):
    """Apply nostalgic film-like look filter"""
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(0.95)
    saturation = ImageEnhance.Color(image)
    image = saturation.enhance(0.9)

    # Add slight sepia tone
    image_array = np.array(image).astype(np.float32)
    sepia_effect = np.array([0.9, 0.95, 1.1])  # RGB multipliers
    for i in range(3):
        image_array[:,:,i] = np.clip(image_array[:,:,i] * sepia_effect[i], 0, 255)
    image = Image.fromarray(np.uint8(image_array))

    # Add film grain
    image = add_film_grain(image, amount=15)
    return image

def apply_golden_hour_filter(image):
    """Apply golden hour photography filter"""
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.1)

    # Enhance golden tones
    image_array = np.array(image)
    # Boost oranges and yellows
    yellow_boost = 1.15
    orange_boost = 1.1
    image_array[:,:,1] = np.clip(image_array[:,:,1] * yellow_boost, 0, 255)  # Boost green channel (affects yellows)
    image_array[:,:,2] = np.clip(image_array[:,:,2] * orange_boost, 0, 255)  # Boost red channel
    image = Image.fromarray(image_array)

    # Add subtle light leak (top right)
    light_leak = np.zeros_like(np.array(image), dtype=np.float32)
    h, w = light_leak.shape[:2]

    # Create radial gradient from top right
    y, x = np.ogrid[:h, :w]
    center = (0, w)
    dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    max_dist = np.sqrt(h**2 + w**2)
    mask = 1 - (dist_from_center / max_dist)
    mask = np.clip(mask * 1.5, 0, 1)

    # Apply light leak with orange/golden color
    light_color = np.array([50, 100, 255])  # BGR
    for i in range(3):
        light_leak[:,:,i] = mask * light_color[i]

    # Blend with original
    image_array = np.array(image).astype(np.float32)
    blended = cv2.addWeighted(image_array, 1.0, light_leak, 0.2, 0)
    image = Image.fromarray(np.uint8(blended))
    return image

def apply_instagram_filter(image, filter_type):
    """Apply Instagram-style filters to an image"""
    # Apply selected filter
    if filter_type == "natural":
        image = apply_natural_filter(image)
    elif filter_type == "warm_travel":
        image = apply_warm_travel_filter(image)
    elif filter_type == "moody":
        image = apply_moody_filter(image)
    elif filter_type == "nostalgic":
        image = apply_nostalgic_filter(image)
    elif filter_type == "golden_hour":
        image = apply_golden_hour_filter(image)
    else:
        # Default filter if not recognized
        image = apply_warm_travel_filter(image)
    
    # Enhance details for that professional travel photography look
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.2)
    
    return image

def add_text_overlay(image, text, style="modern", progress=0, emoji=None):
    """Add Instagram-style text overlay to image"""
    img_pil = image.copy()
    width, height = img_pil.size

    # Create transparent overlay
    overlay = Image.new('RGBA', img_pil.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Attempt to find a font - fallback to default if necessary
    try:
        font_size = 36
        # Try to use a cool font if available
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        # If all else fails, we'll use the default drawing without specified font
        pass

    # Calculate text width for positioning
    try:
        # For newer PIL versions
        text_width, text_height = overlay_draw.textbbox((0, 0), text, font=font)[2:]
    except:
        # For older PIL versions
        text_width = overlay_draw.textlength(text, font=font) if hasattr(overlay_draw, 'textlength') else width * 0.8

    # Different text styles
    if style.startswith("bold"):
        # Bold centered text with gradient background
        y_pos = int(height * 0.5)  # Centered
        overlay_height = int(height * 0.2)
        y_start = max(0, y_pos - overlay_height//2)

        # Create gradient background - more Instagram-like
        for y in range(y_start, y_start + overlay_height):
            alpha = 160  # Semi-transparent
            overlay_draw.rectangle(
                [(0, y), (width, y+1)],
                fill=(0, 0, 0, alpha)
            )

        # Add text with shadow
        text_x = (width - text_width) // 2
        text_y = y_start + (overlay_height - font_size) // 2

        # Draw shadow
        overlay_draw.text(
            (text_x+2, text_y+2),
            text,
            fill=(0, 0, 0, 200),
            font=font if 'font' in locals() else None
        )

        # Draw main text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 255),
            font=font if 'font' in locals() else None
        )

    elif style.startswith("modern"):
        # Modern style at bottom with animated entry
        opacity = min(1.0, progress * 2) if progress < 0.5 else 1.0

        y_pos = int(height * 0.85)
        overlay_height = int(height * 0.15)

        # Semi-transparent black background with fade in
        overlay_draw.rectangle(
            [(0, y_pos), (width, y_pos + overlay_height)],
            fill=(0, 0, 0, int(180 * opacity))
        )

        # Calculate text position
        text_x = (width - text_width) // 2
        text_y = y_pos + (overlay_height - font_size) // 2

        # Draw text with opacity
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, int(255 * opacity)),
            font=font if 'font' in locals() else None
        )

    elif "right" in style:
        # Right aligned with stylish gradient
        x_start = int(width * 0.4)
        y_pos = int(height * 0.7)
        overlay_height = int(height * 0.15)

        # Draw gradient background
        for x in range(x_start, width):
            alpha = int(160 * (x - x_start) / (width - x_start))
            overlay_draw.rectangle(
                [(x, y_pos), (x+1, y_pos + overlay_height)],
                fill=(20, 20, 60, alpha)
            )

        # Calculate text position - right aligned
        text_x = width - text_width - 20  # Padding from right
        text_y = y_pos + (overlay_height - font_size) // 2

        # Draw text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 230),
            font=font if 'font' in locals() else None
        )

    elif "left" in style:
        # Left aligned with animated entry
        x_end = int(width * 0.6)
        y_pos = int(height * 0.7)
        overlay_height = int(height * 0.15)

        # Slide-in effect
        slide_offset = int(width * (1 - min(1.0, progress * 2.5)))

        # Draw gradient background
        gradient_start = (0, 20, 60)
        gradient_end = (20, 20, 40)

        for x in range(0, x_end):
            # Calculate gradient color
            alpha = int(160 * (1 - x / x_end))
            r = int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * (x / x_end))
            g = int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * (x / x_end))
            b = int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * (x / x_end))

            overlay_draw.rectangle(
                [(x - slide_offset, y_pos), (x + 1 - slide_offset, y_pos + overlay_height)],
                fill=(r, g, b, alpha + 60)
            )

        # Calculate text position - left aligned
        text_x = 20 - slide_offset  # Padding from left
        text_y = y_pos + (overlay_height - font_size) // 2

        # Draw text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 230),
            font=font if 'font' in locals() else None
        )

    elif "dramatic" in style:
        # Dramatic centered text with animated zoom
        zoom_factor = 1.0 + 0.2 * (1 - abs(progress - 0.5) * 2)
        center_y = height // 2
        overlay_height = int(height * 0.25 * zoom_factor)
        y_start = max(0, center_y - overlay_height//2)

        # Dark gradient background
        for y in range(y_start, min(height, y_start + overlay_height)):
            dist_from_center = abs(y - center_y) / (overlay_height/2)
            alpha = int(200 * (1 - dist_from_center))
            overlay_draw.rectangle(
                [(0, y), (width, y+1)],
                fill=(0, 0, 0, alpha)
            )

        # Scale font size for dramatic effect
        big_font_size = int(font_size * 1.5 * zoom_factor)
        try:
            big_font = ImageFont.truetype("Arial.ttf", big_font_size)
        except:
            big_font = font  # Fallback to regular font

        # Calculate text position
        try:
            # For newer PIL versions
            big_text_width, _ = overlay_draw.textbbox((0, 0), text, font=big_font)[2:]
        except:
            # For older PIL versions
            big_text_width = overlay_draw.textlength(text, font=big_font) if 'big_font' in locals() and hasattr(overlay_draw, 'textlength') else width * 0.9
        
        text_x = (width - big_text_width) // 2
        text_y = center_y - big_font_size // 2

        # Draw shadow
        shadow_offset = int(2 * zoom_factor)
        overlay_draw.text(
            (text_x + shadow_offset, text_y + shadow_offset),
            text,
            fill=(0, 0, 0, 200),
            font=big_font if 'big_font' in locals() else None
        )

        # Draw main text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 255),
            font=big_font if 'big_font' in locals() else None
        )

    elif "call" in style:
        # Call to action with animated appearance and emoji
        opacity = 0
        if progress > 0.4:
            opacity = min(1.0, (progress - 0.4) * 1.7)

        if opacity > 0:
            # Center position
            center_y = height // 2
            overlay_height = int(height * 0.3)
            y_start = max(0, center_y - overlay_height//2)

            # Create a gradient background with animated opacity
            for y in range(y_start, min(height, y_start + overlay_height)):
                dist_from_center = abs(y - center_y) / (overlay_height/2)
                alpha = int(180 * (1 - dist_from_center) * opacity)
                overlay_draw.rectangle(
                    [(0, y), (width, y+1)],
                    fill=(30, 30, 100, alpha)
                )

            # Adding emoji if provided
            if emoji:
                full_text = f"{text} {emoji}"
            else:
                full_text = f"{text} ✨"

            # Calculate text position
            try:
                # For newer PIL versions
                emoji_text_width, _ = overlay_draw.textbbox((0, 0), full_text, font=font)[2:]
            except:
                # For older PIL versions
                emoji_text_width = overlay_draw.textlength(full_text, font=font) if 'font' in locals() and hasattr(overlay_draw, 'textlength') else width * 0.8
            
            text_x = (width - emoji_text_width) // 2
            text_y = center_y - font_size // 2

            # Draw text with glow effect
            for offset in range(1, 4):
                alpha = int(50 * opacity * (4-offset) / 3)
                overlay_draw.text(
                    (text_x + offset, text_y),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )
                overlay_draw.text(
                    (text_x - offset, text_y),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )
                overlay_draw.text(
                    (text_x, text_y + offset),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )
                overlay_draw.text(
                    (text_x, text_y - offset),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )

            # Draw main text
            overlay_draw.text(
                (text_x, text_y),
                full_text,
                fill=(255, 255, 255, int(255 * opacity)),
                font=font if 'font' in locals() else None
            )

    # Composite the overlay onto the original image
    # Convert to RGBA first if not already
    if img_pil.mode != 'RGBA':
        img_pil = img_pil.convert('RGBA')

    result = Image.alpha_composite(img_pil, overlay)
    return result.convert('RGB')  # Convert back to RGBance.Color(image)
    image = saturation.enhance(0.9)

    # Add slight sepia tone
    image_array = np.array(image).astype(np.float32)
    sepia_effect = np.array([0.9, 0.95, 1.1])  # RGB multipliers
    for i in range(3):
        image_array[:,:,i] = np.clip(image_array[:,:,i] * sepia_effect[i], 0, 255)
    image = Image.fromarray(np.uint8(image_array))

    # Add film grain
    image = add_film_grain(image, amount=15)
    return image

def apply_golden_hour_filter(image):
    """Apply golden hour photography filter"""
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.1)

    # Enhance golden tones
    image_array = np.array(image)
    # Boost oranges and yellows
    yellow_boost = 1.15
    orange_boost = 1.1
    image_array[:,:,1] = np.clip(image_array[:,:,1] * yellow_boost, 0, 255)  # Boost green channel (affects yellows)
    image_array[:,:,2] = np.clip(image_array[:,:,2] * orange_boost, 0, 255)  # Boost red channel
    image = Image.fromarray(image_array)

    # Add subtle light leak (top right)
    light_leak = np.zeros_like(np.array(image), dtype=np.float32)
    h, w = light_leak.shape[:2]

    # Create radial gradient from top right
    y, x = np.ogrid[:h, :w]
    center = (0, w)
    dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    max_dist = np.sqrt(h**2 + w**2)
    mask = 1 - (dist_from_center / max_dist)
    mask = np.clip(mask * 1.5, 0, 1)

    # Apply light leak with orange/golden color
    light_color = np.array([50, 100, 255])  # BGR
    for i in range(3):
        light_leak[:,:,i] = mask * light_color[i]

    # Blend with original
    image_array = np.array(image).astype(np.float32)
    blended = cv2.addWeighted(image_array, 1.0, light_leak, 0.2, 0)
    image = Image.fromarray(np.uint8(blended))
    return image

def apply_instagram_filter(image, filter_type):
    """Apply Instagram-style filters to an image"""
    # Apply selected filter
    if filter_type == "natural":
        image = apply_natural_filter(image)
    elif filter_type == "warm_travel":
        image = apply_warm_travel_filter(image)
    elif filter_type == "moody":
        image = apply_moody_filter(image)
    elif filter_type == "nostalgic":
        image = apply_nostalgic_filter(image)
    elif filter_type == "golden_hour":
        image = apply_golden_hour_filter(image)
    else:
        # Default filter if not recognized
        image = apply_warm_travel_filter(image)
    
    # Enhance details for that professional travel photography look
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.2)
    
    return image

def add_text_overlay(image, text, style="modern", progress=0, emoji=None):
    """Add Instagram-style text overlay to image"""
    from PIL import ImageFont
    
    img_pil = image.copy()
    width, height = img_pil.size

    # Create transparent overlay
    overlay = Image.new('RGBA', img_pil.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Attempt to find a font - fallback to default if necessary
    try:
        font_size = 36
        # Try to use a cool font if available
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        # If all else fails, we'll use the default drawing without specified font
        pass

    # Calculate text width for positioning
    text_width = overlay_draw.textlength(text, font=font) if 'font' in locals() else width * 0.8

    # Different text styles
    if style.startswith("bold"):
        # Bold centered text with gradient background
        y_pos = int(height * 0.5)  # Centered
        overlay_height = int(height * 0.2)
        y_start = max(0, y_pos - overlay_height//2)

        # Create gradient background - more Instagram-like
        for y in range(y_start, y_start + overlay_height):
            alpha = 160  # Semi-transparent
            overlay_draw.rectangle(
                [(0, y), (width, y+1)],
                fill=(0, 0, 0, alpha)
            )

        # Add text with shadow
        text_x = (width - text_width) // 2
        text_y = y_start + (overlay_height - font_size) // 2

        # Draw shadow
        overlay_draw.text(
            (text_x+2, text_y+2),
            text,
            fill=(0, 0, 0, 200),
            font=font if 'font' in locals() else None
        )

        # Draw main text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 255),
            font=font if 'font' in locals() else None
        )

    elif style.startswith("modern"):
        # Modern style at bottom with animated entry
        opacity = min(1.0, progress * 2) if progress < 0.5 else 1.0

        y_pos = int(height * 0.85)
        overlay_height = int(height * 0.15)

        # Semi-transparent black background with fade in
        overlay_draw.rectangle(
            [(0, y_pos), (width, y_pos + overlay_height)],
            fill=(0, 0, 0, int(180 * opacity))
        )

        # Calculate text position
        text_x = (width - text_width) // 2
        text_y = y_pos + (overlay_height - font_size) // 2

        # Draw text with opacity
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, int(255 * opacity)),
            font=font if 'font' in locals() else None
        )

    elif "right" in style:
        # Right aligned with stylish gradient
        x_start = int(width * 0.4)
        y_pos = int(height * 0.7)
        overlay_height = int(height * 0.15)

        # Draw gradient background
        for x in range(x_start, width):
            alpha = int(160 * (x - x_start) / (width - x_start))
            overlay_draw.rectangle(
                [(x, y_pos), (x+1, y_pos + overlay_height)],
                fill=(20, 20, 60, alpha)
            )

        # Calculate text position - right aligned
        text_x = width - text_width - 20  # Padding from right
        text_y = y_pos + (overlay_height - font_size) // 2

        # Draw text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 230),
            font=font if 'font' in locals() else None
        )

    elif "left" in style:
        # Left aligned with animated entry
        x_end = int(width * 0.6)
        y_pos = int(height * 0.7)
        overlay_height = int(height * 0.15)

        # Slide-in effect
        slide_offset = int(width * (1 - min(1.0, progress * 2.5)))

        # Draw gradient background
        gradient_start = (0, 20, 60)
        gradient_end = (20, 20, 40)

        for x in range(0, x_end):
            # Calculate gradient color
            alpha = int(160 * (1 - x / x_end))
            r = int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * (x / x_end))
            g = int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * (x / x_end))
            b = int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * (x / x_end))

            overlay_draw.rectangle(
                [(x - slide_offset, y_pos), (x + 1 - slide_offset, y_pos + overlay_height)],
                fill=(r, g, b, alpha + 60)
            )

        # Calculate text position - left aligned
        text_x = 20 - slide_offset  # Padding from left
        text_y = y_pos + (overlay_height - font_size) // 2

        # Draw text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 230),
            font=font if 'font' in locals() else None
        )

    elif "dramatic" in style:
        # Dramatic centered text with animated zoom
        zoom_factor = 1.0 + 0.2 * (1 - abs(progress - 0.5) * 2)
        center_y = height // 2
        overlay_height = int(height * 0.25 * zoom_factor)
        y_start = max(0, center_y - overlay_height//2)

        # Dark gradient background
        for y in range(y_start, min(height, y_start + overlay_height)):
            dist_from_center = abs(y - center_y) / (overlay_height/2)
            alpha = int(200 * (1 - dist_from_center))
            overlay_draw.rectangle(
                [(0, y), (width, y+1)],
                fill=(0, 0, 0, alpha)
            )

        # Scale font size for dramatic effect
        big_font_size = int(font_size * 1.5 * zoom_factor)
        try:
            big_font = ImageFont.truetype("Arial.ttf", big_font_size)
        except:
            big_font = font  # Fallback to regular font

        # Calculate text position
        big_text_width = overlay_draw.textlength(text, font=big_font) if 'big_font' in locals() else width * 0.9
        text_x = (width - big_text_width) // 2
        text_y = center_y - big_font_size // 2

        # Draw shadow
        shadow_offset = int(2 * zoom_factor)
        overlay_draw.text(
            (text_x + shadow_offset, text_y + shadow_offset),
            text,
            fill=(0, 0, 0, 200),
            font=big_font if 'big_font' in locals() else None
        )

        # Draw main text
        overlay_draw.text(
            (text_x, text_y),
            text,
            fill=(255, 255, 255, 255),
            font=big_font if 'big_font' in locals() else None
        )

    elif "call" in style:
        # Call to action with animated appearance and emoji
        opacity = 0
        if progress > 0.4:
            opacity = min(1.0, (progress - 0.4) * 1.7)

        if opacity > 0:
            # Center position
            center_y = height // 2
            overlay_height = int(height * 0.3)
            y_start = max(0, center_y - overlay_height//2)

            # Create a gradient background with animated opacity
            for y in range(y_start, min(height, y_start + overlay_height)):
                dist_from_center = abs(y - center_y) / (overlay_height/2)
                alpha = int(180 * (1 - dist_from_center) * opacity)
                overlay_draw.rectangle(
                    [(0, y), (width, y+1)],
                    fill=(30, 30, 100, alpha)
                )

            # Adding emoji if provided
            if emoji:
                full_text = f"{text} {emoji}"
            else:
                full_text = f"{text} ✨"

            # Calculate text position
            text_width = overlay_draw.textlength(full_text, font=font) if 'font' in locals() else width * 0.8
            text_x = (width - text_width) // 2
            text_y = center_y - font_size // 2

            # Draw text with glow effect
            for offset in range(1, 4):
                alpha = int(50 * opacity * (4-offset) / 3)
                overlay_draw.text(
                    (text_x + offset, text_y),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )
                overlay_draw.text(
                    (text_x - offset, text_y),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )
                overlay_draw.text(
                    (text_x, text_y + offset),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )
                overlay_draw.text(
                    (text_x, text_y - offset),
                    full_text,
                    fill=(100, 100, 255, alpha),
                    font=font if 'font' in locals() else None
                )

            # Draw main text
            overlay_draw.text(
                (text_x, text_y),
                full_text,
                fill=(255, 255, 255, int(255 * opacity)),
                font=font if 'font' in locals() else None
            )

    # Composite the overlay onto the original image
    # Convert to RGBA first if not already
    if img_pil.mode != 'RGBA':
        img_pil = img_pil.convert('RGBA')

    result = Image.alpha_composite(img_pil, overlay)
    return result.convert('RGB')  # Convert back to RGB