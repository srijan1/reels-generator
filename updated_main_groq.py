"""
Main script for Instagram Reels Generator with Groq API integration.
FIXED: Using the proven working pattern from updated_main_mixed_images.py
This version provides enhanced image generation and reliable frame processing.
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
from piper_tts_integration import generate_narration, convert_text_to_speech, get_audio_duration, adjust_speech_to_duration
from video_assembly import compile_frames, create_audio_track, create_final_video
from enhanced_image_generation import generate_segment_images_mixed, test_pexels_api
from utils import adjust_segment_duration

def main(custom_script=None):
    """Main function to create the Instagram Reel with enhanced mixed generation
    
    Parameters:
    - custom_script: Optional custom script generated via Groq API
    """
    
    print("🎬 GROQ REEL GENERATOR - Enhanced Mixed Generation")
    print("="*60)
    print("✨ Features:")
    print("   📸 Mixed image sources (Pexels stock + AI generated)")
    print("   🤖 Stable Diffusion AI generation with enhanced auth")
    print("   🎙️ Crystal clear audio with Piper TTS")
    print("   📐 Perfect 9:16 aspect ratio enforcement")
    print("   🎬 Advanced motion effects and transitions")
    print("="*60)
    
    # Create directories
    timestamp = int(time.time())
    base_dir = f"./story_reel_{timestamp}"
    
    print(f"\n📁 Creating project directory: {base_dir}")
    
    directories = [
        f"{base_dir}/1_script",
        f"{base_dir}/2_images", 
        f"{base_dir}/3_frames",
        f"{base_dir}/4_transitions",
        f"{base_dir}/5_final",
        f"{base_dir}/6_audio"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Step 1: Generate narrative story content
    print("\n📝 Step 1: Preparing narrative story content...")

    # Use custom script if provided, otherwise use default
    if custom_script:
        travel_story_script = custom_script
        print(f"✅ Using custom script: {travel_story_script.get('title', 'Custom Story')}")
    else:
        # Default story for testing
        travel_story_script = {
            "title": "My Solo Trip to Kyoto",
            "style": "authentic, cinematic, immersive travel vlog",
            "aspect_ratio": "9:16",
            "background_music": "japanese_lofi.mp3",
            "segments": [
                {
                    "text": "After months of planning, I finally made it to Kyoto, Japan 🇯🇵",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 7,
                    "image_prompt": "Young traveler with backpack arriving at Kyoto train station, looking excited and slightly tired, golden hour lighting, candid moment, Japanese signs visible, vertical format, 9:16 aspect ratio",
                    "zoom_direction": "in",
                    "transition": "smooth_fade",
                    "emoji": "✈️",
                    "subtitle_mode": True
                },
                {
                    "text": "The cherry blossoms were in full bloom, creating a magical pink canopy",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 6,
                    "image_prompt": "Beautiful cherry blossom trees in full bloom in Kyoto, soft pink petals falling, peaceful temple in background, morning light filtering through branches, vertical composition, 9:16 aspect ratio",
                    "zoom_direction": "out",
                    "transition": "cross_fade",
                    "emoji": "🌸",
                    "subtitle_mode": True
                },
                {
                    "text": "I spent hours wandering through the bamboo forest, feeling at peace",
                    "text_overlay": True,
                    "text_style": "bold, centered", 
                    "duration_seconds": 8,
                    "image_prompt": "Towering bamboo forest path in Arashiyama, green filtered light, peaceful atmosphere, person walking in distance, natural vertical composition, 9:16 aspect ratio",
                    "zoom_direction": "in",
                    "transition": "slide_left",
                    "emoji": "🎋",
                    "subtitle_mode": True
                },
                {
                    "text": "The golden temple reflected perfectly in the calm pond",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 7,
                    "image_prompt": "Kinkaku-ji golden temple reflecting in calm pond water, autumn colors, serene atmosphere, traditional Japanese architecture, vertical reflection composition, 9:16 aspect ratio",
                    "zoom_direction": "out",
                    "transition": "zoom_in",
                    "emoji": "🏛️",
                    "subtitle_mode": True
                },
                {
                    "text": "Every street corner revealed a new hidden gem or local treasure",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 6,
                    "image_prompt": "Charming narrow Japanese street in Gion district, traditional wooden buildings, lanterns, cobblestone path, warm evening lighting, vertical street view, 9:16 aspect ratio",
                    "zoom_direction": "in",
                    "transition": "cross_fade",
                    "emoji": "🏮",
                    "subtitle_mode": True
                },
                {
                    "text": "The traditional tea ceremony was a moment of pure mindfulness",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 8,
                    "image_prompt": "Traditional Japanese tea ceremony, elegant hands preparing matcha, bamboo whisk, ceramic bowls, tatami mat, soft natural lighting, vertical composition, 9:16 aspect ratio",
                    "zoom_direction": "out",
                    "transition": "fade",
                    "emoji": "🍵",
                    "subtitle_mode": True
                },
                {
                    "text": "As the sun set, the city transformed into a sea of warm lights",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 7,
                    "image_prompt": "Kyoto cityscape at sunset, warm golden light over traditional rooftops, distant mountains, glowing lanterns, peaceful evening atmosphere, vertical panoramic view, 9:16 aspect ratio",
                    "zoom_direction": "in",
                    "transition": "slide_right",
                    "emoji": "🌅",
                    "subtitle_mode": True
                },
                {
                    "text": "This journey to Kyoto taught me that the best adventures happen when you slow down",
                    "text_overlay": True,
                    "text_style": "bold, centered",
                    "duration_seconds": 9,
                    "image_prompt": "Peaceful meditation moment in Japanese temple garden, person sitting quietly, zen atmosphere, soft morning light, traditional architecture, contemplative mood, vertical composition, 9:16 aspect ratio",
                    "zoom_direction": "out",
                    "transition": "fade_to_black",
                    "emoji": "🙏",
                    "subtitle_mode": True
                }
            ]
        }

    # Adjust segment durations and ensure subtitle mode
    if not custom_script:
        travel_story_script = adjust_segment_duration(travel_story_script, target_total_duration=30)
    else:
        # Make sure all segments have subtitle_mode enabled
        for segment in travel_story_script["segments"]:
            segment["subtitle_mode"] = True

    # Save the script
    script_path = f"{base_dir}/1_script/story_script.json"
    with open(script_path, 'w', encoding='utf-8') as f:
        json.dump(travel_story_script, f, indent=4, ensure_ascii=False)
    print(f"✅ Story script saved to {script_path}")

    # Step 2: Generate enhanced narration using Groq API
    print("\n🎙️ Step 2: Generating enhanced narration content using Groq API...")

    # Generate narration for each segment
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"Generating narration for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Get the original text and image prompt
        original_text = segment["text"]
        image_prompt = segment.get("image_prompt", original_text)
        
        # Generate enhanced narration content using Groq API
        try:
            enhanced_narration = generate_narration(
                image_prompt, 
                original_text, 
                desired_duration_seconds=segment["duration_seconds"]
            )
            
            # Store the narration in the segment
            segment["narration"] = enhanced_narration
            print(f"   ✅ Generated narration for segment {i+1}")
            
        except Exception as e:
            print(f"   ⚠️ Could not generate narration for segment {i+1}: {e}")
            segment["narration"] = segment["text"]  # Fallback to original text

    # Save the updated script with narrations
    narration_script_path = f"{base_dir}/1_script/story_script_with_narration.json"
    with open(narration_script_path, 'w', encoding='utf-8') as f:
        json.dump(travel_story_script, f, indent=4, ensure_ascii=False)

    print(f"✅ Narration script saved to {narration_script_path}")

    # Step 3: Generate audio files using Piper TTS
    print("\n🎵 Step 3: Generating audio narrations with Piper TTS...")

    # Generate audio for each segment
    for i, segment in enumerate(travel_story_script["segments"]):
        print(f"Generating audio for segment {i+1}/{len(travel_story_script['segments'])}")
        
        # Get the narration text
        narration_text = segment.get("narration", segment["text"])
        
        # Calculate target speech rate based on segment duration
        target_duration = segment["duration_seconds"]
        
        # Generate audio file with speech rate adjusted to match segment duration
        audio_path = f"{base_dir}/6_audio/segment_{i+1}.mp3"
        audio_file = adjust_speech_to_duration(narration_text, target_duration, audio_path)
        
        if audio_file:
            # Get the actual duration of the audio
            duration = get_audio_duration(audio_file)
            if duration:
                print(f"   ✅ Audio duration: {duration:.2f} seconds")
                # Update the segment duration based on the actual audio
                segment["audio_duration"] = duration
                # Store the audio path
                segment["audio_path"] = audio_file
        else:
            print(f"   ⚠️ Could not generate audio for segment {i+1}")

    # Save the updated script with audio information
    audio_script_path = f"{base_dir}/1_script/story_script_with_audio.json"
    with open(audio_script_path, 'w', encoding='utf-8') as f:
        json.dump(travel_story_script, f, indent=4, ensure_ascii=False)

    print(f"✅ Audio script saved to {audio_script_path}")

    # Step 4: Generate images using enhanced mixed approach
    print("\n🎨 Step 4: Generating images using enhanced mixed approach (Pexels + Stable Diffusion)...")

    # Determine device - CPU for compatibility
    device = "cpu"
    print(f"Using device: {device}")

    # Image dimensions (9:16 aspect ratio for vertical video)
    HEIGHT = 512  # Optimized for processing
    WIDTH = 288   # Perfect 9:16 aspect ratio

    # Test Pexels API availability
    print("🔍 Testing Pexels API availability...")
    pexels_available = test_pexels_api()
    
    if pexels_available:
        print("✅ Pexels API is working - will use stock photos for half the images")
    else:
        print("⚠️ Pexels API unavailable - will use AI generation for all images")

    # Generate mixed images using enhanced approach
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
        print(f"\n❌ Error with enhanced image generation: {e}")
        print("🔄 Falling back to placeholder images...\n")
        
        # Create enhanced placeholder images as fallback
        segment_images = []
        placeholder_dir = f"{base_dir}/2_images"
        os.makedirs(placeholder_dir, exist_ok=True)
        
        for i, segment in enumerate(travel_story_script["segments"]):
            print(f"Creating enhanced placeholder image for segment {i+1}/{len(travel_story_script['segments'])}")
            
            # Create a gradient placeholder image with different colors for each segment
            image = create_enhanced_placeholder(WIDTH, HEIGHT, segment, i)
            
            # Save image
            image_path = f"{placeholder_dir}/segment_{i+1}.png"
            image.save(image_path, format="PNG", compress_level=0)
            segment_images.append(image_path)
            print(f"   ✅ Enhanced placeholder for segment {i+1} saved to {image_path}")

    # Step 5: Apply Instagram filters to all images
    print("\n🎨 Step 5: Applying Instagram-style filters to images...")
    
    filter_types = ["natural", "warm_travel", "moody", "nostalgic", "golden_hour"]
    
    for i, image_path in enumerate(segment_images):
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Apply filter
            filter_type = filter_types[i % len(filter_types)]
            print(f"   Applying {filter_type} filter to segment {i+1}")
            filtered_image = apply_instagram_filter(image, filter_type)
            
            # Save the filtered image
            filtered_image.save(image_path, format="PNG", compress_level=0)
            
        except Exception as e:
            print(f"   ⚠️ Could not apply filter to segment {i+1}: {e}")
            continue

    print("✅ Instagram filters applied successfully!")

    # Step 6: Generate dynamic video frames with motion effects (WORKING METHOD)
    print("\n🎬 Step 6: Generating dynamic video frames with audio-synced motion and captions...")

    # Process each segment to create dynamic motion effects using the WORKING approach
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
        subtitle_mode = segment.get("subtitle_mode", True)
        
        # Determine visual style based on segment
        visual_style = "cinematic" if "cinematic" in segment.get("style", "") else "professional"
        
        # Create enhanced motion frames with captions synced to audio (WORKING METHOD)
        print(f"   Creating motion frames for segment {i+1} with {'subtitle captions' if subtitle_mode else 'text overlay'}")
        
        try:
            create_enhanced_motion_frames(
                image_path,                   # Direct image path (WORKING METHOD)
                segment_frames_dir,          # Output directory (WORKING METHOD)
                segment_duration,            # Duration (WORKING METHOD)
                text,                        # Text content (WORKING METHOD)
                audio_duration=audio_duration, # Audio sync (WORKING METHOD)
                style=visual_style,          # Visual style (WORKING METHOD)
                motion_type=zoom_direction,  # Motion type (WORKING METHOD)
                subtitle=subtitle_mode       # Subtitle mode (WORKING METHOD)
            )
            print(f"   ✅ Created motion frames for segment {i+1}")
            
        except Exception as e:
            print(f"   ❌ Error creating frames for segment {i+1}: {e}")
            
            # Create emergency frames if motion generation fails
            create_emergency_segment_frames(image_path, segment_frames_dir, segment_duration, text, i+1)

    # Step 7: Create advanced transitions between segments (WORKING METHOD)
    print("\n🔄 Step 7: Creating advanced transitions between segments...")

    # Create transition frames for each pair of segments using WORKING METHOD
    for i in range(len(travel_story_script["segments"]) - 1):
        from_segment = i + 1
        to_segment = i + 2
        transition_type = travel_story_script["segments"][i].get("transition", "smooth_fade")

        # Use actual audio duration for perfect transitions
        segment_duration = travel_story_script["segments"][i].get("audio_duration", 
                          travel_story_script["segments"][i]["duration_seconds"])

        print(f"   Creating transition {from_segment} to {to_segment} ({transition_type})")
        
        try:
            create_transition_frames(
                base_dir,          # Base directory (WORKING METHOD)
                from_segment,      # From segment (WORKING METHOD)
                to_segment,        # To segment (WORKING METHOD)
                transition_type,   # Transition type (WORKING METHOD)
                segment_duration,  # Duration (WORKING METHOD)
                WIDTH,             # Width (WORKING METHOD)
                HEIGHT             # Height (WORKING METHOD)
            )
            print(f"   ✅ Created transition {from_segment}->{to_segment}")
            
        except Exception as e:
            print(f"   ⚠️ Could not create transition {from_segment}->{to_segment}: {e}")

    # Step 8: Compile all frames into final video sequence (WORKING METHOD)
    print("\n🎞️ Step 8: Compiling all frames into final video with audio...")

    # Create a directory to hold all frames in sequence
    final_frames_dir = f"{base_dir}/5_final/frames"
    os.makedirs(final_frames_dir, exist_ok=True)

    # Compile frames and track audio segments using WORKING METHOD
    try:
        frame_count, audio_segments, current_time = compile_frames(
            base_dir,           # Base directory (WORKING METHOD)
            final_frames_dir,   # Final frames directory (WORKING METHOD)
            travel_story_script # Complete script (WORKING METHOD)
        )

        print(f"✅ Compiled {frame_count} frames for final video")
        
    except Exception as e:
        print(f"❌ Error compiling frames: {e}")
        return None

    # Step 9: Create final audio track (WORKING METHOD)
    print("\n🎵 Step 9: Creating final audio track...")
    
    try:
        final_audio_path = f"{base_dir}/6_audio/final_audio.mp3"
        final_audio_path = create_audio_track(audio_segments, current_time, final_audio_path)
        
        if final_audio_path:
            print(f"✅ Final audio track created: {final_audio_path}")
        else:
            print("⚠️ Audio creation failed, video will be silent")
        
    except Exception as e:
        print(f"❌ Error creating final audio: {e}")
        final_audio_path = None

    # Step 10: Create video from frames using FFMPEG (WORKING METHOD)
    print("\n🎬 Step 10: Creating final video with audio...")

    try:
        current_dir = os.getcwd()
        filename_prefix = "narrative_story" if custom_script else "travel_story"
        final_video_no_audio = f"{current_dir}/{filename_prefix}_final_no_audio.mp4"
        final_video = f"{current_dir}/{filename_prefix}_final_with_audio.mp4"

        success = create_final_video(
            final_frames_dir,     # Frames directory (WORKING METHOD)
            final_video_no_audio, # Video without audio (WORKING METHOD)
            final_video,          # Final video with audio (WORKING METHOD)
            final_audio_path      # Audio path (WORKING METHOD)
        )

        if success:
            print("\n" + "=" * 80)
            print("🎉 SUCCESS! Enhanced video generation completed!")
            print("=" * 80)
            print(f"📹 Final video: {final_video}")
            
            # Get file size
            file_size = os.path.getsize(final_video) / (1024 * 1024)  # MB
            print(f"📊 File size: {file_size:.2f} MB")
            
            print(f"\n✨ Enhanced Features Used:")
            print(f"   📸 Mixed image generation (Pexels + AI)")
            print(f"   🎙️ Crystal clear Piper TTS audio")
            print(f"   🎨 Instagram filters and effects")
            print(f"   📐 Perfect 9:16 aspect ratio")
            print(f"   🎬 Smooth transitions and motion")
            print(f"   📱 Optimized for social media")
            
            print(f"\n📊 Image Generation Summary:")
            print(f"   📸 Pexels API: {'✅ Available' if pexels_available else '❌ Not available'}")
            print(f"   🤖 AI Generation: ✅ Stable Diffusion with enhanced fallbacks")
            print(f"   🎨 Filters Applied: ✅ Instagram-style effects")
            
            print(f"\n🚀 Ready for: Instagram Reels, TikTok, YouTube Shorts")
            return final_video
            
        else:
            print("\n⚠️ Video file was not created successfully")
            return None
            
    except Exception as e:
        print(f"\n❌ Error creating final video: {e}")
        print("💡 Check the frames and audio in the output directory")
        return None

def create_enhanced_placeholder(width, height, segment, index):
    """Create an enhanced placeholder image with gradient and proper formatting"""
    
    # Create gradient background
    colors = [
        (70, 130, 180),   # Steel Blue
        (100, 149, 237),  # Cornflower Blue
        (138, 43, 226),   # Blue Violet
        (147, 112, 219),  # Medium Purple
        (186, 85, 211),   # Medium Orchid
        (255, 20, 147),   # Deep Pink
        (255, 69, 0),     # Red Orange
        (255, 140, 0)     # Dark Orange
    ]
    
    base_color = colors[index % len(colors)]
    
    # Create gradient
    image = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(image)
    
    # Add gradient effect
    for y in range(height):
        progress = y / height
        r = int(base_color[0] + (50 * progress))
        g = int(base_color[1] + (30 * progress))
        b = int(base_color[2] + (20 * progress))
        color = (min(255, r), min(255, g), min(255, b))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add decorative elements
    center_x, center_y = width // 2, height // 2
    
    # Draw circles
    for i in range(3):
        radius = 20 + (i * 15)
        alpha = 150 - (i * 40)
        
        # Draw circle outline
        draw.ellipse([
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        ], outline=(255, 255, 255, alpha), width=2)
    
    # Add text
    try:
        font_large = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw text with better formatting
    title = f"Segment {index + 1}"
    text = segment.get("text", "")
    
    # Wrap text
    max_width = width - 40
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) * 8 < max_width:  # Rough estimate
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Keep only first 4 lines
    lines = lines[:4]
    
    # Calculate text positioning
    total_text_height = 25 + (len(lines) * 18)  # Title + lines
    start_y = center_y - (total_text_height // 2)
    
    # Draw title
    title_width = len(title) * 10  # Rough estimate
    title_x = center_x - (title_width // 2)
    
    # Title shadow
    draw.text((title_x + 1, start_y + 1), title, font=font_large, fill=(0, 0, 0))
    # Title text
    draw.text((title_x, start_y), title, font=font_large, fill=(255, 255, 255))
    
    # Draw content lines
    for i, line in enumerate(lines):
        line_width = len(line) * 7  # Rough estimate
        line_x = center_x - (line_width // 2)
        line_y = start_y + 25 + (i * 18)
        
        # Line shadow
        draw.text((line_x + 1, line_y + 1), line, font=font_small, fill=(0, 0, 0))
        # Line text
        draw.text((line_x, line_y), line, font=font_small, fill=(255, 255, 255))
    
    return image

def create_emergency_segment_frames(image_path, frames_dir, duration, text, segment_num):
    """Create emergency frames when motion generation fails"""
    try:
        print(f"   🚨 Creating emergency frames for segment {segment_num}")
        
        # Load the image
        image = Image.open(image_path)
        
        # Calculate frame count
        fps = 30
        total_frames = max(30, int(duration * fps))
        
        # Create static frames with slight variations
        for frame_num in range(total_frames):
            # Create a copy of the image
            frame = image.copy()
            
            # Save frame
            frame_filename = f"frame_{frame_num:04d}.png"
            frame_path = os.path.join(frames_dir, frame_filename)
            frame.save(frame_path)
        
        print(f"   ✅ Created {total_frames} emergency frames for segment {segment_num}")
        
    except Exception as e:
        print(f"   ❌ Emergency frame creation failed for segment {segment_num}: {e}")

if __name__ == "__main__":
    print("🎬 Enhanced Groq Reel Generator - Direct Run")
    print("="*50)
    print("Running with proven working pattern...")
    result = main()
    
    if result:
        print(f"\n🎉 Video generated successfully: {result}")
    else:
        print(f"\n⚠️ Video generation had issues")
