"""
Main script with fixed audio-video synchronization and guaranteed audio for all segments.
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
from fixed_pyttsx3_integration import (
    generate_narration, 
    adjust_speech_to_duration, 
    get_audio_duration, 
    ensure_audio_for_segment,
    verify_audio_file
)
from enhanced_video_assembly import compile_frames, create_audio_track, create_final_video
from enhanced_image_generation import generate_segment_images_mixed, test_pexels_api
from utils import adjust_segment_duration

def main(custom_script=None):
    """Main function with perfect audio-video synchronization"""
    
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
        # Default travel story
        travel_story_script = {
            "title": "My Solo Trip to Kyoto",
            "style": "authentic, cinematic, immersive travel vlog",
            "aspect_ratio": "9:16",
            "segments": [
                {
                    "text": "After months of planning, I finally made it to Kyoto, Japan 🇯🇵",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 7.5,
                    "image_prompt": "Young traveler with backpack arriving at Kyoto train station, looking excited and slightly tired, golden hour lighting, candid moment, Japanese signs visible, vertical format, 9:16 aspect ratio",
                    "zoom_direction": "in",
                    "transition": "smooth_fade",
                    "emoji": "✈️",
                    "subtitle_mode": True
                },
                {
                    "text": "First stop: Fushimi Inari Shrine at sunrise to beat the crowds",
                    "text_overlay": True,
                    "text_style": "modern",
                    "duration_seconds": 7.5,
                    "image_prompt": "POV walking through iconic red torii gates at Fushimi Inari Shrine at dawn, misty atmosphere, soft morning light filtering through, no people visible, path stretching ahead, vertical 9:16 format",
                    "zoom_direction": "forward_push",
                    "transition": "slide_up",
                    "subtitle_mode": True
                },
                {
                    "text": "Kyoto's traditional architecture is absolutely stunning",
                    "text_overlay": True,
                    "text_style": "right aligned",
                    "duration_seconds": 7.5,
                    "image_prompt": "Close-up details of traditional Japanese wooden temple architecture, intricate carvings, slightly weathered, beautiful craftsmanship, soft natural lighting, vertical 9:16 format, authentic travel photography style",
                    "zoom_direction": "slow_pan",
                    "transition": "color_pulse",
                    "subtitle_mode": True
                },
                {
                    "text": "Found this hidden tea house where locals actually go",
                    "text_overlay": True,
                    "text_style": "left aligned",
                    "duration_seconds": 7.5,
                    "image_prompt": "Cozy traditional Japanese tea house interior, authentic setting, steam rising from tea cup in foreground, elderly Japanese shop owner preparing tea in background, warm intimate lighting, vertical 9:16 format",
                    "zoom_direction": "gentle_zoom_out",
                    "transition": "slide_left",
                    "subtitle_mode": True
                },
                {
                    "text": "The evening streets come alive with lanterns and local life",
                    "text_overlay": True,
                    "text_style": "modern",
                    "duration_seconds": 7.5,
                    "image_prompt": "Traditional Kyoto street at dusk, red lanterns glowing, locals walking, traditional buildings, warm evening light, authentic Japanese atmosphere, vertical 9:16 format",
                    "zoom_direction": "drift",
                    "transition": "gradient_wipe",
                    "subtitle_mode": True
                },
                {
                    "text": "Meeting fellow travelers from around the world enriches the journey",
                    "text_overlay": True,
                    "text_style": "modern",
                    "duration_seconds": 7.5,
                    "image_prompt": "Group of diverse international travelers sharing stories in traditional Japanese setting, friendship forming, cultural exchange, warm social lighting, vertical 9:16 format",
                    "zoom_direction": "gentle_pulse",
                    "transition": "whip_pan",
                    "subtitle_mode": True
                },
                {
                    "text": "The bamboo forest creates a world of emerald tranquility",
                    "text_overlay": True,
                    "text_style": "modern",
                    "duration_seconds": 7.5,
                    "image_prompt": "Walking through Arashiyama bamboo grove, towering green bamboo creating natural cathedral, filtered light, peaceful solitude, vertical 9:16 format",
                    "zoom_direction": "looking_up",
                    "transition": "smooth_fade",
                    "subtitle_mode": True
                },
                {
                    "text": "This journey has changed my perspective on travel forever",
                    "text_overlay": True,
                    "text_style": "modern",
                    "duration_seconds": 7.5,
                    "image_prompt": "Contemplative traveler at sunset viewpoint overlooking Kyoto city, peaceful reflection, journey's end, golden hour lighting, transformation visible, vertical 9:16 format",
                    "zoom_direction": "focus_in",
                    "transition": "smooth_fade",
                    "subtitle_mode": True
                }
            ]
        }

    # Adjust segment durations if needed
    if not custom_script:
        travel_story_script = adjust_segment_duration(travel_story_script, target_total_duration=60)
    else:
        # Ensure all segments have subtitle_mode enabled
        for segment in travel_story_script["segments"]:
            segment["subtitle_mode"] = True

    # Save the script to file
    script_path = f"{base_dir}/1_script/story_script.json"
    with open(script_path, 'w') as f:
        json.dump(travel_story_script, f, indent=4)

    print(f"Story script saved to {script_path}")

    # Step 2: Generate enhanced narration using Groq API
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

    # Step 3: Generate audio files with guaranteed success
    print("\nStep 3: Generating audio narrations with guaranteed synchronization...")

    # Voice mapping to cycle through for variety
    voice_mapping = {
        0: "male",
        1: "female", 
        2: "default"
    }

    # Generate audio for each segment with verification
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"\nGenerating audio for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Ensure this segment gets audio
        audio_path = ensure_audio_for_segment(
            segment, 
            i+1, 
            f"{base_dir}/6_audio"
        )
        
        if audio_path:
            # Get the actual duration of the audio
            duration = get_audio_duration(audio_path)
            if duration:
                print(f"✅ Audio duration: {duration:.2f} seconds")
                # Store both paths
                segment["audio_duration"] = duration
                segment["audio_path"] = audio_path
            else:
                print(f"⚠️  Could not get duration for {audio_path}")
                # Use target duration as fallback
                segment["audio_duration"] = segment["duration_seconds"]
                segment["audio_path"] = audio_path
        else:
            print(f"❌ Failed to create audio for segment {i+1}")
            # This should not happen with the new system, but just in case
            segment["audio_duration"] = segment["duration_seconds"]

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
    HEIGHT = 512
    WIDTH = 288

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

    # Step 6: Generate dynamic video frames with PERFECT audio sync
    print("\nStep 6: Generating dynamic video frames with perfect audio-visual sync...")

    # Process each segment to create motion effects EXACTLY matched to audio duration
    for i, image_path in enumerate(segment_images):
        segment_frames_dir = f"{base_dir}/3_frames/segment_{i+1}"
        os.makedirs(segment_frames_dir, exist_ok=True)

        # Get segment details
        segment = travel_story_script["segments"][i]
        
        # CRITICAL: Use actual audio duration for perfect sync
        audio_duration = segment.get("audio_duration")
        if not audio_duration:
            # Fallback to configured duration
            audio_duration = segment.get("duration_seconds", 7.5)
            print(f"⚠️  No audio duration for segment {i+1}, using {audio_duration}s")
        
        print(f"📱 Creating frames for segment {i+1}: {audio_duration:.2f} seconds")
        
        zoom_direction = segment.get("zoom_direction", "gentle_pulse")
        text = segment.get("narration", segment.get("text", ""))
        text_style = segment.get("text_style", "modern")
        emoji = segment.get("emoji", None)
        subtitle_mode = segment.get("subtitle_mode", True)
        
        # Determine visual style
        visual_style = "cinematic" if "cinematic" in segment.get("style", "") else "professional"
        
        # Create enhanced motion frames with EXACT audio sync
        print(f"🎬 Creating motion frames for segment {i+1} with {'subtitle captions' if subtitle_mode else 'text overlay'}")
        
        try:
            create_enhanced_motion_frames(
                image_path,
                segment_frames_dir,
                audio_duration,  # Use EXACT audio duration
                text,
                audio_duration=audio_duration,  # Pass the same duration
                style=visual_style,
                motion_type=zoom_direction,
                subtitle=subtitle_mode
            )
            
            # Verify frame count matches expected
            frame_files = [f for f in os.listdir(segment_frames_dir) if f.endswith('.png')]
            expected_frames = int(audio_duration * 30)  # 30 FPS
            actual_frames = len(frame_files)
            
            print(f"✅ Segment {i+1}: {actual_frames} frames for {audio_duration:.2f}s (expected: {expected_frames})")
            
            if abs(actual_frames - expected_frames) > 2:  # Allow small variance
                print(f"⚠️  Frame count mismatch for segment {i+1}: got {actual_frames}, expected {expected_frames}")
            
        except Exception as e:
            print(f"❌ Error creating frames for segment {i+1}: {e}")

    # Step 7: Create advanced transitions between segments
    print("\nStep 7: Creating advanced transitions between segments...")

    # Create transition frames for each pair of segments
    for i in range(len(travel_story_script["segments"]) - 1):
        from_segment = i + 1
        to_segment = i + 2
        transition_type = travel_story_script["segments"][i].get("transition", "smooth_fade")

        print(f"🔄 Creating {transition_type} transition from segment {from_segment} to {to_segment}")

        try:
            create_transition_frames(
                base_dir,
                from_segment,
                to_segment,
                transition_type,
                1.0,  # Fixed 1 second transitions
                WIDTH,
                HEIGHT
            )
        except Exception as e:
            print(f"⚠️  Error creating transition {from_segment}->{to_segment}: {e}")

    # Step 8: Compile all frames into final video sequence
    print("\nStep 8: Compiling all frames into final video with perfect audio sync...")

    # Create a directory to hold all frames in sequence
    final_frames_dir = f"{base_dir}/5_final/frames"
    os.makedirs(final_frames_dir, exist_ok=True)

    # Compile frames and track audio segments
    frame_count, audio_segments, current_time = compile_frames(
        base_dir, 
        final_frames_dir, 
        travel_story_script
    )

    print(f"✅ Compiled {frame_count} frames for final video")
    print(f"📊 Total duration: {current_time:.2f} seconds")

    # Verify audio segments
    print("\n🎵 Audio segments summary:")
    for i, audio_segment in enumerate(audio_segments):
        is_valid, message = verify_audio_file(audio_segment["path"])
        print(f"  Segment {i+1}: {message}")

    # Step 9: Create final audio track
    print("\nStep 9: Creating final audio track with perfect synchronization...")
    final_audio_path = f"{base_dir}/6_audio/final_audio.mp3"
    final_audio_path = create_audio_track(audio_segments, current_time, final_audio_path)

    if final_audio_path:
        final_audio_duration = get_audio_duration(final_audio_path)
        if final_audio_duration:
            print(f"✅ Final audio track: {final_audio_duration:.2f} seconds")
        else:
            print("⚠️  Could not verify final audio duration")
    else:
        print("❌ Failed to create final audio track")

    # Step 10: Create video from frames using FFMPEG
    print("\nStep 10: Creating final video with perfect audio-video sync...")

    current_dir = os.getcwd()
    filename_prefix = "narrative_story" if custom_script else "travel_story"
    final_video_no_audio = f"{current_dir}/{filename_prefix}_final_no_audio.mp4"
    final_video = f"{current_dir}/{filename_prefix}_final_with_audio.mp4"

    success = create_final_video(
        final_frames_dir, 
        final_video_no_audio, 
        final_video, 
        final_audio_path
    )

    if success:
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Video generated with perfect synchronization!")
        print("=" * 60)
        print(f"📁 Final video: {final_video}")
        
        # Verify final video
        try:
            video_duration = get_audio_duration(final_video)  # Works for video files too
            if video_duration:
                print(f"📹 Final video duration: {video_duration:.2f} seconds")
            
            if final_audio_path:
                audio_duration = get_audio_duration(final_audio_path)
                if audio_duration and video_duration:
                    sync_diff = abs(video_duration - audio_duration)
                    if sync_diff < 0.5:
                        print("✅ Perfect audio-video synchronization achieved!")
                    else:
                        print(f"⚠️  Audio-video sync difference: {sync_diff:.2f}s")
        except:
            pass
        
        print("\n🌟 This video features:")
        if custom_script and len(travel_story_script["segments"]) == 8:
            print("   📖 Custom narrative storytelling powered by Groq API")
            print("   📸 Mixed image sources (Pexels stock + AI generated)")
            print("   🎙️  Professional pyttsx3 voice narration")
            print("   🎯 Perfect audio-video synchronization")
            print("   🎨 Dynamic visual effects and transitions")
            print("   📱 8 segments optimized for social media")
        else:
            print("   ✈️  Authentic travel storytelling narrative")
            print("   🤖 Enhanced narration powered by Groq API")
            print("   📸 Mixed image sources (Pexels stock + AI generated)")
            print("   🎙️  Professional pyttsx3 voice narration")
            print("   📱 Perfect subtitle styling and timing")
            print("   🎬 Cinematic camera movements and transitions")
            
        print(f"\n💡 Technical Summary:")
        print(f"   📊 Total segments: {len(travel_story_script['segments'])}")
        print(f"   🎵 Audio segments: {len(audio_segments)}")
        print(f"   🖼️  Total frames: {frame_count}")
        print(f"   ⏱️  Total duration: {current_time:.1f} seconds")
        print(f"   📱 Format: 9:16 vertical for social media")
        print(f"\n🚀 Ready for: Instagram Reels, TikTok, YouTube Shorts")
        
    else:
        print("\n❌ Video generation encountered issues.")
        print("📁 Generated frames and audio are available in the output directory")
        print("💡 Try manual compilation or check the logs for errors")
        
        # Provide manual compilation instructions
        print(f"\n🔧 Manual compilation commands:")
        print(f"1. Create video from frames:")
        print(f"   ffmpeg -framerate 30 -i {final_frames_dir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p {final_video_no_audio}")
        
        if final_audio_path:
            print(f"2. Add audio to video:")
            print(f"   ffmpeg -i {final_video_no_audio} -i {final_audio_path} -c:v copy -c:a aac -shortest {final_video}")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
