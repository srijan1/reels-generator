"""
Main script with fixed audio-video synchronization and guaranteed audio for all segments.
Save this as: fixed_main_with_sync.py
"""

# --- BEGIN FFMPEG PATH MODIFICATION ---
from ffmpeg_config import ensure_ffmpeg_in_path
ensure_ffmpeg_in_path()
# --- END FFMPEG PATH MODIFICATION ---
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
from enhanced_video_assembly import compile_frames, create_audio_track, create_final_video
from enhanced_image_generation import generate_segment_images_mixed, test_pexels_api
from utils import adjust_segment_duration

def ensure_audio_for_segment(segment, segment_num, audio_dir):
    """Ensure a segment has valid audio, creating it if necessary"""
    
    audio_path = f"{audio_dir}/segment_{segment_num}.mp3"
    
    # Check if audio already exists and is valid
    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
        duration = get_audio_duration(audio_path)
        if duration and duration > 0:
            print(f"Segment {segment_num} audio already exists and is valid ({duration:.2f}s)")
            return audio_path
    
    print(f"Segment {segment_num} needs audio generation")
    
    # Get text for narration
    narration_text = segment.get("narration", segment.get("text", f"Segment {segment_num}"))
    target_duration = segment.get("duration_seconds", 7.5)
    
    # Generate audio with multiple attempts
    for attempt in range(3):
        print(f"Audio generation attempt {attempt + 1} for segment {segment_num}")
        
        try:
            result = adjust_speech_to_duration(narration_text, target_duration, audio_path)
            
            if result and os.path.exists(result) and os.path.getsize(result) > 0:
                duration = get_audio_duration(result)
                if duration and duration > 0:
                    print(f"✅ Successfully generated audio for segment {segment_num} ({duration:.2f}s)")
                    return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
    
    # Final fallback - create silent audio
    print(f"Creating silent fallback for segment {segment_num}")
    return create_silent_audio_with_duration(narration_text, audio_path, target_duration)

def create_silent_audio_with_duration(text, output_path, target_duration):
    """Create a silent audio file with specific duration"""
    try:
        # Calculate duration based on text length if not provided
        if target_duration is None:
            word_count = len(text.split())
            target_duration = max(3, word_count / 2.5)
        
        print(f"Creating silent audio fallback (duration: {target_duration:.2f}s)")
        
        # Use ffmpeg to create a silent audio file
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", 
            "-i", f"anullsrc=r=44100:cl=stereo", 
            "-t", str(target_duration),
            "-acodec", "mp3",
            "-ab", "128k",
            output_path
        ]
        
        import subprocess
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                      timeout=30, check=True)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"Created silent audio at {output_path}")
            return output_path
        else:
            print(f"Failed to create silent audio at {output_path}")
            return None
    
    except Exception as e:
        print(f"Error creating silent audio: {e}")
        return None

