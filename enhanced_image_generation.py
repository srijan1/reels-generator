"""
Enhanced image generation using both Pexels stock photos and Stable Diffusion.
Half the images come from Pexels, half from AI generation.
"""

import os
import torch
import random
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoencoderKL
from huggingface_hub import login
from PIL import Image, ImageDraw, ImageFont
from pexels_integration import get_pexels_image, test_pexels_api

# Login to Hugging Face
def login_to_huggingface():
    """Login to Hugging Face using API token"""
    login(token="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")

def setup_stable_diffusion(device="cpu"):
    """Setup and configure Stable Diffusion pipeline"""
    print("🤖 Loading Stable Diffusion model - this may take a while on CPU...")
    
    # Login to Hugging Face
    login_to_huggingface()
    
    # Load Stable Diffusion model
    pipe_img = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,
                safety_checker=None,
            )

    # Try to load VAE
    try:
        vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float32)
        pipe_img.vae = vae
        print("✅ Successfully loaded alternative VAE")
    except Exception as e:
        print(f"⚠️  Could not load VAE: {e}")
        print("Continuing with default VAE")

    # Use recommended scheduler
    pipe_img.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe_img.scheduler.config,
        algorithm_type="dpmsolver++",
        solver_order=2,
        use_karras_sigmas=True
    )

    pipe_img.to(device)
    print("✅ Stable Diffusion model loaded successfully")
    return pipe_img

def generate_ai_image(pipe_img, prompt, height=512, width=288, device="cpu"):
    """Generate an image using Stable Diffusion"""
    
    # Add realistic travel photography terms to prompt
    enhanced_prompt = f"{prompt}, authentic travel photography, photorealistic, detailed, cinematic lighting, 9:16 vertical format, high detail"

    # Negative prompt to avoid common issues
    negative_prompt = """(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, manga style),
    text, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated,
    extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed,
    blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured,
    gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs,
    fused fingers, too many fingers, long neck, strange facial features, distorted features, text overlay, watermark, logo"""

    # Use different seeds for each image for variety
    seed = random.randint(1, 10000)
    generator = torch.Generator(device=device).manual_seed(seed)

    # Reduce number of inference steps for CPU
    num_steps = 40  # Reduced for faster generation on CPU

    try:
        print(f"🎨 Generating AI image with Stable Diffusion...")
        # Generate image
        image = pipe_img(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_steps,
            guidance_scale=7.5,
            height=height,
            width=width,  # 9:16 aspect ratio
            generator=generator
        ).images[0]
        
        print(f"✅ Successfully generated AI image")
        return image
        
    except Exception as e:
        print(f"❌ Error generating AI image: {e}")
        return create_fallback_image(width, height, f"AI generation failed: {str(e)[:50]}")

def create_fallback_image(width, height, message):
    """Create a fallback image when both Pexels and AI generation fail"""
    print(f"🎨 Creating fallback placeholder image...")
    
    # Create a gradient background
    image = Image.new('RGB', (width, height), color=(100, 100, 120))
    draw = ImageDraw.Draw(image)
    
    # Add gradient effect
    for y in range(height):
        progress = y / height
        color_value = int(100 + (50 * progress))
        color = (color_value, color_value, color_value + 20)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add text explaining the situation
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Wrap text
    lines = []
    words = message.split()
    current_line = ""
    max_width = width - 20
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        try:
            text_width = draw.textbbox((0, 0), test_line, font=font)[2]
        except:
            text_width = len(test_line) * 10  # Rough estimate
            
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Draw text
    total_text_height = len(lines) * 25
    start_y = (height - total_text_height) // 2
    
    for i, line in enumerate(lines):
        try:
            text_width = draw.textbbox((0, 0), line, font=font)[2]
        except:
            text_width = len(line) * 10
            
        x = (width - text_width) // 2
        y = start_y + (i * 25)
        
        # Draw shadow
        draw.text((x + 1, y + 1), line, font=font, fill=(0, 0, 0))
        # Draw main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
    
    return image

