"""
Functions for assembling frames and audio into the final video.
"""

import os
import shutil
from pydub import AudioSegment

def compile_frames(base_dir, final_frames_dir, travel_story_script):
    """
    Compile all frames and transitions into a sequence,
    and track audio segments and timing
    """
    # Frame counter for the final sequence
    frame_count = 0

    # Keep track of audio segments and their timing
    audio_segments = []
    current_time = 0

    # Add each segment and transition to the final sequence
    for i, segment in enumerate(travel_story_script["segments"]):
        segment_num = i + 1
        segment_frames_dir = f"{base_dir}/3_frames/segment_{segment_num}"
        
        # Check if the directory exists
        if not os.path.exists(segment_frames_dir):
            print(f"Warning: Segment frames directory not found: {segment_frames_dir}")
            continue
            
        # Copy segment frames to final sequence
        try:
            segment_frame_files = sorted([f for f in os.listdir(segment_frames_dir) if f.endswith('.png')])
            if not segment_frame_files:
                print(f"Warning: No frames found in {segment_frames_dir}")
                continue
                
            # Record this segment's audio timing information
            segment_duration = len(segment_frame_files) / 30.0  # 30fps
            
            if "audio_path" in segment:
                audio_segments.append({
                    "path": segment["audio_path"],
                    "start_time": current_time,
                    "duration": segment_duration
                })
            
            # Update timing for next segment
            current_time += segment_duration
                
            for frame_file in segment_frame_files:
                src_path = os.path.join(segment_frames_dir, frame_file)
                dst_path = f"{final_frames_dir}/frame_{frame_count:06d}.png"
                # Use shutil.copy
                shutil.copy(src_path, dst_path)
                frame_count += 1
                
            print(f"Added {len(segment_frame_files)} frames from segment {segment_num}")
        except Exception as e:
            print(f"Error processing segment {segment_num}: {e}")

        # Add transition to next segment if not the last segment
        if i < len(travel_story_script["segments"]) - 1:
            transition_dir = f"{base_dir}/4_transitions/transition_{segment_num}_to_{segment_num+1}"
            
            if not os.path.exists(transition_dir):
                print(f"Warning: Transition directory not found: {transition_dir}")
                continue
                
            try:
                transition_frame_files = sorted([f for f in os.listdir(transition_dir) if f.endswith('.png')])
                if not transition_frame_files:
                    print(f"Warning: No transition frames found in {transition_dir}")
                    continue
                    
                # Record transition timing for audio
                transition_duration = len(transition_frame_files) / 30.0  # 30fps
                current_time += transition_duration
                    
                for frame_file in transition_frame_files:
                    src_path = os.path.join(transition_dir, frame_file)
                    dst_path = f"{final_frames_dir}/frame_{frame_count:06d}.png"
                    # Use shutil.copy
                    shutil.copy(src_path, dst_path)
                    frame_count += 1
                    
                print(f"Added {len(transition_frame_files)} frames from transition {segment_num} to {segment_num+1}")
            except Exception as e:
                print(f"Error processing transition {segment_num} to {segment_num+1}: {e}")

    return frame_count, audio_segments, current_time

def create_audio_track(audio_segments, total_duration, output_path):
    """Create final audio track by overlaying all segment audio files"""
    try:
        # Check if we have any audio segments
        if audio_segments:
            # Create an empty audio segment as the base
            final_audio = AudioSegment.silent(duration=0)
            
            # Calculate the total duration in milliseconds
            total_duration_ms = int(total_duration * 1000)
            final_audio = AudioSegment.silent(duration=total_duration_ms)
            
            # Overlay each audio segment at the correct position
            for segment in audio_segments:
                if os.path.exists(segment["path"]):
                    # Load the audio segment
                    audio = AudioSegment.from_file(segment["path"])
                    
                    # Position in milliseconds
                    position_ms = int(segment["start_time"] * 1000)
                    
                    # Overlay at the correct position
                    final_audio = final_audio.overlay(audio, position=position_ms)
                    
                    print(f"Added audio segment starting at {segment['start_time']:.2f}s")
                else:
                    print(f"Warning: Audio file not found: {segment['path']}")
            
            # Export the final audio
            final_audio.export(output_path, format="mp3")
            print(f"Created final audio track at {output_path}")
            return output_path
        else:
            print("No audio segments found, skipping audio creation")
            return None
    except Exception as e:
        print(f"Error creating final audio track: {e}")
        return None

