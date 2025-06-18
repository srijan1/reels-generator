"""
Advanced Cinematic Transitions System
This creates professional-quality transitions with dynamic effects like zoom, pan, rotation, and more.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import cv2
import glob
from tqdm import tqdm
import random
import math

class CinematicTransitions:
    """Advanced cinematic transitions with professional effects"""
    
    def __init__(self):
        self.transition_duration = 1.0  # seconds
        self.fps = 30
        self.transition_frames = int(self.transition_duration * self.fps)
        
    def create_transition_frames(self, base_dir, from_segment, to_segment, transition_type, duration, width, height):
        """
        Create advanced cinematic transition frames
        
        Parameters:
        - base_dir: Base directory for the video project
        - from_segment: Source segment number
        - to_segment: Target segment number  
        - transition_type: Type of cinematic transition
        - duration: Duration of transition in seconds
        - width: Frame width
        - height: Frame height
        """
        
        print(f"🎬 Creating CINEMATIC {transition_type} transition: {from_segment} → {to_segment}")
        
        # Create transition directory
        transition_dir = f"{base_dir}/4_transitions/transition_{from_segment}_to_{to_segment}"
        os.makedirs(transition_dir, exist_ok=True)
        
        # Find source frames with better error handling
        from_segment_dir = f"{base_dir}/3_frames/segment_{from_segment}"
        to_segment_dir = f"{base_dir}/3_frames/segment_{to_segment}"
        
        # Check if segment directories exist
        if not os.path.exists(from_segment_dir):
            print(f"❌ Source segment directory not found: {from_segment_dir}")
            return False
            
        if not os.path.exists(to_segment_dir):
            print(f"❌ Target segment directory not found: {to_segment_dir}")
            return False
        
        # Find available frames using glob for better reliability
        from_frames = sorted(glob.glob(os.path.join(from_segment_dir, "*.png")))
        to_frames = sorted(glob.glob(os.path.join(to_segment_dir, "*.png")))
        
        if not from_frames or not to_frames:
            print(f"❌ No frames found in segments {from_segment} or {to_segment}")
            return False
        
        # Get the last frame from source segment and first frame from target segment
        last_frame_path = from_frames[-1]  # Last frame
        first_frame_path = to_frames[0]    # First frame
        
        print(f"📸 Transition frames:")
        print(f"   From: {os.path.basename(last_frame_path)}")
        print(f"   To: {os.path.basename(first_frame_path)}")
        
        try:
            # Load the frames
            last_frame = Image.open(last_frame_path).convert('RGB')
            first_frame = Image.open(first_frame_path).convert('RGB')
            
            # Ensure frames are the correct size
            last_frame = last_frame.resize((width, height), Image.Resampling.LANCZOS)
            first_frame = first_frame.resize((width, height), Image.Resampling.LANCZOS)
            
        except Exception as e:
            print(f"❌ Error loading frames: {e}")
            return False
        
        # Use dynamic frame count based on transition complexity
        if transition_type in ["zoom_burst", "spiral_wipe", "3d_flip", "lens_distortion"]:
            transition_frames = 45  # 1.5 seconds for complex transitions
        elif transition_type in ["zoom_in_out", "pan_zoom", "rotate_zoom", "elastic_zoom"]:
            transition_frames = 36  # 1.2 seconds for moderate transitions
        else:
            transition_frames = 30  # 1.0 second for simple transitions
        
        print(f"🎬 Generating {transition_frames} cinematic transition frames...")
        
        # Generate transition frames based on type
        try:
            for j in tqdm(range(transition_frames), desc=f"Creating {transition_type}"):
                progress = j / (transition_frames - 1)  # 0 to 1
                
                # Create the cinematic transition frame
                transition_frame = self.create_cinematic_effect(
                    last_frame, first_frame, progress, transition_type, width, height
                )
                
                # Save transition frame
                frame_filename = f"frame_{j:04d}.png"
                transition_path = os.path.join(transition_dir, frame_filename)
                transition_frame.save(transition_path, format="PNG")
            
            print(f"✅ Created {transition_frames} cinematic transition frames!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating transition frames: {e}")
            return False
    
    def create_cinematic_effect(self, img1, img2, progress, transition_type, width, height):
        """Create specific cinematic transition effects"""
        
        if transition_type == "zoom_in_out":
            return self.zoom_in_out_transition(img1, img2, progress)
        
        elif transition_type == "pan_zoom":
            return self.pan_zoom_transition(img1, img2, progress, width, height)
        
        elif transition_type == "rotate_zoom":
            return self.rotate_zoom_transition(img1, img2, progress, width, height)
        
        elif transition_type == "zoom_burst":
            return self.zoom_burst_transition(img1, img2, progress, width, height)
        
        elif transition_type == "spiral_wipe":
            return self.spiral_wipe_transition(img1, img2, progress, width, height)
        
        elif transition_type == "3d_flip":
            return self.flip_3d_transition(img1, img2, progress, width, height)
        
        elif transition_type == "lens_distortion":
            return self.lens_distortion_transition(img1, img2, progress, width, height)
        
        elif transition_type == "elastic_zoom":
            return self.elastic_zoom_transition(img1, img2, progress, width, height)
        
        elif transition_type == "cinematic_wipe":
            return self.cinematic_wipe_transition(img1, img2, progress, width, height)
        
        elif transition_type == "depth_push":
            return self.depth_push_transition(img1, img2, progress, width, height)
        
        elif transition_type == "radial_blur":
            return self.radial_blur_transition(img1, img2, progress, width, height)
        
        elif transition_type == "vortex_spin":
            return self.vortex_spin_transition(img1, img2, progress, width, height)
        
        else:
            # Default to enhanced smooth fade
            return self.enhanced_smooth_fade(img1, img2, progress)
    
    def zoom_in_out_transition(self, img1, img2, progress):
        """Zoom into first image, then zoom out to reveal second image"""
        
        if progress < 0.5:
            # First half: zoom into img1
            zoom_progress = progress * 2  # 0 to 1
            zoom_factor = 1.0 + (1.5 * zoom_progress)  # Zoom from 1x to 2.5x
            
            # Apply zoom with easing
            eased_zoom = zoom_factor ** 1.5
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            h, w = img1_cv.shape[:2]
            
            # Create zoom transformation matrix
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, eased_zoom)
            M[0, 2] += (w - eased_zoom * w) / 2
            M[1, 2] += (h - eased_zoom * h) / 2
            
            zoomed = cv2.warpAffine(img1_cv, M, (w, h))
            
            # Add motion blur for realism
            if zoom_progress > 0.3:
                blur_amount = int((zoom_progress - 0.3) * 10)
                zoomed = cv2.blur(zoomed, (blur_amount, blur_amount))
            
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        else:
            # Second half: zoom out from img2
            zoom_progress = (progress - 0.5) * 2  # 0 to 1
            zoom_factor = 2.5 - (1.5 * zoom_progress)  # Zoom from 2.5x to 1x
            
            # Apply reverse zoom with easing
            eased_zoom = zoom_factor ** 0.7
            img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
            h, w = img2_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, eased_zoom)
            M[0, 2] += (w - eased_zoom * w) / 2
            M[1, 2] += (h - eased_zoom * h) / 2
            
            zoomed = cv2.warpAffine(img2_cv, M, (w, h))
            
            # Add motion blur for transition
            if zoom_progress < 0.7:
                blur_amount = int((0.7 - zoom_progress) * 8)
                zoomed = cv2.blur(zoomed, (blur_amount, blur_amount))
            
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
    
    def pan_zoom_transition(self, img1, img2, progress, width, height):
        """Pan across first image while zooming, then reveal second image"""
        
        # Create expanded canvas for panning
        expanded_width = int(width * 1.5)
        expanded_height = int(height * 1.5)
        
        if progress < 0.6:
            # Pan and zoom on first image
            pan_progress = progress / 0.6
            
            # Resize img1 to expanded size
            img1_expanded = img1.resize((expanded_width, expanded_height), Image.Resampling.LANCZOS)
            img1_cv = cv2.cvtColor(np.array(img1_expanded), cv2.COLOR_RGB2BGR)
            
            # Calculate pan offset (right to left movement)
            max_offset_x = expanded_width - width
            offset_x = int(max_offset_x * pan_progress)
            
            # Add slight zoom during pan
            zoom_factor = 1.0 + (0.3 * pan_progress)
            center_x = offset_x + width // 2
            center_y = height // 2
            
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            
            # Apply transformation
            panned = cv2.warpAffine(img1_cv, M, (expanded_width, expanded_height))
            
            # Crop to original size
            cropped = panned[0:height, offset_x:offset_x + width]
            
            result = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        else:
            # Transition to second image with zoom out
            transition_progress = (progress - 0.6) / 0.4
            
            # Get final frame from pan sequence
            img1_expanded = img1.resize((expanded_width, expanded_height), Image.Resampling.LANCZOS)
            img1_cv = cv2.cvtColor(np.array(img1_expanded), cv2.COLOR_RGB2BGR)
            
            max_offset_x = expanded_width - width
            offset_x = max_offset_x
            
            zoom_factor = 1.3
            center_x = offset_x + width // 2
            center_y = height // 2
            
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            panned = cv2.warpAffine(img1_cv, M, (expanded_width, expanded_height))
            cropped = panned[0:height, offset_x:offset_x + width]
            
            panned_img1 = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
            
            # Blend with second image
            return Image.blend(panned_img1, img2, transition_progress)
    
    def rotate_zoom_transition(self, img1, img2, progress, width, height):
        """Rotate and zoom first image, then spin into second image"""
        
        if progress < 0.5:
            # First half: rotate and zoom img1
            rotate_progress = progress * 2
            
            angle = 180 * rotate_progress  # Rotate 180 degrees
            zoom_factor = 1.0 + (1.0 * rotate_progress)  # Zoom from 1x to 2x
            
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            h, w = img1_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), angle, zoom_factor)
            
            rotated = cv2.warpAffine(img1_cv, M, (w, h))
            
            # Add motion blur for spin effect
            if rotate_progress > 0.2:
                blur_amount = int(rotate_progress * 5)
                rotated = cv2.blur(rotated, (blur_amount, blur_amount))
            
            result = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        else:
            # Second half: spin from img2
            rotate_progress = (progress - 0.5) * 2
            
            angle = 180 - (180 * rotate_progress)  # Rotate from 180 to 0 degrees
            zoom_factor = 2.0 - (1.0 * rotate_progress)  # Zoom from 2x to 1x
            
            img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
            h, w = img2_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), angle, zoom_factor)
            
            rotated = cv2.warpAffine(img2_cv, M, (w, h))
            
            # Add motion blur for spin effect
            if rotate_progress < 0.8:
                blur_amount = int((0.8 - rotate_progress) * 5)
                rotated = cv2.blur(rotated, (blur_amount, blur_amount))
            
            result = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
    
    def zoom_burst_transition(self, img1, img2, progress, width, height):
        """Explosive zoom effect with radial burst"""
        
        if progress < 0.3:
            # Build up: slight zoom on first image
            zoom_progress = progress / 0.3
            zoom_factor = 1.0 + (0.2 * zoom_progress)
            
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            h, w = img1_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            M[0, 2] += (w - zoom_factor * w) / 2
            M[1, 2] += (h - zoom_factor * h) / 2
            
            zoomed = cv2.warpAffine(img1_cv, M, (w, h))
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        elif progress < 0.7:
            # Burst phase: extreme zoom with radial blur
            burst_progress = (progress - 0.3) / 0.4
            zoom_factor = 1.2 + (3.0 * burst_progress)  # Zoom from 1.2x to 4.2x
            
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            h, w = img1_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            M[0, 2] += (w - zoom_factor * w) / 2
            M[1, 2] += (h - zoom_factor * h) / 2
            
            zoomed = cv2.warpAffine(img1_cv, M, (w, h))
            
            # Add radial motion blur
            blur_amount = int(15 * burst_progress)
            if blur_amount > 0:
                zoomed = cv2.blur(zoomed, (blur_amount, blur_amount))
            
            # Add white flash effect
            flash_intensity = int(255 * burst_progress * 0.3)
            if flash_intensity > 0:
                zoomed = cv2.add(zoomed, np.full(zoomed.shape, flash_intensity, dtype=np.uint8))
            
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        else:
            # Settle phase: zoom out to second image
            settle_progress = (progress - 0.7) / 0.3
            zoom_factor = 4.2 - (3.2 * settle_progress)  # Zoom from 4.2x to 1x
            
            img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
            h, w = img2_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            M[0, 2] += (w - zoom_factor * w) / 2
            M[1, 2] += (h - zoom_factor * h) / 2
            
            zoomed = cv2.warpAffine(img2_cv, M, (w, h))
            
            # Reduce blur as we settle
            blur_amount = int(15 * (1 - settle_progress))
            if blur_amount > 0:
                zoomed = cv2.blur(zoomed, (blur_amount, blur_amount))
            
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
    
    def spiral_wipe_transition(self, img1, img2, progress, width, height):
        """Spiral wipe effect that reveals second image"""
        
        # Create a spiral mask
        center_x, center_y = width // 2, height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        # Create coordinate arrays
        y, x = np.ogrid[:height, :width]
        
        # Calculate distance and angle from center
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        angle = np.arctan2(y - center_y, x - center_x)
        
        # Normalize angle to 0-1
        angle_normalized = (angle + np.pi) / (2 * np.pi)
        
        # Create spiral pattern
        spiral_factor = 3  # Number of spiral arms
        spiral_angle = angle_normalized * spiral_factor
        
        # Calculate spiral progress
        spiral_progress = (distance / max_radius + spiral_angle) % 1
        
        # Create mask based on progress
        reveal_threshold = progress
        mask = spiral_progress < reveal_threshold
        
        # Apply mask
        result = np.array(img1)
        img2_array = np.array(img2)
        
        result[mask] = img2_array[mask]
        
        return Image.fromarray(result)
    
    def flip_3d_transition(self, img1, img2, progress, width, height):
        """3D flip effect like a card turning"""
        
        # Create 3D flip transformation
        img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
        
        if progress < 0.5:
            # First half: img1 flipping away
            flip_progress = progress * 2
            
            # Create perspective transformation
            scale_x = 1.0 - flip_progress
            if scale_x < 0.1:
                scale_x = 0.1
            
            # Create transformation matrix for horizontal flip
            src_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
            dst_points = np.float32([
                [width * (1 - scale_x) / 2, 0],
                [width * (1 + scale_x) / 2, 0],
                [width * (1 + scale_x) / 2, height],
                [width * (1 - scale_x) / 2, height]
            ])
            
            M = cv2.getPerspectiveTransform(src_points, dst_points)
            flipped = cv2.warpPerspective(img1_cv, M, (width, height))
            
            # Add shadow effect
            shadow_intensity = int(100 * flip_progress)
            flipped = cv2.subtract(flipped, np.full(flipped.shape, shadow_intensity, dtype=np.uint8))
            
            result = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        else:
            # Second half: img2 flipping in
            flip_progress = (progress - 0.5) * 2
            
            scale_x = flip_progress
            if scale_x < 0.1:
                scale_x = 0.1
            
            src_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
            dst_points = np.float32([
                [width * (1 - scale_x) / 2, 0],
                [width * (1 + scale_x) / 2, 0],
                [width * (1 + scale_x) / 2, height],
                [width * (1 - scale_x) / 2, height]
            ])
            
            M = cv2.getPerspectiveTransform(src_points, dst_points)
            flipped = cv2.warpPerspective(img2_cv, M, (width, height))
            
            # Add shadow effect (decreasing)
            shadow_intensity = int(100 * (1 - flip_progress))
            flipped = cv2.subtract(flipped, np.full(flipped.shape, shadow_intensity, dtype=np.uint8))
            
            result = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
    
    def lens_distortion_transition(self, img1, img2, progress, width, height):
        """Lens distortion effect like looking through a magnifying glass"""
        
        # Create circular distortion
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2
        
        # Create coordinate arrays
        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Create distortion effect
        distortion_radius = max_radius * progress
        
        result = np.array(img1)
        img2_array = np.array(img2)
        
        # Apply lens distortion
        mask = distance <= distortion_radius
        
        if np.any(mask):
            # Create magnification effect
            magnification = 1.5
            
            # Calculate new coordinates with distortion
            x_dist = center_x + (x - center_x) / magnification
            y_dist = center_y + (y - center_y) / magnification
            
            # Ensure coordinates are within bounds
            x_dist = np.clip(x_dist, 0, width - 1).astype(int)
            y_dist = np.clip(y_dist, 0, height - 1).astype(int)
            
            # Apply distortion to img2
            distorted_img2 = img2_array[y_dist, x_dist]
            
            # Blend with circular mask
            result[mask] = distorted_img2[mask]
        
        return Image.fromarray(result)
    
    def elastic_zoom_transition(self, img1, img2, progress, width, height):
        """Elastic zoom effect with bounce"""
        
        # Create elastic easing function
        def elastic_ease_out(t):
            if t == 0:
                return 0
            if t == 1:
                return 1
            
            p = 0.3
            s = p / 4
            return (2 ** (-10 * t)) * math.sin((t - s) * (2 * math.pi) / p) + 1
        
        if progress < 0.5:
            # Zoom in with elastic effect on img1
            zoom_progress = progress * 2
            elastic_factor = elastic_ease_out(zoom_progress)
            zoom_factor = 1.0 + (2.0 * elastic_factor)
            
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            h, w = img1_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            M[0, 2] += (w - zoom_factor * w) / 2
            M[1, 2] += (h - zoom_factor * h) / 2
            
            zoomed = cv2.warpAffine(img1_cv, M, (w, h))
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
        
        else:
            # Zoom out with elastic effect on img2
            zoom_progress = (progress - 0.5) * 2
            elastic_factor = 1 - elastic_ease_out(1 - zoom_progress)
            zoom_factor = 3.0 - (2.0 * elastic_factor)
            
            img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
            h, w = img2_cv.shape[:2]
            
            center_x, center_y = w // 2, h // 2
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            M[0, 2] += (w - zoom_factor * w) / 2
            M[1, 2] += (h - zoom_factor * h) / 2
            
            zoomed = cv2.warpAffine(img2_cv, M, (w, h))
            result = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result)
    
    def enhanced_smooth_fade(self, img1, img2, progress):
        """Enhanced smooth fade with subtle zoom"""
        # Add slight zoom during fade for more dynamic effect
        zoom_factor = 1.0 + (0.05 * math.sin(progress * math.pi))
        
        img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
        
        h, w = img1_cv.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Apply subtle zoom to both images
        M1 = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
        M1[0, 2] += (w - zoom_factor * w) / 2
        M1[1, 2] += (h - zoom_factor * h) / 2
        
        M2 = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
        M2[0, 2] += (w - zoom_factor * w) / 2
        M2[1, 2] += (h - zoom_factor * h) / 2
        
        zoomed1 = cv2.warpAffine(img1_cv, M1, (w, h))
        zoomed2 = cv2.warpAffine(img2_cv, M2, (w, h))
        
        # Blend with easing
        eased_progress = progress * progress * (3 - 2 * progress)
        blended = cv2.addWeighted(zoomed1, 1 - eased_progress, zoomed2, eased_progress, 0)
        
        result = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
        return Image.fromarray(result)
    
    def cinematic_wipe_transition(self, img1, img2, progress, width, height):
        """Cinematic wipe with directional motion blur"""
        # Create diagonal wipe with motion blur
        wipe_angle = 45  # degrees
        wipe_width = width * 0.2  # Width of the wipe transition
        
        # Create coordinate arrays
        y, x = np.ogrid[:height, :width]
        
        # Calculate diagonal distance
        diagonal_distance = (x * math.cos(math.radians(wipe_angle)) + 
                           y * math.sin(math.radians(wipe_angle)))
        
        # Normalize distance
        max_diagonal = (width * math.cos(math.radians(wipe_angle)) + 
                       height * math.sin(math.radians(wipe_angle)))
        
        normalized_distance = diagonal_distance / max_diagonal
        
        # Create wipe progress
        wipe_center = progress
        wipe_start = wipe_center - (wipe_width / max_diagonal)
        wipe_end = wipe_center + (wipe_width / max_diagonal)
        
        # Create masks
        mask_img1 = normalized_distance < wipe_start
        mask_img2 = normalized_distance > wipe_end
        mask_transition = ~(mask_img1 | mask_img2)
        
        result = np.array(img1)
        img2_array = np.array(img2)
        
        # Apply solid regions
        result[mask_img2] = img2_array[mask_img2]
        
        # Apply transition region with motion blur
        if np.any(mask_transition):
            transition_progress = ((normalized_distance[mask_transition] - wipe_start) / 
                                 (wipe_end - wipe_start))
            
            # Blend in transition region
            for i in range(3):  # RGB channels
                result[mask_transition, i] = (
                    img1.convert('RGB').split()[i].convert('L').point(lambda p: p).load()[0][0] * (1 - transition_progress) +
                    img2_array[mask_transition, i] * transition_progress
                ).astype(np.uint8)
        
        return Image.fromarray(result)
    
    def depth_push_transition(self, img1, img2, progress, width, height):
        """3D depth push effect like moving through space"""
        img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
        
        if progress < 0.5:
            # Push img1 away (shrink and fade)
            push_progress = progress * 2
            
            # Scale down and move back
            scale_factor = 1.0 - (0.8 * push_progress)
            alpha = 1.0 - push_progress
            
            # Create scaled version
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            if new_width > 0 and new_height > 0:
                scaled = cv2.resize(img1_cv, (new_width, new_height))
                
                # Create black background
                result = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Center the scaled image
                start_x = (width - new_width) // 2
                start_y = (height - new_height) // 2
                
                result[start_y:start_y + new_height, start_x:start_x + new_width] = scaled
                
                # Apply fade
                result = (result * alpha).astype(np.uint8)
            else:
                result = np.zeros((height, width, 3), dtype=np.uint8)
        
        else:
            # Pull img2 forward (grow and brighten)
            pull_progress = (progress - 0.5) * 2
            
            # Scale up from small
            scale_factor = 0.2 + (0.8 * pull_progress)
            alpha = pull_progress
            
            # Create scaled version
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            scaled = cv2.resize(img2_cv, (new_width, new_height))
            
            # Create black background
            result = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Center the scaled image
            start_x = (width - new_width) // 2
            start_y = (height - new_height) // 2
            
            result[start_y:start_y + new_height, start_x:start_x + new_width] = scaled
            
            # Apply brightness
            result = (result * alpha).astype(np.uint8)
        
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    
    def radial_blur_transition(self, img1, img2, progress, width, height):
        """Radial blur transition from center outward"""
        center_x, center_y = width // 2, height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        # Create coordinate arrays
        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Normalize distance
        normalized_distance = distance / max_radius
        
        # Create radial progress
        reveal_radius = progress
        
        # Create mask
        mask = normalized_distance <= reveal_radius
        
        result = np.array(img1)
        img2_array = np.array(img2)
        
        if progress < 0.5:
            # First half: apply radial blur to img1
            blur_progress = progress * 2
            
            # Apply increasing blur based on distance from center
            img1_cv = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
            
            # Create blur kernel size based on distance
            for r in range(0, int(max_radius), 10):
                ring_mask = (distance >= r) & (distance < r + 10)
                if np.any(ring_mask):
                    blur_amount = int((r / max_radius) * 15 * blur_progress)
                    if blur_amount > 0:
                        blurred_section = cv2.blur(img1_cv, (blur_amount, blur_amount))
                        img1_cv[ring_mask] = blurred_section[ring_mask]
            
            result = cv2.cvtColor(img1_cv, cv2.COLOR_BGR2RGB)
        
        else:
            # Second half: reveal img2 from center with decreasing blur
            reveal_progress = (progress - 0.5) * 2
            
            # Start with img1
            result = np.array(img1)
            
            # Reveal img2 in circular pattern
            reveal_mask = normalized_distance <= (reveal_progress * 1.2)
            result[reveal_mask] = img2_array[reveal_mask]
            
            # Apply edge blur for smooth transition
            edge_mask = ((normalized_distance <= (reveal_progress * 1.2 + 0.1)) & 
                        (normalized_distance > (reveal_progress * 1.2 - 0.1)))
            
            if np.any(edge_mask):
                # Smooth blend at edges
                blend_factor = 0.5
                result[edge_mask] = (result[edge_mask] * (1 - blend_factor) + 
                                   img2_array[edge_mask] * blend_factor).astype(np.uint8)
        
        return Image.fromarray(result)
    
    def vortex_spin_transition(self, img1, img2, progress, width, height):
        """Vortex spinning transition effect"""
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2
        
        # Create coordinate arrays
        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        angle = np.arctan2(y - center_y, x - center_x)
        
        # Create vortex effect
        spin_intensity = progress * 10  # Maximum spin amount
        
        # Calculate new angles with vortex distortion
        normalized_distance = np.clip(distance / max_radius, 0, 1)
        spin_amount = spin_intensity * (1 - normalized_distance) * progress
        
        new_angle = angle + spin_amount
        
        # Convert back to coordinates
        new_x = center_x + distance * np.cos(new_angle)
        new_y = center_y + distance * np.sin(new_angle)
        
        # Clip coordinates
        new_x = np.clip(new_x, 0, width - 1).astype(int)
        new_y = np.clip(new_y, 0, height - 1).astype(int)
        
        if progress < 0.5:
            # First half: spin img1
            img1_array = np.array(img1)
            result = np.zeros_like(img1_array)
            
            # Apply vortex distortion
            result[y.astype(int), x.astype(int)] = img1_array[new_y, new_x]
            
        else:
            # Second half: spin in img2
            img2_array = np.array(img2)
            
            # Reverse the spin for img2
            reverse_progress = 1 - ((progress - 0.5) * 2)
            reverse_spin = spin_intensity * (1 - normalized_distance) * reverse_progress
            reverse_angle = angle - reverse_spin
            
            reverse_x = center_x + distance * np.cos(reverse_angle)
            reverse_y = center_y + distance * np.sin(reverse_angle)
            
            reverse_x = np.clip(reverse_x, 0, width - 1).astype(int)
            reverse_y = np.clip(reverse_y, 0, height - 1).astype(int)
            
            result = np.zeros_like(img2_array)
            result[y.astype(int), x.astype(int)] = img2_array[reverse_y, reverse_x]
        
        return Image.fromarray(result)

# Global instance
cinematic_transitions = CinematicTransitions()

def create_transition_frames(base_dir, from_segment, to_segment, transition_type, duration, width, height):
    """
    Main function to create cinematic transition frames
    This replaces your existing transitions.py function
    """
    return cinematic_transitions.create_transition_frames(
        base_dir, from_segment, to_segment, transition_type, duration, width, height
    )

# Available transition types for your scripts
AVAILABLE_TRANSITIONS = [
    # Dynamic zoom effects
    "zoom_in_out",      # Zoom into first image, zoom out to reveal second
    "zoom_burst",       # Explosive zoom with radial burst effect  
    "elastic_zoom",     # Zoom with elastic bounce effect
    
    # Pan and camera movement
    "pan_zoom",         # Pan across image while zooming
    "depth_push",       # 3D depth effect like moving through space
    
    # Rotation effects  
    "rotate_zoom",      # Rotate and zoom simultaneously
    "vortex_spin",      # Vortex spinning distortion
    
    # Creative wipes
    "spiral_wipe",      # Spiral pattern reveal
    "cinematic_wipe",   # Diagonal wipe with motion blur
    "radial_blur",      # Circular blur transition from center
    
    # 3D effects
    "3d_flip",          # Card flip effect in 3D space
    "lens_distortion",  # Magnifying glass distortion effect
    
    # Enhanced basics
    "enhanced_fade",    # Smooth fade with subtle zoom
]

def get_random_cinematic_transition():
    """Get a random cinematic transition for variety"""
    return random.choice(AVAILABLE_TRANSITIONS)

def get_transition_for_mood(mood="dynamic"):
    """Get appropriate transition based on mood/style"""
    
    mood_transitions = {
        "dynamic": ["zoom_burst", "rotate_zoom", "pan_zoom", "vortex_spin"],
        "smooth": ["enhanced_fade", "zoom_in_out", "elastic_zoom"],
        "dramatic": ["3d_flip", "depth_push", "radial_blur"],
        "creative": ["spiral_wipe", "lens_distortion", "cinematic_wipe"],
        "professional": ["pan_zoom", "zoom_in_out", "enhanced_fade", "cinematic_wipe"]
    }
    
    return random.choice(mood_transitions.get(mood, mood_transitions["dynamic"]))

# Example usage in your script:
"""
# In your main script, replace transition types with:

segments = [
    {
        "text": "Welcome to Japan!",
        "transition": "zoom_burst",  # Explosive effect
        # ... other properties
    },
    {
        "text": "Exploring Kyoto...", 
        "transition": "pan_zoom",    # Cinematic pan
        # ... other properties
    },
    {
        "text": "Amazing temples!",
        "transition": "3d_flip",     # Card flip effect
        # ... other properties  
    }
]

# Or use automatic selection:
transition_type = get_transition_for_mood("dramatic")
transition_type = get_random_cinematic_transition()
"""

print("🎬 Advanced Cinematic Transitions System Loaded!")
print(f"✨ Available Effects: {len(AVAILABLE_TRANSITIONS)} professional transitions")
print("🚀 Features: Zoom, Pan, Rotate, 3D Effects, Creative Wipes, and more!")
print("💡 Use get_transition_for_mood() or get_random_cinematic_transition() for variety")
