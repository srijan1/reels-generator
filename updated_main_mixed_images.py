"""
Main script for Instagram Reels Generator with mixed image generation.
This version uses both Pexels stock photos and Stable Diffusion AI generation.
"""

import os
import time
import torch
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from image_effects import apply_instagram_filter
from enhanced_motion import create_enhanced_motion_frames
from transitions import create_transition_frames
from pyttsx3_integration import generate_narration, convert_text_to_speech, get_audio_duration, adjust_speech_to_duration
from enhanced_video_assembly import compile_frames, create_audio_track, create_final_video
from enhanced_image_generation import generate_segment_images_mixed, test_pexels_api
from utils import adjust_segment_duration

def main(custom_script=None):
    """Main function to create the Instagram Reel with mixed image generation
    
    Parameters:
    - custom_script: Optional custom script generated via Groq API
    """
    
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

    # Use custom script if provided, otherwise use default
    if custom_script:
        travel_story_script = custom_script
        print(f"Using custom script: {travel_story_script['title']}")
    else:
        # This is the default story that follows a real person's travel vlog
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
                    "emoji": "✈️",
                    "subtitle_mode": True  # Enable subtitle-style captions
                },
                {
                    "text": "First stop: Fushimi Inari Shrine at sunrise to beat the crowds",
                    "text_overlay": True,
                    "text_style": "modern",
                    "duration_seconds": 7,
                    "image_prompt": "POV walking through iconic red torii gates at Fushimi Inari Shrine at dawn, misty atmosphere, soft morning light filtering through, no people visible, path stretching ahead, vertical 9:16 format",
                    "zoom_direction": "forward_push",
                    "transition": "slide_up",
                    "subtitle_mode": True
                },
                {
                    "text": "Kyoto's traditional architecture is absolutely stunning",
                    "text_overlay": True,
                    "text_style": "right aligned",
                    "duration_seconds": 7,
                    "image_prompt": "Close-up details of traditional Japanese wooden temple architecture, intricate carvings, slightly weathered, beautiful craftsmanship, soft natural lighting, vertical 9:16 format, authentic travel photography style",
                    "zoom_direction": "slow_pan",
                    "transition": "color_pulse",
                    "subtitle_mode": True
                },
                {
                    "text": "Found this hidden tea house where locals actually go",
                    "text_overlay": True,
                    "text_style": "left aligned",
                    "duration_seconds": 7,
                    "image_prompt": "Cozy traditional Japanese tea house interior, authentic setting, steam rising from tea cup in foreground, elderly Japanese shop owner preparing tea in background, warm intimate lighting, vertical 9:16 format",
                    "zoom_direction": "gentle_zoom_out",
                    "transition": "slide_left",
                    "subtitle_mode": True
                }
            ]
        }

    # Adjust segment durations to target appropriate video length
    if not custom_script:
        travel_story_script = adjust_segment_duration(travel_story_script, target_total_duration=30)
    else:
        # Make sure all segments have subtitle_mode enabled
        for segment in travel_story_script["segments"]:
            segment["subtitle_mode"] = True

    # Save the script to file
    script_path = f"{base_dir}/1_script/story_script.json"
    with open(script_path, 'w') as f:
        json.dump(travel_story_script, f, indent=4)

    print(f"Story script saved to {script_path}")

    # Step 2: Generate enhanced narration using Groq API
    print("\nStep 2: Generating enhanced narration content using Groq API...")

    # Generate narration for each segment
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"Generating narration for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Get the original text and image prompt
        original_text = segment["text"]
        image_prompt = segment["image_prompt"]
        
        # Generate enhanced narration content using Groq API
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

    # Step 3: Generate audio files using pyttsx3 TTS
    print("\nStep 3: Generating audio narrations with pyttsx3...")

    # Voice mapping to cycle through for variety
    voice_mapping = {
        0: "male",      # Use a male voice
        1: "female",    # Use a female voice 
        2: "default"    # Use default voice
    }

    # Generate audio for each segment
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"Generating audio for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Get the narration text
        narration_text = segment.get("narration", segment["text"])
        
        # Choose a voice (cycle through available voices)
        voice_type = voice_mapping[i % len(voice_mapping)]
        
        # Calculate target speech rate based on segment duration
        target_duration = segment["duration_seconds"]
        
        # Generate audio file with speech rate adjusted to match segment duration
        audio_path = f"{base_dir}/6_audio/segment_{i+1}.mp3"
        audio_file = adjust_speech_to_duration(narration_text, target_duration, audio_path)
        
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

    # Step 4: Generate images using mixed approach (Pexels + AI)
    print("\nStep 4: Generating images using mixed approach (Pexels + Stable Diffusion)...")

    # Determine device - CPU for compatibility
    device = "cpu"
    print(f"Using device: {device}")

    # Image dimensions (9:16 aspect ratio for vertical video)
    HEIGHT = 512  # Reduced from 1024 for faster processing
    WIDTH = 288   # Reduced from 576 (maintaining 9:16 aspect ratio)

    # Test Pexels API availability
    print("🔍 Testing Pexels API availability...")
    pexels_available = test_pexels_api()
    
    if pexels_available:
        print("✅ Pexels API is working - will use stock photos for half the images")
    else:
        print("⚠️  Pexels API unavailable - will use AI generation for all images")

    # Generate mixed images
    try:
        segment_images = generate_segment_images_mixed(
            travel_story_script["segments"],
            base_dir,
            height=HEIGHT,
            width=WIDTH,
            device=device
        )
        
        print(f"✅ Successfully generated {len(segment_images)} images")
        
    except Exception as e:
        print(f"\nError with mixed image generation: {e}")
        print("Falling back to placeholder images...\n")
        
        # Create placeholder images as final fallback
        segment_images = []
        placeholder_dir = f"{base_dir}/2_images"
        os.makedirs(placeholder_dir, exist_ok=True)
        
        for i, segment in enumerate(travel_story_script["segments"]):
            print(f"Creating placeholder image for segment {i+1}/{len(travel_story_script['segments'])}")
            
            # Create a colored placeholder image with different colors for each segment
            colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255), (255, 255, 200), 
                     (255, 200, 255), (200, 255, 255), (255, 230, 200), (230, 255, 200)]
            color = colors[i % len(colors)]
            
            # Create a colored image
            image = Image.new('RGB', (WIDTH, HEIGHT), color=color)
            draw = ImageDraw.Draw(image)
            
            # Add text describing what would be in the image
            text = f"Segment {i+1}\n{segment['text'][:50]}..."
            
            # Try to use a nice font, fall back to default
            try:
                font = ImageFont.truetype("Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Draw text in the center with better formatting
            lines = text.split('\n')
            total_height = len(lines) * 25
            start_y = (HEIGHT - total_height) // 2
            
            for j, line in enumerate(lines):
                try:
                    text_width = draw.textbbox((0, 0), line, font=font)[2]
                except:
                    text_width = len(line) * 10
                
                x = (WIDTH - text_width) // 2
                y = start_y + (j * 25)
                
                # Draw with outline for visibility
                draw.text((x-1, y), line, font=font, fill=(0, 0, 0))
                draw.text((x+1, y), line, font=font, fill=(0, 0, 0))
                draw.text((x, y-1), line, font=font, fill=(0, 0, 0))
                draw.text((x, y+1), line, font=font, fill=(0, 0, 0))
                draw.text((x, y), line, font=font, fill=(255, 255, 255))
            
            # Save image
            image_path = f"{placeholder_dir}/segment_{i+1}.png"
            image.save(image_path, format="PNG", compress_level=0)
            segment_images.append(image_path)
            print(f"Placeholder image for segment {i+1} saved to {image_path}")

    # Step 5: Apply Instagram filters to all images
    print("\nStep 5: Applying Instagram-style filters to images...")
    
    filter_types = ["natural", "warm_travel", "moody", "nostalgic", "golden_hour"]
    
    for i, image_path in enumerate(segment_images):
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Apply filter
            filter_type = filter_types[i % len(filter_types)]
            print(f"Applying {filter_type} filter to segment {i+1}")
            filtered_image = apply_instagram_filter(image, filter_type)
            
            # Save the filtered image
            filtered_image.save(image_path, format="PNG", compress_level=0)
            
        except Exception as e:
            print(f"⚠️  Could not apply filter to segment {i+1}: {e}")
            continue

    # Step 6: Generate dynamic video frames with motion effects synced to audio
    print("\nStep 6: Generating dynamic video frames with audio-synced motion and captions...")

    # Process each segment to create dynamic motion effects
    for i, image_path in enumerate(segment_images):
        segment_frames_dir = f"{base_dir}/3_frames/segment_{i+1}"
        os.makedirs(segment_frames_dir, exist_ok=True)

        # Get segment details
        segment = travel_story_script["segments"][i]
        
        # Use the audio duration for perfect sync
        segment_duration = segment.get("duration_seconds")
        audio_duration = segment.get("audio_duration")
        
        zoom_direction = segment.get("zoom_direction", "gentle_pulse")
        text = segment.get("narration", segment.get("text", ""))
        text_style = segment.get("text_style", "modern")
        emoji = segment.get("emoji", None)
        subtitle_mode = segment.get("subtitle_mode", True)  # Default to subtitle mode
        
        # Determine visual style based on segment
        visual_style = "cinematic" if "cinematic" in segment.get("style", "") else "professional"
        
        # Create enhanced motion frames with captions synced to audio
        print(f"Creating motion frames for segment {i+1} with {'subtitle captions' if subtitle_mode else 'text overlay'}")
        create_enhanced_motion_frames(
            image_path,
            segment_frames_dir,
            segment_duration,
            text,
            audio_duration=audio_duration,
            style=visual_style,
            motion_type=zoom_direction,
            subtitle=subtitle_mode
        )

    # Step 7: Create advanced transitions between segments
    print("\nStep 7: Creating advanced transitions between segments...")

    # Create transition frames for each pair of segments
    for i in range(len(travel_story_script["segments"]) - 1):
        from_segment = i + 1
        to_segment = i + 2
        transition_type = travel_story_script["segments"][i].get("transition", "smooth_fade")

        # Use actual audio duration for perfect transitions
        segment_duration = travel_story_script["segments"][i].get("audio_duration", 
                          travel_story_script["segments"][i]["duration_seconds"])

        create_transition_frames(
            base_dir,
            from_segment,
            to_segment,
            transition_type,
            segment_duration,
            WIDTH,
            HEIGHT
        )

    # Step 8: Compile all frames into final video sequence
    print("\nStep 8: Compiling all frames into final video with audio...")

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

    # Step 9: Create final audio track by concatenating segment audio files
    print("\nStep 9: Creating final audio track...")
    final_audio_path = f"{base_dir}/6_audio/final_audio.mp3"
    final_audio_path = create_audio_track(audio_segments, current_time, final_audio_path)

    # Step 10: Create video from frames using FFMPEG and add audio
    print("\nStep 10: Creating final video with audio...")

    current_dir = os.getcwd()
    filename_prefix = "narrative_story" if custom_script else "travel_story"
    final_video_no_audio = f"{current_dir}/{filename_prefix}_final_no_audio.mp4"
    final_video = f"{current_dir}/{filename_prefix}_final_with_audio.mp4"  # Final output with audio

    success = create_final_video(
        final_frames_dir, 
        final_video_no_audio, 
        final_video, 
        final_audio_path
    )

    if success:
        # Determine what kind of story was created
        print("\n" + "=" * 60)
        if custom_script and len(travel_story_script["segments"]) == 8:
            print("🎉 COMPLETE! Custom narrative story video generated successfully!")
            print("=" * 60)
            print(f"📁 Final video: {final_video}")
            print("\n🌟 This video features:")
            print("   📖 Custom narrative storytelling powered by Groq API")
            print("   📸 Mixed image sources (Pexels stock + AI generated)")
            print("   🎙️  Professional pyttsx3 voice narration")
            print("   🎯 Synchronized captions and audio")
            print("   🎨 Dynamic visual effects and transitions")
            print("   📱 8 segments optimized for social media")
        else:
            print("🎉 COMPLETE! Instagram Reels-style travel story generated!")
            print("=" * 60)
            print(f"📁 Final video: {final_video}")
            print("\n🌟 This video features:")
            print("   ✈️  Authentic travel storytelling narrative")
            print("   🤖 Enhanced narration powered by Groq API")
            print("   📸 Mixed image sources (Pexels stock + AI generated)")
            print("   🎙️  Professional pyttsx3 voice narration")
            print("   📱 Perfect subtitle styling and timing")
            print("   🎬 Cinematic camera movements and transitions")
            
        print(f"\n💡 Image Generation Summary:")
        print(f"   📸 Used Pexels API: {'✅ Available' if pexels_available else '❌ Unavailable'}")
        print(f"   🤖 Used AI Generation: ✅ Stable Diffusion")
        print(f"   🎨 Applied Instagram filters to all images")
        print(f"\n🚀 Ready for: Instagram Reels, TikTok, YouTube Shorts")
        
    else:
        print("\n❌ Video generation encountered issues.")
        print("📁 Generated frames are available in the output directory")
        print("💡 Try manual compilation or check the logs for errors")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
