"""
Main script for Instagram Reels Generator.
This is the entry point that orchestrates the entire process.
"""

import os
import time
import torch
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from image_effects import apply_instagram_filter
from motion_effects import create_motion_frames
from transitions import create_transition_frames
from grok_integration import generate_narration, convert_text_to_speech, get_audio_duration
from video_assembly import compile_frames, create_audio_track, create_final_video
from image_generation import generate_segment_image, setup_stable_diffusion
from utils import adjust_segment_duration

def main():
    """Main function to create the Instagram Reel with voice narration"""
    
    # Create directories
    timestamp = int(time.time())
    base_dir = f"./story_reel_{timestamp}"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(f"{base_dir}/1_script", exist_ok=True)
    os.makedirs(f"{base_dir}/2_images", exist_ok=True)
    os.makedirs(f"{base_dir}/3_frames", exist_ok=True)
    os.makedirs(f"{base_dir}/4_transitions", exist_ok=True)
    os.makedirs(f"{base_dir}/5_final", exist_ok=True)
    os.makedirs(f"{base_dir}/6_audio", exist_ok=True)

    # Step 1: Generate narrative story content
    print("Step 1: Generating narrative story content...")

    # This story follows a real person's travel vlog
    travel_story_script = {
        "title": "My Solo Trip to Kyoto",
        "style": "authentic, cinematic, immersive travel vlog",
        "aspect_ratio": "9:16",  # Vertical format for Reels
        "background_music": "japanese_lofi.mp3",  # Placeholder for music track
        "segments": [
            {
                "text": "After months of planning, I finally made it to Kyoto, Japan 🇯🇵",
                "text_overlay": True,
                "text_style": "bold, centered",
                "duration_seconds": 7,  # Extended for narration
                "image_prompt": "Young traveler with backpack arriving at Kyoto train station, looking excited and slightly tired, golden hour lighting, candid moment, Japanese signs visible, vertical format, 9:16 aspect ratio",
                "zoom_direction": "in",
                "transition": "smooth_fade",
                "emoji": "✈️"
            },
            {
                "text": "First stop: Fushimi Inari Shrine at sunrise to beat the crowds",
                "text_overlay": True,
                "text_style": "modern",
                "duration_seconds": 7,
                "image_prompt": "POV walking through iconic red torii gates at Fushimi Inari Shrine at dawn, misty atmosphere, soft morning light filtering through, no people visible, path stretching ahead, vertical 9:16 format",
                "zoom_direction": "forward_push",
                "transition": "slide_up"
            },
            {
                "text": "Kyoto's traditional architecture is absolutely stunning",
                "text_overlay": True,
                "text_style": "right aligned",
                "duration_seconds": 7,
                "image_prompt": "Close-up details of traditional Japanese wooden temple architecture, intricate carvings, slightly weathered, beautiful craftsmanship, soft natural lighting, vertical 9:16 format, authentic travel photography style",
                "zoom_direction": "slow_pan",
                "transition": "color_pulse"
            },
            {
                "text": "Found this hidden tea house where locals actually go",
                "text_overlay": True,
                "text_style": "left aligned",
                "duration_seconds": 7,
                "image_prompt": "Cozy traditional Japanese tea house interior, authentic setting, steam rising from tea cup in foreground, elderly Japanese shop owner preparing tea in background, warm intimate lighting, vertical 9:16 format",
                "zoom_direction": "gentle_zoom_out",
                "transition": "slide_left"
            }
        ]
    }

    # Use shorter script for testing - remove this in production
    # Add more segments if you want a longer video
    
    # Adjust segment durations to target 1 minute total video length
    travel_story_script = adjust_segment_duration(travel_story_script, target_total_duration=30)

    # Save the script to file
    script_path = f"{base_dir}/1_script/story_script.json"
    with open(script_path, 'w') as f:
        json.dump(travel_story_script, f, indent=4)

    print(f"Story script saved to {script_path}")

    # Step 2: Generate enhanced narration
    print("\nStep 2: Generating enhanced narration content...")

    # Generate narration for each segment
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"Generating narration for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Get the original text and image prompt
        original_text = segment["text"]
        image_prompt = segment["image_prompt"]
        
        # Generate enhanced narration content
        enhanced_narration = generate_narration(
            image_prompt, 
            original_text, 
            desired_duration_seconds=segment["duration_seconds"]
        )
        
        # Store the narration in the segment
        segment["narration"] = enhanced_narration

    # Save the updated script with narrations
    narration_script_path = f"{base_dir}/1_script/story_script_with_narration.json"
    with open(narration_script_path, 'w') as f:
        json.dump(travel_story_script, f, indent=4)

    print(f"Narration script saved to {narration_script_path}")

    # Step 3: Generate audio files using Speechify API (with fallback)
    print("\nStep 3: Generating audio narrations...")

    # List of voices to cycle through for variety
    voices = ["Stephanie", "Jennifer", "Peter", "Alex", "Lily"]

    # Generate audio for each segment
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"Generating audio for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Get the narration text
        narration_text = segment.get("narration", segment["text"])
        
        # Choose a voice (cyclic)
        voice = voices[i % len(voices)]
        
        # Generate audio file
        audio_path = f"{base_dir}/6_audio/segment_{i+1}.mp3"
        audio_file = convert_text_to_speech(narration_text, voice=voice, output_path=audio_path)
        
        if audio_file:
            # Get the actual duration of the audio
            duration = get_audio_duration(audio_file)
            if duration:
                print(f"Audio duration: {duration:.2f} seconds")
                # Update the segment duration based on the actual audio
                segment["audio_duration"] = duration
                # Store the audio path
                segment["audio_path"] = audio_file

    # Save the updated script with audio information
    audio_script_path = f"{base_dir}/1_script/story_script_with_audio.json"
    with open(audio_script_path, 'w') as f:
        json.dump(travel_story_script, f, indent=4)

    print(f"Audio script saved to {audio_script_path}")

    # Step 4: Generate images for each segment with storytelling focus
    print("\nStep 4: Generating images for each segment...")

    # Determine device - CPU for compatibility
    device = "cpu"
    print(f"Using device: {device}")

    # First try to use Stable Diffusion for image generation
    try:
        # Setup Stable Diffusion model
        pipe_img = setup_stable_diffusion(device)

        # Image dimensions
        HEIGHT = 512  # Reduced from 1024
        WIDTH = 288   # Reduced from 576 (maintaining 9:16 aspect ratio)

        # Generate image for each segment
        segment_images = []

        for i, segment in enumerate(travel_story_script["segments"]):
            print(f"Generating image for segment {i+1}/{len(travel_story_script['segments'])}")

            # Generate image
            image_path = f"{base_dir}/2_images/segment_{i+1}.png"
            image = generate_segment_image(
                pipe_img, 
                segment["image_prompt"], 
                height=HEIGHT, 
                width=WIDTH,
                device=device
            )

            # Apply Instagram filter
            filter_type = ["natural", "warm_travel", "moody", "nostalgic", "golden_hour"][i % 5]
            print(f"Applying {filter_type} filter...")
            image = apply_instagram_filter(image, filter_type)

            # Save image
            image.save(image_path, format="PNG", compress_level=0)
            segment_images.append(image_path)
            print(f"Image for segment {i+1} saved to {image_path}")

        # Free up memory
        del pipe_img
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"\nError with Stable Diffusion: {e}")
        print("Falling back to placeholder images...\n")
        
        # Create placeholder images instead
        # Image dimensions
        HEIGHT = 512
        WIDTH = 288  # 9:16 aspect ratio

        # Create placeholder images for each segment
        segment_images = []

        # Create placeholder directory if it doesn't exist
        placeholder_dir = f"{base_dir}/2_images"
        os.makedirs(placeholder_dir, exist_ok=True)

        for i, segment in enumerate(travel_story_script["segments"]):
            print(f"Creating placeholder image for segment {i+1}/{len(travel_story_script['segments'])}")
            
            # Create a colored placeholder image
            # Use a different color for each segment
            colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255), (255, 255, 200)]
            color = colors[i % len(colors)]
            
            # Create a colored image
            image = Image.new('RGB', (WIDTH, HEIGHT), color=color)
            draw = ImageDraw.Draw(image)
            
            # Add text describing what would be in the image
            text = f"Segment {i+1}\n{segment['text']}"
            
            # Try to use a nice font, fall back to default
            try:
                font = ImageFont.truetype("Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Draw text in the center
            try:
                # For newer PIL versions
                text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
            except:
                # For older PIL versions
                text_width, text_height = draw.textsize(text, font) if hasattr(draw, 'textsize') else (WIDTH//2, HEIGHT//4)
            
            position = ((WIDTH - text_width) // 2, (HEIGHT - text_height) // 2)
            
            # Draw with outline for visibility
            draw.text((position[0]-1, position[1]), text, font=font, fill=(0, 0, 0))
            draw.text((position[0]+1, position[1]), text, font=font, fill=(0, 0, 0))
            draw.text((position[0], position[1]-1), text, font=font, fill=(0, 0, 0))
            draw.text((position[0], position[1]+1), text, font=font, fill=(0, 0, 0))
            draw.text(position, text, font=font, fill=(255, 255, 255))
            
            # Save image
            image_path = f"{placeholder_dir}/segment_{i+1}.png"
            image.save(image_path, format="PNG", compress_level=0)
            segment_images.append(image_path)
            print(f"Placeholder image for segment {i+1} saved to {image_path}")

    # Step 5: Generate dynamic video frames with motion effects
    print("\nStep 5: Generating dynamic video frames with realistic camera motion and audio sync...")

    # Process each segment to create dynamic motion effects
    for i, image_path in enumerate(segment_images):
        segment_frames_dir = f"{base_dir}/3_frames/segment_{i+1}"
        os.makedirs(segment_frames_dir, exist_ok=True)

        # Get segment details
        segment = travel_story_script["segments"][i]
        
        # Use the audio duration if available, otherwise use the configured duration
        segment_duration = segment.get("audio_duration", segment["duration_seconds"])
        zoom_direction = segment.get("zoom_direction", "none")
        emoji = segment.get("emoji", None)
        
        # Create motion frames
        create_motion_frames(
            image_path, 
            segment_frames_dir, 
            segment_duration,
            zoom_direction,
            segment.get("text", ""),
            segment.get("text_overlay", False),
            segment.get("text_style", "modern"),
            emoji
        )

    # Step 6: Create advanced transitions between segments
    print("\nStep 6: Creating advanced transitions between segments...")

    # Create transition frames for each pair of segments
    for i in range(len(travel_story_script["segments"]) - 1):
        from_segment = i + 1
        to_segment = i + 2
        transition_type = travel_story_script["segments"][i]["transition"]

        create_transition_frames(
            base_dir,
            from_segment,
            to_segment,
            transition_type,
            travel_story_script["segments"][i].get("audio_duration", 
            travel_story_script["segments"][i]["duration_seconds"]),
            WIDTH,
            HEIGHT
        )

    # Step 7: Compile all frames into final video sequence
    print("\nStep 7: Compiling all frames into final video with audio...")

    # Create a directory to hold all frames in sequence
    final_frames_dir = f"{base_dir}/5_final/frames"
    os.makedirs(final_frames_dir, exist_ok=True)

    # Compile frames and track audio segments
    frame_count, audio_segments, current_time = compile_frames(
        base_dir, 
        final_frames_dir, 
        travel_story_script
    )

    print(f"Compiled {frame_count} frames for final video")

    # Step 8: Create final audio track by concatenating segment audio files
    print("\nStep 8: Creating final audio track...")
    final_audio_path = f"{base_dir}/6_audio/final_audio.mp3"
    final_audio_path = create_audio_track(audio_segments, current_time, final_audio_path)

    # Step 9: Create video from frames using FFMPEG and add audio
    print("\nStep 9: Creating final video with audio...")

    current_dir = os.getcwd()
    final_video_no_audio = f"{current_dir}/travel_story_final_no_audio.mp4"
    final_video = f"{current_dir}/travel_story_final_with_audio.mp4"  # Final output with audio

    success = create_final_video(
        final_frames_dir, 
        final_video_no_audio, 
        final_video, 
        final_audio_path
    )

    if success:
        print("\nComplete Instagram Reels-style travel story video generation process finished!")
        print(f"Final video available at: {final_video}")
        print("\nThis video features:")
        print("- Authentic travel storytelling narrative")
        print("- Enhanced narration")
        print("- Realistic camera movements mimicking handheld footage")
        print("- Professional text animations with timing")
        print("- Cinematic transitions between scenes")
        print("- Approximately 30-second length optimized for social sharing")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()

    # Process each segment to create dynamic motion effects
    for i, image_path in enumerate(segment_images):
        segment_frames_dir = f"{base_dir}/3_frames/segment_{i+1}"
        os.makedirs(segment_frames_dir, exist_ok=True)

        # Get segment details
        segment = travel_story_script["segments"][i]
        
        # Use the audio duration if available, otherwise use the configured duration
        segment_duration = segment.get("audio_duration", segment["duration_seconds"])
        zoom_direction = segment.get("zoom_direction", "none")
        emoji = segment.get("emoji", None)
        
        # Create motion frames
        create_motion_frames(
            image_path, 
            segment_frames_dir, 
            segment_duration,
            zoom_direction,
            segment.get("text", ""),
            segment.get("text_overlay", False),
            segment.get("text_style", "modern"),
            emoji
        )

    # Step 6: Create advanced transitions between segments
    print("\nStep 6: Creating advanced transitions between segments...")

    # Create transition frames for each pair of segments
    for i in range(len(travel_story_script["segments"]) - 1):
        from_segment = i + 1
        to_segment = i + 2
        transition_type = travel_story_script["segments"][i]["transition"]

        create_transition_frames(
            base_dir,
            from_segment,
            to_segment,
            transition_type,
            travel_story_script["segments"][i].get("audio_duration", 
            travel_story_script["segments"][i]["duration_seconds"]),
            WIDTH,
            HEIGHT
        )

    # Step 7: Compile all frames into final video sequence
    print("\nStep 7: Compiling all frames into final video with audio...")

    # Create a directory to hold all frames in sequence
    final_frames_dir = f"{base_dir}/5_final/frames"
    os.makedirs(final_frames_dir, exist_ok=True)

    # Compile frames and track audio segments
    frame_count, audio_segments, current_time = compile_frames(
        base_dir, 
        final_frames_dir, 
        travel_story_script
    )

    print(f"Compiled {frame_count} frames for final video")

    # Step 8: Create final audio track by concatenating segment audio files
    print("\nStep 8: Creating final audio track...")
    final_audio_path = f"{base_dir}/6_audio/final_audio.mp3"
    final_audio_path = create_audio_track(audio_segments, current_time, final_audio_path)

    # Step 9: Create video from frames using FFMPEG and add audio
    print("\nStep 9: Creating final video with audio...")

    current_dir = os.getcwd()
    final_video_no_audio = f"{current_dir}/travel_story_final_no_audio.mp4"
    final_video = f"{current_dir}/travel_story_final_with_audio.mp4"  # Final output with audio

    success = create_final_video(
        final_frames_dir, 
        final_video_no_audio, 
        final_video, 
        final_audio_path
    )

    if success:
        print("\nComplete Instagram Reels-style travel story video generation process finished!")
        print(f"Final video available at: {final_video}")
        print("\nThis video features:")
        print("- Authentic travel storytelling narrative")
        print("- Enhanced narration")
        print("- Realistic camera movements mimicking handheld footage")
        print("- Professional text animations with timing")
        print("- Cinematic transitions between scenes")
        print("- Approximately 30-second length optimized for social sharing")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()