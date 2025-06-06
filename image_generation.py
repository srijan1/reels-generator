"""
Functions for generating images using Stable Diffusion.
"""

import torch
import random
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoencoderKL
from huggingface_hub import login
from PIL import Image, ImageDraw

# Login to Hugging Face
def login_to_huggingface():
    """Login to Hugging Face using API token"""
    login(token="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")

def setup_stable_diffusion(device="cpu"):
    """Setup and configure Stable Diffusion pipeline"""
    print("Loading model - this may take a while on CPU...")
    
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
        print("Successfully loaded alternative VAE")
    except Exception as e:
        print(f"Could not load VAE: {e}")
        print("Continuing with default VAE")

    # Use recommended scheduler
    pipe_img.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe_img.scheduler.config,
        algorithm_type="dpmsolver++",
        solver_order=2,
        use_karras_sigmas=True
    )

    pipe_img.to(device)
    return pipe_img

def generate_segment_image(pipe_img, prompt, height=512, width=288, device="cpu"):
    """Generate an image for a segment using Stable Diffusion"""
    
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
        
        print(f"Successfully generated image with prompt: {enhanced_prompt[:100]}...")
        return image
        
    except Exception as e:
        print(f"Error generating image: {e}")
        # Create a blank placeholder image if generation fails
        image = Image.new('RGB', (width, height), color=(0, 0, 0))
        # Add text explaining the error
        draw = ImageDraw.Draw(image)
        draw.text((10, height//2), f"Image generation failed. Error: {str(e)[:50]}", fill=(255, 255, 255))
        return image
        