def determine_image_strategy(segments):
    """
    Determine which segments should use Pexels vs AI generation
    
    Parameters:
    - segments: List of segment dictionaries
    
    Returns:
    - Dictionary mapping segment indices to generation method ('pexels' or 'ai')
    """
    total_segments = len(segments)
    
    # Determine how many should use each method
    # pexels_count = total_segments // 2
    pexels_count = total_segments
    ai_count = total_segments - pexels_count
    
    print(f"📊 Image Generation Strategy:")
    print(f"   📸 Pexels stock photos: {pexels_count} images")
    print(f"   🤖 AI generated: {ai_count} images")
    
    # Create strategy mapping
    strategy = {}
    
    # Randomly assign methods, but ensure good distribution
    segment_indices = list(range(total_segments))
    random.shuffle(segment_indices)
    
    # Assign first half to Pexels
    for i in range(pexels_count):
        strategy[segment_indices[i]] = 'pexels'
    
    # Assign rest to AI
    for i in range(pexels_count, total_segments):
        strategy[segment_indices[i]] = 'ai'
    
    return strategy

def generate_segment_images_mixed(segments, base_dir, height=512, width=288, device="cpu"):
    """
    Generate images for all segments using a mix of Pexels and Stable Diffusion
    
    Parameters:
    - segments: List of segment dictionaries with image prompts
    - base_dir: Base directory for saving images
    - height: Target image height
    - width: Target image width
    - device: Device for AI generation
    
    Returns:
    - List of image paths
    """
    print("🎨 Starting mixed image generation (Pexels + AI)...")
    
    # Test Pexels API first
    pexels_available = test_pexels_api()
    if not pexels_available:
        print("⚠️  Pexels API not available, will use more AI generation")
    
    # Determine generation strategy
    strategy = determine_image_strategy(segments)
    
    # Setup Stable Diffusion for AI images
    pipe_img = None
    ai_segments = [i for i, method in strategy.items() if method == 'ai']
    
    if ai_segments:
        try:
            pipe_img = setup_stable_diffusion(device)
        except Exception as e:
            print(f"⚠️  Could not setup Stable Diffusion: {e}")
            print("Will try to use more Pexels images instead")
    
    # Generate images for each segment
    segment_images = []
    
    for i, segment in enumerate(segments):
        print(f"\n📸 Generating image for segment {i+1}/{len(segments)}")
        image_path = f"{base_dir}/2_images/segment_{i+1}.png"
        image = None
        
        generation_method = strategy.get(i, 'ai')
        
        # Try the assigned method first
        if generation_method == 'pexels' and pexels_available:
            print(f"📸 Using Pexels stock photo for segment {i+1}")
            image = get_pexels_image(
                segment["image_prompt"], 
                image_path, 
                target_width=width, 
                target_height=height
            )
            
            # If Pexels fails, fall back to AI
            if not image and pipe_img:
                print(f"⚠️  Pexels failed, falling back to AI for segment {i+1}")
                image = generate_ai_image(
                    pipe_img, 
                    segment["image_prompt"], 
                    height=height, 
                    width=width, 
                    device=device
                )
        
        elif generation_method == 'ai' and pipe_img:
            print(f"🤖 Using AI generation for segment {i+1}")
            image = generate_ai_image(
                pipe_img, 
                segment["image_prompt"], 
                height=height, 
                width=width, 
                device=device
            )
            
            # If AI fails, try Pexels
            if not image and pexels_available:
                print(f"⚠️  AI generation failed, trying Pexels for segment {i+1}")
                image = get_pexels_image(
                    segment["image_prompt"], 
                    image_path, 
                    target_width=width, 
                    target_height=height
                )
        
        # Final fallback: create placeholder
        if not image:
            print(f"⚠️  Both methods failed, creating placeholder for segment {i+1}")
            image = create_fallback_image(
                width, 
                height, 
                f"Segment {i+1}: {segment.get('text', 'No text')[:50]}..."
            )
        
        # Save the image if it wasn't already saved by Pexels
        if image and not os.path.exists(image_path):
            image.save(image_path, format="PNG", compress_level=0)
        
        segment_images.append(image_path)
        print(f"✅ Image for segment {i+1} saved to {image_path}")
    
    # Clean up AI model
    if pipe_img:
        del pipe_img
        torch.cuda.empty_cache()
    
    print(f"\n✅ All {len(segment_images)} images generated successfully!")
    return segment_images

# Compatibility function for existing code
def generate_segment_image(pipe_img, prompt, height=512, width=288, device="cpu"):
    """Legacy function for backward compatibility"""
    return generate_ai_image(pipe_img, prompt, height, width, device)