def create_final_video(frames_dir, video_no_audio_path, final_video_path, audio_path=None):
    """Create video from frames using FFMPEG and add audio"""
    try:
        # Check if ffmpeg is installed and accessible
        ffmpeg_check = os.system("which ffmpeg > /dev/null 2>&1")
        
        if ffmpeg_check != 0:
            # For macOS, try to check with another method
            ffmpeg_check = os.system("ffmpeg -version > /dev/null 2>&1")
            if ffmpeg_check != 0:
                print("FFMPEG not found. Please install ffmpeg:")
                print("For macOS: brew install ffmpeg")
                print("For Linux: apt-get install ffmpeg")
                print("Then run the script again.")
                return False
        else:
            print("FFMPEG is installed. Proceeding with video creation.")
        
        # Create 30fps video - using absolute paths
        abs_frames_dir = os.path.abspath(frames_dir)
        abs_final_video_no_audio = os.path.abspath(video_no_audio_path)
        
        print(f"Creating video from frames in {abs_frames_dir}")
        
        # First create video without audio
        cmd = f"ffmpeg -y -framerate 30 -pattern_type glob -i '{abs_frames_dir}/frame_*.png' -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p {abs_final_video_no_audio}"
        print(f"Running FFMPEG command: {cmd}")
        os.system(cmd)

        if os.path.exists(abs_final_video_no_audio):
            print(f"Successfully created video without audio: {abs_final_video_no_audio}")
            
            # If we have audio, add it to the video
            if audio_path and os.path.exists(audio_path):
                abs_final_audio = os.path.abspath(audio_path)
                abs_final_video = os.path.abspath(final_video_path)
                
                # Add audio to video
                cmd_audio = f"ffmpeg -y -i {abs_final_video_no_audio} -i {abs_final_audio} -c:v copy -c:a aac -shortest {abs_final_video}"
                print(f"Adding audio with command: {cmd_audio}")
                os.system(cmd_audio)
                
                if os.path.exists(abs_final_video):
                    print(f"Successfully created final video with audio: {abs_final_video}")
                    return True
                else:
                    print(f"Failed to create video with audio at {abs_final_video}")
                    return False
            else:
                print("No audio track found or not created successfully.")
                # Copy no-audio version to final name
                shutil.copy(abs_final_video_no_audio, final_video_path)
                print(f"Copied no-audio version to {final_video_path}")
                return True
        else:
            print(f"FFMPEG command failed to create video file at {abs_final_video_no_audio}")
            # Try an alternative approach
            cmd2 = f"ffmpeg -y -framerate 30 -i {abs_frames_dir}/frame_%06d.png -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p {abs_final_video_no_audio}"
            print(f"Trying alternative FFMPEG command: {cmd2}")
            os.system(cmd2)
            
            if os.path.exists(abs_final_video_no_audio):
                print(f"Successfully created video with alternative command")
                # If we have audio, add it to the video
                if audio_path and os.path.exists(audio_path):
                    abs_final_audio = os.path.abspath(audio_path)
                    abs_final_video = os.path.abspath(final_video_path)
                    
                    # Add audio to video
                    cmd_audio = f"ffmpeg -y -i {abs_final_video_no_audio} -i {abs_final_audio} -c:v copy -c:a aac -shortest {abs_final_video}"
                    print(f"Adding audio with command: {cmd_audio}")
                    os.system(cmd_audio)
                    return os.path.exists(abs_final_video)
                else:
                    # Copy no-audio version to final name
                    shutil.copy(abs_final_video_no_audio, final_video_path)
                    return True
            else:
                return False

    except Exception as e:
        print(f"Error creating final video: {e}")
        print("\nTo manually create the video from the frames, run the following command:")
        print(f"ffmpeg -framerate 30 -i {frames_dir}/frame_%06d.png -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p {video_no_audio_path}")
        if audio_path:
            print(f"Then add audio with:")
            print(f"ffmpeg -i {video_no_audio_path} -i {audio_path} -c:v copy -c:a aac -shortest {final_video_path}")
        return False
        
