"""
Enhanced image generation using both Pexels stock photos and Stable Diffusion.
Half the images come from Pexels, half from AI generation.
"""

import os
import torch
import random
import logging
import traceback
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoencoderKL
from huggingface_hub import login
from PIL import Image, ImageDraw, ImageFont
from pexels_integration import get_pexels_image, test_pexels_api

# --- Error Logging Setup ---
logging.basicConfig(
    filename="image_generation_errors.log",
    filemode="a",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s\n%(pathname)s:%(lineno)d\n"
)

def log_exception(e, context=""):
    logging.error(f"{context}\n{traceback.format_exc()}")

# Login to Hugging Face
def login_to_huggingface():
    try:
        login(token="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")
    except Exception as e:
        log_exception(e, "Error during Hugging Face login")
        print("❌ Error during Hugging Face login. See log for details.")

def setup_stable_diffusion(device="cuda"):
    try:
        print("🤖 Loading Stable Diffusion model - this may take a while on CPU...")
        login_to_huggingface()
        pipe_img = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32,
            safety_checker=None,
        )
        try:
            vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float32)
            pipe_img.vae = vae
            print("✅ Successfully loaded alternative VAE")
        except Exception as e:
            log_exception(e, "Error loading VAE")
            print(f"⚠️  Could not load VAE: {e}")
            print("Continuing with default VAE")

        pipe_img.scheduler = DPMSolverMultistepScheduler.from_config(
            pipe_img.scheduler.config,
            algorithm_type="dpmsolver++",
            solver_order=2,
            use_karras_sigmas=True
        )

        pipe_img.to(device)
        print("✅ Stable Diffusion model loaded successfully")
        return pipe_img
    except Exception as e:
        log_exception(e, "Error setting up Stable Diffusion pipeline")
        print("❌ Error setting up Stable Diffusion pipeline. See log for details.")
        raise

def generate_ai_image(pipe_img, prompt, height=512, width=288, device="cpu"):
    try:
        enhanced_prompt = f"{prompt}, authentic travel photography, photorealistic, detailed, cinematic lighting, 9:16 vertical format, high detail"
        negative_prompt = """(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, manga style),
        text, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated,
        extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed,
        blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured,
        gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs,
        fused fingers, too many fingers, long neck, strange facial features, distorted features, text overlay, watermark, logo"""
        seed = random.randint(1, 10000)
        generator = torch.Generator(device=device).manual_seed(seed)
        num_steps = 40

        print(f"🎨 Generating AI image with Stable Diffusion...")
        image = pipe_img(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_steps,
            guidance_scale=7.5,
            height=height,
            width=width,
            generator=generator
        ).images[0]
        print(f"✅ Successfully generated AI image")
        return image
    except Exception as e:
        log_exception(e, "Error generating AI image")
        print(f"❌ Error generating AI image: {e}. See log for details.")
        return create_fallback_image(width, height, f"AI generation failed: {str(e)[:50]}")

def create_fallback_image(width, height, message):
    try:
        print(f"🎨 Creating fallback placeholder image...")
        image = Image.new('RGB', (width, height), color=(100, 100, 120))
        draw = ImageDraw.Draw(image)
        for y in range(height):
            progress = y / height
            color_value = int(100 + (50 * progress))
            color = (color_value, color_value, color_value + 20)
            draw.line([(0, y), (width, y)], fill=color)
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except Exception as e:
            log_exception(e, "Error loading font in fallback image")
            font = ImageFont.load_default()
        lines = []
        words = message.split()
        current_line = ""
        max_width = width - 20
        for word in words:
            test_line = current_line + " " + word if current_line else word
            try:
                text_width = draw.textbbox((0, 0), test_line, font=font)[2]
            except Exception as e:
                log_exception(e, "Error measuring text width in fallback image")
                text_width = len(test_line) * 10
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        total_text_height = len(lines) * 25
        start_y = (height - total_text_height) // 2
        for i, line in enumerate(lines):
            try:
                text_width = draw.textbbox((0, 0), line, font=font)[2]
            except Exception as e:
                log_exception(e, "Error measuring text width (draw) in fallback image")
                text_width = len(line) * 10
            x = (width - text_width) // 2
            y = start_y + (i * 25)
            draw.text((x + 1, y + 1), line, font=font, fill=(0, 0, 0))
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
        return image
    except Exception as e:
        log_exception(e, "Error creating fallback image")
        raise