def main(custom_script=None, resume_base_dir=None, resume_state=None):
    """Main function with perfect audio-video synchronization"""

    if resume_state is None:
        resume_state = {}

    travel_story_script = None 
    base_dir = None
    segment_images = []
    final_frames_dir = None
    final_audio_path = None
    audio_segments = [] 
    current_time = 0    

    # --- Initialization Phase ---
    if resume_base_dir and os.path.isdir(resume_base_dir) and custom_script: # custom_script is the loaded script when resuming
        base_dir = resume_base_dir
        travel_story_script = custom_script # Script is passed by groq_reel_generator
        print(f"Attempting to resume from: {base_dir}")
        if not travel_story_script:
            print("Error: Script not provided for resume. Cannot continue.")
            return
        print(f"Using loaded script: {travel_story_script.get('title', 'Untitled Script')}")
    elif not resume_base_dir: # New run
        timestamp = int(time.time())
        base_dir = f"./story_reel_{timestamp}"
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(f"{base_dir}/1_script", exist_ok=True)
        os.makedirs(f"{base_dir}/2_images", exist_ok=True)
        os.makedirs(f"{base_dir}/3_frames", exist_ok=True)
        os.makedirs(f"{base_dir}/4_transitions", exist_ok=True)
        os.makedirs(f"{base_dir}/5_final", exist_ok=True)
        os.makedirs(f"{base_dir}/6_audio", exist_ok=True)
    else: # resume_base_dir provided but custom_script (loaded script) is not
        print("Error: Resume directory provided, but no script loaded. Cannot resume.")
        return

    # --- Step 1: Script Generation/Loading ---
    if not resume_base_dir: # New run logic for script
        print("Step 1: Generating narrative story content...")
        # custom_script is from groq_reel_generator for new runs
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
        if not custom_script: # Only adjust if it's the default script
            travel_story_script = adjust_segment_duration(travel_story_script, target_total_duration=60)
        else: # For custom scripts, ensure subtitle_mode is set
            for segment in travel_story_script["segments"]:
                segment["subtitle_mode"] = True

        # Save the script to file
        script_path = f"{base_dir}/1_script/story_script.json"
        with open(script_path, 'w') as f:
            json.dump(travel_story_script, f, indent=4)
        print(f"Story script saved to {script_path}")
        resume_state['script_generated'] = True # Mark as done for this new run

    if not travel_story_script:
        print("Error: Story script not available. Exiting.")
        return

    # --- Step 2: Narration ---
    if not resume_state.get('narration_generated'):
        print("\nStep 2: Generating enhanced narration content...")
        for i, segment in enumerate(travel_story_script["segments"]):
            original_text = segment["text"]
            image_prompt = segment["image_prompt"]
            enhanced_narration = generate_narration(
                image_prompt, 
                original_text, 
                desired_duration_seconds=segment["duration_seconds"]
            )
            segment["narration"] = enhanced_narration
        narration_script_path = f"{base_dir}/1_script/story_script_with_narration.json"
        with open(narration_script_path, 'w') as f:
            json.dump(travel_story_script, f, indent=4)
        print(f"Narration script saved to {narration_script_path}")
        resume_state['narration_generated'] = True

    # --- Step 3: Audio Segments ---
    if not resume_state.get('audio_segments_generated'):
        print("\nStep 3: Generating audio narrations with guaranteed synchronization...")
        for i, segment in enumerate(travel_story_script["segments"]):
            audio_path_segment = ensure_audio_for_segment(
                segment, 
                i+1, 
                f"{base_dir}/6_audio"
            )
            if audio_path_segment:
                duration = get_audio_duration(audio_path_segment)
                if duration:
                    segment["audio_duration"] = duration
                    segment["audio_path"] = audio_path_segment
                else:
                    segment["audio_duration"] = segment["duration_seconds"]
                    segment["audio_path"] = audio_path_segment
            else:
                segment["audio_duration"] = segment["duration_seconds"]
        audio_script_path = f"{base_dir}/1_script/story_script_with_audio.json"
        with open(audio_script_path, 'w') as f:
            json.dump(travel_story_script, f, indent=4)
        print(f"Audio script saved to {audio_script_path}")
        resume_state['audio_segments_generated'] = True

    # --- Step 4: Image Generation ---
    # Image dimensions (9:16 aspect ratio for vertical video)
    HEIGHT = 512
    WIDTH = 288
    device = "cpu" # Determine device - CPU for compatibility
    
    # This list will hold the final paths for all segments.
    # It will be populated by existing images first, then by newly generated ones.
    final_segment_image_paths = [None] * len(travel_story_script["segments"])
    indices_needing_generation = list(range(len(travel_story_script["segments"])))

    if resume_base_dir:
        print("\nStep 4: Checking for existing images (Resume Mode)...")
        images_base_path = os.path.join(base_dir, "2_images")
        
        temp_indices_needing_generation = []
        all_found_on_resume = True
        for i_resume_check in range(len(travel_story_script["segments"])):
            expected_image_path = os.path.join(images_base_path, f"segment_{i_resume_check+1}.png")
            if os.path.exists(expected_image_path) and os.path.getsize(expected_image_path) > 0:
                final_segment_image_paths[i_resume_check] = expected_image_path
                print(f"  Image for segment {i_resume_check+1} found: {expected_image_path}")
            else:
                temp_indices_needing_generation.append(i_resume_check)
                all_found_on_resume = False
                print(f"  Image for segment {i_resume_check+1} MISSING.")
        
        if all_found_on_resume:
            print("All images previously generated. Skipping image generation step.")
            resume_state['images_generated'] = True
        else:
            indices_needing_generation = temp_indices_needing_generation
            print(f"Will generate images for {len(indices_needing_generation)} missing segments: {[(x+1) for x in indices_needing_generation]}")
            resume_state['images_generated'] = False # Mark that some generation is needed
    else: # New run
        print("\nStep 4: Preparing for new image generation (New Run)...")
        resume_state['images_generated'] = False

    if not resume_state.get('images_generated'): # If not all images were present on resume, or it's a new run
        print(f"\nStep 4 (Execution): Generating images for segments: {[(idx+1) for idx in indices_needing_generation]}...")
        print(f"Using device: {device}")
        pexels_available = test_pexels_api()
        if pexels_available:
            print("✅ Pexels API is working - will use stock photos where possible")
        else:
            print("⚠️  Pexels API unavailable - will use AI generation for all images")
        
        try:
            # This function will generate images for 'indices_needing_generation'
            # and save them to their respective paths like "base_dir/2_images/segment_{index+1}.png"
            # It also handles fallbacks to placeholders if individual generations fail.
            _ = generate_segment_images_mixed( 
                travel_story_script["segments"],
                base_dir,
                height=HEIGHT,
                width=WIDTH,
                device=device,
                only_indices=indices_needing_generation # CRITICAL: pass only missing indices
            )

            # After generation, verify all images again and populate final_segment_image_paths
            all_images_now_definitively_present = True
            images_base_path_after_gen = os.path.join(base_dir, "2_images")
            for i_verify in range(len(travel_story_script["segments"])):
                current_path = os.path.join(images_base_path_after_gen, f"segment_{i_verify+1}.png")
                if os.path.exists(current_path) and os.path.getsize(current_path) > 0:
                    final_segment_image_paths[i_verify] = current_path
                else:
                    print(f"⚠️ Image for segment {i_verify+1} still missing after generation attempt. Creating placeholder.")
                    colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255), (255, 255, 200), 
                              (255, 200, 255), (200, 255, 255), (255, 230, 200), (230, 255, 200)]
                    color = colors[i_verify % len(colors)]
                    ph_image = Image.new('RGB', (WIDTH, HEIGHT), color=color)
                    ph_path = os.path.join(images_base_path_after_gen, f"segment_{i_verify+1}.png")
                    ph_image.save(ph_path)
                    final_segment_image_paths[i_verify] = ph_path
                    all_images_now_definitively_present = False 
            
            if all_images_now_definitively_present and all(p is not None for p in final_segment_image_paths):
                print(f"✅ Successfully generated/verified all {len(final_segment_image_paths)} images.")
            else:
                print(f"⚠️  Some images might be placeholders. Total images accounted for: {len([p for p in final_segment_image_paths if p])}.")
            resume_state['images_generated'] = True # Mark step as "processed"

        except Exception as e:
            print(f"\nGlobal error during mixed image generation: {e}. Falling back to placeholders for ALL segments.")
            placeholder_dir = f"{base_dir}/2_images"
            os.makedirs(placeholder_dir, exist_ok=True)
            for i_ph_global in range(len(travel_story_script["segments"])):
                if final_segment_image_paths[i_ph_global] is None or not os.path.exists(final_segment_image_paths[i_ph_global]):
                    colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255), (255, 255, 200), 
                              (255, 200, 255), (200, 255, 255), (255, 230, 200), (230, 255, 200)]
                    color = colors[i_ph_global % len(colors)]
                    ph_image = Image.new('RGB', (WIDTH, HEIGHT), color=color)
                    ph_path = os.path.join(placeholder_dir, f"segment_{i_ph_global+1}.png")
                    ph_image.save(ph_path)
                    final_segment_image_paths[i_ph_global] = ph_path
            resume_state['images_generated'] = True # Mark step as "processed" with fallbacks

    segment_images = final_segment_image_paths # Use the populated list for subsequent steps
    if any(p is None for p in segment_images):
        print("Error: Not all segment images have a valid path after generation/resume. Aborting.")
        return # Or raise an exception

    # --- Step 5: Filters ---
    if not resume_state.get('filters_applied', False): # Add 'filters_applied' to resume_state checks
        print("\nStep 5: Applying Instagram-style filters to images...")
        filter_types = ["natural", "warm_travel", "moody", "nostalgic", "golden_hour"]
        for i_filter, img_path_filter in enumerate(segment_images):
            try:
                image = Image.open(img_path_filter)
                filter_type = filter_types[i_filter % len(filter_types)]
                print(f"Applying {filter_type} filter to segment {i_filter+1}")
                filtered_image = apply_instagram_filter(image, filter_type)
                filtered_image.save(img_path_filter, format="PNG", compress_level=0)
            except Exception as e:
                print(f"⚠️  Could not apply filter to segment {i_filter+1}: {e}")
        resume_state['filters_applied'] = True

    # --- Step 6: Segment Frames ---
    if not resume_state.get('segment_frames_generated'):
        print("\nStep 6: Generating dynamic video frames with perfect audio-visual sync...")
        for i_motion, img_path_motion in enumerate(segment_images):
            segment_frames_dir = f"{base_dir}/3_frames/segment_{i_motion+1}"
            os.makedirs(segment_frames_dir, exist_ok=True)
            segment = travel_story_script["segments"][i_motion]
            audio_duration = segment.get("audio_duration", segment.get("duration_seconds", 7.5))
            # ... (rest of create_enhanced_motion_frames call and params) ...
            create_enhanced_motion_frames(
                img_path_motion, segment_frames_dir, audio_duration, 
                segment.get("narration", segment.get("text", "")),
                audio_duration=audio_duration, style=segment.get("style","professional"),
                motion_type=segment.get("zoom_direction","gentle_pulse"), subtitle=segment.get("subtitle_mode",True)
            )
        resume_state['segment_frames_generated'] = True

    # --- Step 7: Transitions ---
    if not resume_state.get('transitions_generated'):
        print("\nStep 7: Creating advanced transitions between segments...")
        for i_trans in range(len(travel_story_script["segments"]) - 1):
            # ... (create_transition_frames call and params) ...
            create_transition_frames(base_dir, i_trans + 1, i_trans + 2, 
                                     travel_story_script["segments"][i_trans].get("transition", "smooth_fade"),
                                     1.0, WIDTH, HEIGHT)
        resume_state['transitions_generated'] = True

    # --- Step 8: Compile Frames ---
    final_frames_dir = os.path.join(base_dir, "5_final", "frames") 
    compile_state_path = os.path.join(base_dir, "5_final", "compile_state.json")

    if not resume_state.get('frames_compiled'):
        print("\nStep 8: Compiling all frames into final video with perfect audio sync...")
        os.makedirs(final_frames_dir, exist_ok=True)
        frame_count, audio_segments, current_time = compile_frames(
            base_dir, 
            final_frames_dir, 
            travel_story_script
        )
        print(f"✅ Compiled {frame_count} frames for final video")
        print(f"📊 Total duration: {current_time:.2f} seconds")
        with open(compile_state_path, 'w') as f_state:
            json.dump({"audio_segments": audio_segments, "current_time": current_time, "frame_count": frame_count}, f_state)
        resume_state['frames_compiled'] = True
    else:
        print("\nStep 8: Frames previously compiled. Loading state...")
        if os.path.exists(compile_state_path):
            with open(compile_state_path, 'r') as f_state:
                compile_data = json.load(f_state)
                audio_segments = compile_data.get("audio_segments", [])
                current_time = compile_data.get("current_time", 0)
        else: # compile_state.json missing, must re-run compilation
            print(f"Warning: {compile_state_path} missing. Re-running frame compilation.")
            os.makedirs(final_frames_dir, exist_ok=True) # Ensure dir exists
            frame_count, audio_segments, current_time = compile_frames(
                base_dir, final_frames_dir, travel_story_script
            )
            with open(compile_state_path, 'w') as f_state:
                json.dump({"audio_segments": audio_segments, "current_time": current_time, "frame_count": frame_count}, f_state)
            print(f"✅ Re-compiled {frame_count} frames. Total duration: {current_time:.2f} seconds")

    # --- Step 9: Final Audio ---
    final_audio_path = os.path.join(base_dir, "6_audio", "final_audio.mp3")
    if not resume_state.get('final_audio_created'):
        print("\nStep 9: Creating final audio track with perfect synchronization...")
        if not audio_segments and current_time == 0: # Check if audio_segments and current_time were loaded
            print("Error: Audio segment data not available for final audio creation. This indicates an issue with resuming Step 8.")
            return
        
        final_audio_path_result = create_audio_track(audio_segments, current_time, final_audio_path)

        if final_audio_path_result:
            final_audio_path = final_audio_path_result # Update with actual path
            final_audio_duration = get_audio_duration(final_audio_path) # Use the updated path
            if final_audio_duration:
                print(f"✅ Final audio track: {final_audio_duration:.2f} seconds")
            else:
                print("⚠️  Could not verify final audio duration")
        else:
            print("❌ Failed to create final audio track. Cannot proceed to video creation.")
            return 
        resume_state['final_audio_created'] = True
    elif not os.path.exists(final_audio_path) or os.path.getsize(final_audio_path) == 0:
        print(f"Error: Resuming, final_audio_created is true, but {final_audio_path} is missing or empty. Re-run audio creation.")
        # This case should ideally re-trigger step 9 or be handled by more granular resume_state.
        # For now, error out.
        return


    # --- Step 10: Final Video ---
    print("\nStep 10: Creating final video with perfect audio-video sync...")

    current_dir = os.getcwd()
    
    # Determine if this run (new or resumed) is for a custom story for filename prefix
    is_custom_for_filename = False
    default_script_title_in_this_file = "My Solo Trip to Kyoto" # Title of default script in this file

    if travel_story_script:
        # If a script was loaded (either new custom, new default, or resumed)
        # Check if its title differs from the hardcoded default title in this file.
        # This is a proxy for "is it a custom script from Groq?"
        if travel_story_script.get("title", default_script_title_in_this_file) != default_script_title_in_this_file:
            is_custom_for_filename = True
    elif custom_script: # Fallback if travel_story_script somehow didn't get set but custom_script (arg) was passed
        is_custom_for_filename = True
    
    filename_prefix = "narrative_story" if is_custom_for_filename else "travel_story"
    final_video_no_audio = os.path.join(base_dir, f"{filename_prefix}_final_no_audio.mp4")
    final_video = os.path.join(base_dir, f"{filename_prefix}_final_with_audio.mp4")

    if not os.path.isdir(final_frames_dir) or not os.listdir(final_frames_dir):
        print(f"Error: Final frames directory '{final_frames_dir}' is missing or empty for final video creation.")
        return
    if not final_audio_path or not os.path.exists(final_audio_path):
        print(f"Error: Final audio path '{final_audio_path}' is missing or invalid for final video creation.")
        return
    success = create_final_video(
        final_frames_dir, 
        final_video_no_audio, 
        final_video, 
        final_audio_path
    )

    if success:
        print("\n" + "=" * 60)
        if is_custom_for_filename:
             print("🎉 SUCCESS! Custom narrative video generated/resumed with perfect synchronization!")
        else:
            print("🎉 SUCCESS! Video generated/resumed with perfect synchronization!")
        print("=" * 60)
        print(f"📁 Final video: {final_video}")
        # Further details based on is_custom_for_filename
        if is_custom_for_filename and travel_story_script and len(travel_story_script.get("segments", [])) == 8:
            print("   📖 Custom narrative storytelling powered by Groq API") # Or relevant features
        # ... other print statements from original file, adapted ...
        print(f"\n🚀 Ready for: Instagram Reels, TikTok, YouTube Shorts") # Common footer
        
    else:
        print("\n❌ Video generation encountered issues.")
        print("📁 Generated frames and audio are available in the output directory")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
