# Instagram Reels Generator

Create professional Instagram Reels-style videos with AI-powered narratives, voice-over, and dynamic visual effects.

## What This Tool Does

This system generates complete Instagram Reels videos from simple story prompts. You provide a story idea, and it creates custom scripts, generates AI images, adds professional voice narration, applies cinematic effects, and outputs a polished video ready for social media.

## Getting Started

### Requirements

Install these system dependencies first:

```bash
brew install ffmpeg
```

For Linux:
```bash
sudo apt-get install ffmpeg
```

Install Python packages:
```bash
pip install torch torchvision diffusers transformers
pip install pillow numpy opencv-python pyttsx3 pydub
pip install requests tqdm huggingface_hub
```

### Running the Generator

Start the video creation process:

```bash
python reel_generator_custom.py
```

Follow the interactive prompts to create your video.

## File Structure Guide

### Main Entry Points

**reel_generator_custom.py**
- Primary script you always run
- Handles user input for story creation
- Manages the complete video generation pipeline
- Integrates all components into one smooth workflow

**main_pyttsx3.py**
- Core video generation engine
- Processes custom scripts into final videos
- Handles audio-visual synchronization
- Called automatically by the custom generator

**main.py**
- Alternative version using different APIs
- Contains hardcoded travel story examples
- Less flexible than the custom generator

### Visual Effects and Motion

**enhanced_motion.py**
- Creates professional camera movement effects
- Includes zoom, pan, drift, and pulse motions
- Generates 30fps smooth animations
- Applies motion before adding captions for stability

**motion_effects.py**
- Basic version of motion effects
- Simpler camera movements
- Used as backup system

**image_effects.py**
- Instagram-style photo filters
- Color grading and enhancement
- Text overlay with multiple styles
- Professional visual polish

### Captions and Transitions

**enhanced_captions.py**
- Professional subtitle system
- Fixed positioning during camera movements
- Broadcast-quality text rendering
- Optimized for vertical video format

**transitions.py**
- Cinematic scene transitions
- Multiple transition types available
- Creates smooth 0.5-second transitions
- Professional quality effects

**fixed_caption_transitions.py**
- Maintains caption consistency during transitions
- Prevents text flickering or movement
- Specialized transition handling

### Audio and Speech

**pyttsx3_integration.py**
- Primary text-to-speech system
- Works across different operating systems
- Adjusts speech rate to match video timing
- Creates fallback audio when needed

**grok_integration.py**
- Alternative speech system using external APIs
- Enhanced narration generation
- Professional voice options

### Content Generation

**grok_script_generator.py**
- Creates custom story scripts from user prompts
- Uses AI to generate narrative structures
- Handles different audience types
- Creates fallback scripts when APIs unavailable

**image_generation.py**
- Generates images using Stable Diffusion
- Creates vertical format visuals
- Applies automatic filtering
- Provides placeholder images as backup

### Video Assembly

**enhanced_video_assembly.py**
- Combines all elements into final video
- Handles precise audio synchronization
- Manages multi-track audio mixing
- Creates professional video output

**video_assembly.py**
- Basic video compilation functions
- Frame sequence management
- Audio overlay capabilities

### Support Files

**utils.py**
- Helper functions for file management
- Duration calculation tools
- Directory organization utilities

**professional_transitions.py**
- Advanced transition algorithms
- Mathematical motion curves
- Professional visual effects

## How to Create Videos

### Basic Workflow

Run the main script and follow these steps:

1. Enter your story topic when prompted
2. Choose your target audience
3. Set video duration preferences
4. Wait for the system to generate content
5. Find your completed video in the main directory

### Story Topic Examples

Good story prompts work best:
- A hero discovering their true calling
- Overcoming fear through friendship
- A journey of self-discovery
- Learning to trust others
- Finding courage in difficult times

### Audience Options

**Children**
- Simple language and concepts
- Educational and positive themes
- Bright, engaging visuals

**Adults**
- Complex narratives and themes
- Sophisticated visual treatment
- Mature storytelling approaches

**General**
- Balanced content for all ages
- Universal themes and messages
- Broad appeal styling

## Output and Results

### Video Specifications

Your final videos will have these properties:
- 9:16 vertical aspect ratio perfect for Instagram Reels
- 30 frames per second for smooth playback
- Professional subtitle overlays
- Synchronized audio narration
- Cinematic visual effects

### File Organization

The system creates organized folders:
- Generated scripts and story content
- AI-created images for each scene
- Individual video frames with effects
- Transition sequences between scenes
- Audio files and final soundtrack
- Complete video ready for upload

### Motion Effects Available

- Zoom in for dramatic emphasis
- Forward push with upward motion
- Horizontal panning across scenes
- Gentle zoom out for reveals
- Upward tilt for inspiration
- Diagonal drift for movement
- Breathing pulse for life
- Focus effects for attention

### Transition Styles

- Smooth cross-fade between scenes
- Slide transitions in multiple directions
- Color pulse through white flash
- Raindrop wipe effects
- Motion blur whip pans
- Gradient wipe transitions

### Visual Filters

- Natural clean appearance
- Warm travel photography style
- Moody cinematic color grading
- Nostalgic film-like treatment
- Golden hour enhancement

## Configuration Options

### API Setup

Add your API keys to the appropriate files for enhanced features:
- Grok API for advanced script generation
- Hugging Face for image generation
- Optional Speechify for premium voices

### Customization

Modify settings in the respective files:
- Adjust motion intensity and duration
- Change color grading preferences
- Modify transition timing
- Customize caption styling

## Troubleshooting

### Common Solutions

**FFMPEG Issues**
- Ensure FFMPEG is properly installed
- Check system PATH includes FFMPEG location
- Try reinstalling with package manager

**Voice Generation Problems**
- System automatically creates silent audio as backup
- Check microphone permissions if needed
- Try different voice settings

**Image Generation Failures**
- System uses colored placeholder images
- Ensure adequate system memory
- Close other applications during generation

**Performance Optimization**
- Use CPU mode for compatibility
- Ensure sufficient storage space
- Close unnecessary programs during generation

### Technical Requirements

- Minimum 4GB RAM recommended
- 2GB free storage per video
- Stable internet for API features
- Modern processor for reasonable speed

## Advanced Usage

### Manual Script Creation

Create custom scripts using JSON format with these elements:
- Story title and style description
- Individual segment information
- Image generation prompts
- Motion and transition preferences
- Timing and duration settings

### Batch Processing

Process multiple videos by:
- Preparing multiple story prompts
- Running the generator sequentially
- Organizing output files systematically

### Quality Settings

Adjust output quality by modifying:
- Frame rate preferences
- Image resolution settings
- Audio quality parameters
- Compression settings

## Tips for Best Results

### Story Creation

- Be specific but not overly narrow in prompts
- Focus on universal themes and emotions
- Consider your target audience carefully
- Keep narratives engaging and concise

### Technical Considerations

- Run generation during off-peak hours for better API responses
- Ensure stable internet connection throughout process
- Monitor system resources during generation
- Keep adequate storage space available

### Content Strategy

- Create series of related videos for consistency
- Vary visual styles and transitions
- Consider seasonal or trending topics
- Plan content calendars around generation time