def determine_image_strategy(segments):
    try:
        total_segments = len(segments)
        pexels_count = 0
        ai_count = total_segments - pexels_count
        print(f"📊 Image Generation Strategy:")
        print(f"   📸 Pexels stock photos: {pexels_count} images")
        print(f"   🤖 AI generated: {ai_count} images")
        strategy = {}
        segment_indices = list(range(total_segments))
        random.shuffle(segment_indices)
        for i in range(pexels_count):
            strategy[segment_indices[i]] = 'pexels'
        for i in range(pexels_count, total_segments):
            strategy[segment_indices[i]] = 'ai'
        return strategy
    except Exception as e:
        log_exception(e, "Error determining image strategy")
        raise

def generate_segment_images_mixed(segments, base_dir, height=512, width=288, device="cpu"):
    try:
        print("🎨 Starting mixed image generation (Pexels + AI)...")
        pexels_available = False
        try:
            pexels_available = test_pexels_api()
        except Exception as e:
            log_exception(e, "Error testing Pexels API")
            print("⚠️  Error testing Pexels API. See log for details.")
        if not pexels_available:
            print("⚠️  Pexels API not available, will use more AI generation")
        strategy = determine_image_strategy(segments)
        pipe_img = None
        ai_segments = [i for i, method in strategy.items() if method == 'ai']
        if ai_segments:
            try:
                pipe_img = setup_stable_diffusion(device)
            except Exception as e:
                log_exception(e, "Error setting up Stable Diffusion in generate_segment_images_mixed")
                print(f"⚠️  Could not setup Stable Diffusion: {e}")
                print("Will try to use more Pexels images instead")
        segment_images = []
        for i, segment in enumerate(segments):
            try:
                print(f"\n📸 Generating image for segment {i+1}/{len(segments)}")
                image_path = f"{base_dir}/2_images/segment_{i+1}.png"
                image = None
                generation_method = strategy.get(i, 'ai')
                if generation_method == 'pexels' and pexels_available:
                    print(f"📸 Using Pexels stock photo for segment {i+1}")
                    try:
                        image = get_pexels_image(
                            segment["image_prompt"],
                            image_path,
                            target_width=width,
                            target_height=height
                        )
                    except Exception as e:
                        log_exception(e, f"Error getting Pexels image for segment {i+1}")
                        image = None
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
                    if not image and pexels_available:
                        print(f"⚠️  AI generation failed, trying Pexels for segment {i+1}")
                        try:
                            image = get_pexels_image(
                                segment["image_prompt"],
                                image_path,
                                target_width=width,
                                target_height=height
                            )
                        except Exception as e:
                            log_exception(e, f"Error getting Pexels image (fallback) for segment {i+1}")
                            image = None
                if not image:
                    print(f"⚠️  Both methods failed, creating placeholder for segment {i+1}")
                    image = create_fallback_image(
                        width,
                        height,
                        f"Segment {i+1}: {segment.get('text', 'No text')[:50]}..."
                    )
                if image and not os.path.exists(image_path):
                    try:
                        image.save(image_path, format="PNG", compress_level=0)
                    except Exception as e:
                        log_exception(e, f"Error saving image for segment {i+1}")
                segment_images.append(image_path)
                print(f"✅ Image for segment {i+1} saved to {image_path}")
            except Exception as e:
                log_exception(e, f"Error in image generation loop for segment {i+1}")
        if pipe_img:
            del pipe_img
            try:
                torch.cuda.empty_cache()
            except Exception as e:
                log_exception(e, "Error emptying CUDA cache")
        print(f"\n✅ All {len(segment_images)} images generated successfully!")
        return segment_images
    except Exception as e:
        log_exception(e, "Error in generate_segment_images_mixed")
        print("❌ Error in generate_segment_images_mixed. See log for details.")
        return []

def generate_segment_image(pipe_img, prompt, height=512, width=288, device="cpu"):
    try:
        return generate_ai_image(pipe_img, prompt, height, width, device)
    except Exception as e:
        log_exception(e, "Error in generate_segment_image")
        return create_fallback_image(width, height, "Legacy AI image generation failed.")
