"""
Grok API integration for generating custom narrative scripts based on user prompts.
"""

import requests
import json
import time
import random

# API Key for Grok API
GROK_API_KEY = "api_key_here"

def generate_story_script(story_topic, audience="general", duration_minutes=1, num_segments=8):
    """
    Generate a narrative story script using Grok API based on user prompt
    
    Parameters:
    - story_topic: Story theme or topic from user input
    - audience: Target audience ("children", "adult", "general")
    - duration_minutes: Target duration in minutes
    - num_segments: Number of video segments to create (fixed at 8 for 1-minute videos)
    
    Returns:
    - Dictionary with script data structure
    """
    print(f"Generating a {duration_minutes} minute {audience}-friendly narrative about '{story_topic}' with {num_segments} segments...")
    
    # Calculate segment duration based on total video length
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Adjust prompt based on audience
    audience_prompt = ""
    if audience == "children":
        audience_prompt = "Make it child-friendly, educational, and engaging for young viewers."
    elif audience == "adult":
        audience_prompt = "Make it sophisticated with mature themes appropriate for adult viewers."
    else:
        audience_prompt = "Make it suitable for a general audience, enjoyable for both children and adults."
    
    # Format prompt for Grok API
    prompt = f"""
    Create a script for a {duration_minutes} minute narrative video about "{story_topic}".
    
    The script should tell a cohesive story with exactly {num_segments} segments, each around {int(segment_seconds)} seconds long.
    {audience_prompt}
    
    For each segment, provide:
    1. A brief caption text (15-25 words) that would appear on screen
    2. A detailed image prompt for generating visuals (good for AI image generation)
    3. A suggested camera motion effect (zoom in, pan, drift, etc.)
    
    Format the response as a JSON object with the following structure:
    {{
      "title": "Narrative Story Title",
      "style": "brief style description",
      "aspect_ratio": "9:16",
      "segments": [
        {{
          "text": "Caption text to appear on screen",
          "text_overlay": true,
          "text_style": "modern",
          "duration_seconds": {int(segment_seconds)},
          "image_prompt": "Detailed image generation prompt",
          "zoom_direction": "in/out/pan/etc",
          "transition": "smooth_fade/slide_up/etc",
          "subtitle_mode": true
        }},
        // Additional segments...
      ]
    }}
    
    Make it engaging and suitable for a vertical video format (9:16 aspect ratio) for Instagram Reels.
    Each segment should flow naturally to the next, telling a cohesive narrative about {story_topic}.
    """
    
    try:
        # Call Grok API
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROK_API_KEY}"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a professional narrative scriptwriter for short videos. You create engaging {audience}-friendly stories that flow well in short format videos."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "grok-3-latest",
            "stream": False,
            "temperature": 0.7  # Some creativity but still structured
        }
        
        # Make the API call
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"Error calling Grok API: {response.status_code}")
            print(f"Response: {response.text}")
            return fallback_script(story_topic, audience, duration_minutes, num_segments)
            
        # Parse response
        result = response.json()
        script_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract JSON from the response text
        script_json = extract_json_from_text(script_text)
        if not script_json:
            print("Could not extract valid JSON from Grok response")
            return fallback_script(story_topic, audience, duration_minutes, num_segments)
            
        print("Successfully generated narrative script!")
        return script_json
        
    except Exception as e:
        print(f"Error generating script with Grok API: {e}")
        return fallback_script(story_topic, audience, duration_minutes, num_segments)

def extract_json_from_text(text):
    """Extract JSON object from text that might contain markdown and other content"""
    try:
        # Find content between curly braces
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            return None
            
        json_str = text[start_idx:end_idx+1]
        
        # Parse JSON
        script_data = json.loads(json_str)
        return script_data
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        
        # Try another approach - look for JSON with regex
        import re
        try:
            match = re.search(r'```json\n(.*?)```', text, re.DOTALL)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
        except:
            pass
            
        return None

def fallback_script(story_topic, audience="general", duration_minutes=1, num_segments=8):
    """Generate a fallback script if the API call fails"""
    print("Using fallback script generator...")
    
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Create a title based on story topic
    title = f"The Story of {story_topic}"
    
    # Different transition types
    transitions = ["smooth_fade", "slide_up", "color_pulse", "slide_left", "whip_pan", "gradient_wipe"]
    
    # Different motion types
    motions = ["in", "forward_push", "slow_pan", "gentle_zoom_out", "drift", "gentle_pulse", "looking_up", "focus_in"]
    
    # Create segments based on common narrative patterns
    segments = []
    
    # Structure based on the classic Hero's Journey for narratives
    narrative_patterns = []
    
    if audience == "children":
        # Child-friendly narrative patterns
        narrative_patterns = [
            {
                "text": f"Once upon a time, in a world full of wonder, there was {story_topic}",
                "image_prompt": f"Magical storybook opening with '{story_topic}' illustrated in a colorful, child-friendly style, soft dreamy lighting, vertical 9:16 format",
                "zoom_direction": "gentle_zoom_out"
            },
            {
                "text": f"Every day was full of joy and happiness, until one day something unexpected happened",
                "image_prompt": f"Bright sunny day scene related to {story_topic} suddenly interrupted by a dramatic (but not scary) change, child-friendly illustration style, vertical 9:16 format",
                "zoom_direction": "in"
            },
            {
                "text": f"Our friend didn't know what to do, but decided to be brave and face the challenge",
                "image_prompt": f"Character from {story_topic} looking determined and brave, standing tall against a background suggesting challenge, child-friendly style, vertical 9:16 format",
                "zoom_direction": "forward_push"
            },
            {
                "text": f"Along the way, new friends appeared, offering help and wisdom",
                "image_prompt": f"Group of friendly character designs related to {story_topic}, diverse, supportive poses, sharing wisdom, warm colors, vertical 9:16 format",
                "zoom_direction": "slow_pan"
            },
            {
                "text": f"Together they discovered a special place where solutions could be found",
                "image_prompt": f"Magical discovery scene related to {story_topic}, characters finding a special location with glowing elements, awe on their faces, vertical 9:16 format",
                "zoom_direction": "gentle_pulse"
            },
            {
                "text": f"The biggest challenge was right ahead, but they were prepared to face it",
                "image_prompt": f"Characters from {story_topic} approaching a big (but not scary) obstacle, determined expressions, teamwork evident, dramatic but child-friendly, vertical 9:16 format",
                "zoom_direction": "looking_up"
            },
            {
                "text": f"Working together with courage and kindness, they overcame the challenge",
                "image_prompt": f"Triumphant moment showing characters from {story_topic} successfully overcoming obstacle with teamwork, celebration poses, bright colors, vertical 9:16 format",
                "zoom_direction": "focus_in"
            },
            {
                "text": f"And they all returned home, changed for the better by their adventure",
                "image_prompt": f"Happy ending scene with characters from {story_topic} returning home transformed, sharing what they learned, sunset colors, peaceful resolution, vertical 9:16 format",
                "zoom_direction": "gentle_zoom_out"
            }
        ]
    elif audience == "adult":
        # More mature narrative patterns
        narrative_patterns = [
            {
                "text": f"They say every story has a beginning. This one starts with {story_topic}",
                "image_prompt": f"Atmospheric establishing shot related to {story_topic}, cinematic lighting, moody color grading, sophisticated composition, vertical 9:16 format",
                "zoom_direction": "slow_pan"
            },
            {
                "text": f"Beneath the surface, tensions were building that would soon change everything",
                "image_prompt": f"Subtle visual metaphor showing building tension related to {story_topic}, contrast between light and shadow, foreboding atmosphere, vertical 9:16 format",
                "zoom_direction": "gentle_pulse"
            },
            {
                "text": f"The moment of truth arrived without warning, forcing a critical decision",
                "image_prompt": f"Dramatic pivotal moment related to {story_topic}, character at crossroads, powerful emotional framing, strong directional lighting, vertical 9:16 format",
                "zoom_direction": "in"
            },
            {
                "text": f"Sometimes the hardest path forward is the only one worth taking",
                "image_prompt": f"Visual metaphor of difficult journey related to {story_topic}, character facing hardship with determination, cinematic composition, vertical 9:16 format",
                "zoom_direction": "forward_push"
            },
            {
                "text": f"In the darkest moments, unexpected allies emerged from the shadows",
                "image_prompt": f"Dramatic scene of unexpected support related to {story_topic}, meeting of characters in atmospheric lighting, emotional connection moment, vertical 9:16 format",
                "zoom_direction": "looking_up"
            },
            {
                "text": f"The confrontation that had been brewing was now inevitable",
                "image_prompt": f"Tense confrontation scene related to {story_topic}, dramatic composition with opposing forces, high contrast lighting, emotional intensity, vertical 9:16 format",
                "zoom_direction": "slow_pan"
            },
            {
                "text": f"Victory came at a cost, but revealed a truth that had been hidden all along",
                "image_prompt": f"Aftermath of climactic scene related to {story_topic}, character processing revelation, visual symbolism of truth revealed, moody lighting, vertical 9:16 format",
                "zoom_direction": "gentle_zoom_out"
            },
            {
                "text": f"Some journeys end where they began, but nothing is ever the same again",
                "image_prompt": f"Full circle moment related to {story_topic}, character transformed by experience, visual parallel to opening scene but with significant changes, vertical 9:16 format",
                "zoom_direction": "drift"
            }
        ]
    else:
        # General audience narrative patterns
        narrative_patterns = [
            {
                "text": f"The story of {story_topic} begins in a moment of ordinary life",
                "image_prompt": f"Everyday scene establishing {story_topic}, relatable moment, warm natural lighting, balanced composition, vertical 9:16 format",
                "zoom_direction": "gentle_zoom_out"
            },
            {
                "text": f"But soon, an unexpected challenge appeared, changing everything",
                "image_prompt": f"Moment of interruption or change related to {story_topic}, visible shift in mood or setting, dramatic but not frightening, vertical 9:16 format",
                "zoom_direction": "in"
            },
            {
                "text": f"Facing uncertainty, the first steps of a journey began",
                "image_prompt": f"Character or subject from {story_topic} at the beginning of a journey, standing at threshold, mix of determination and uncertainty, vertical 9:16 format",
                "zoom_direction": "forward_push"
            },
            {
                "text": f"Along the way, new perspectives emerged from unexpected places",
                "image_prompt": f"Scene of discovery or meeting related to {story_topic}, moment of connection or insight, interesting visual angle, vertical 9:16 format",
                "zoom_direction": "slow_pan"
            },
            {
                "text": f"The greatest challenges often reveal our hidden strengths",
                "image_prompt": f"Character or subject from {story_topic} facing obstacle with newly discovered resources or abilities, moment of empowerment, vertical 9:16 format",
                "zoom_direction": "looking_up"
            },
            {
                "text": f"Sometimes, the most important battles are the ones we fight within",
                "image_prompt": f"Introspective moment related to {story_topic}, visual representation of internal conflict or decision, symbolic imagery, atmospheric lighting, vertical 9:16 format",
                "zoom_direction": "gentle_pulse"
            },
            {
                "text": f"With courage and perseverance, even the impossible becomes possible",
                "image_prompt": f"Triumphant moment related to {story_topic}, overcoming significant obstacle, visual payoff to earlier challenges, hopeful imagery, vertical 9:16 format",
                "zoom_direction": "focus_in"
            },
            {
                "text": f"The end of one story is often just the beginning of another",
                "image_prompt": f"Resolution scene related to {story_topic} that also hints at new possibilities, character looking toward horizon or new challenge, hopeful ending, vertical 9:16 format",
                "zoom_direction": "drift"
            }
        ]
    
    # Select segments based on the narrative patterns
    selected_patterns = narrative_patterns[:num_segments] if num_segments <= len(narrative_patterns) else random.sample(narrative_patterns, min(num_segments, len(narrative_patterns)))
    
    # Create actual segments
    for i, pattern in enumerate(selected_patterns):
        segment = {
            "text": pattern["text"],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "image_prompt": pattern["image_prompt"],
            "zoom_direction": pattern["zoom_direction"],
            "transition": transitions[i % len(transitions)],
            "subtitle_mode": True
        }
        segments.append(segment)
    
    # Assemble the script
    story_script = {
        "title": title,
        "style": f"narrative, engaging, {audience}-friendly",
        "aspect_ratio": "9:16",
        "segments": segments
    }
    
    return story_script

def get_user_story_prompt():
    """Get user input for narrative story topic and target audience"""
    print("\n===== Narrative Video Generator =====")
    story_topic = input("\nWhat story topic or theme would you like for your video? (e.g., 'A hero's journey', 'Friendship', 'Overcoming fear'): ")
    
    print("\nChoose a target audience for your story:")
    print("1. Children (child-friendly, educational)")
    print("2. Adults (mature themes, sophisticated)")
    print("3. General (suitable for all ages)")
    
    audience_choice = input("Enter choice (1-3), or press Enter for default (General): ")
    
    if audience_choice == "1":
        audience = "children"
    elif audience_choice == "2":
        audience = "adult"
    else:
        audience = "general"
    
    duration = input("\nHow long should the video be? (in minutes, press Enter for 1 minute): ")
    try:
        duration_minutes = float(duration) if duration.strip() else 1.0
    except:
        duration_minutes = 1.0
    
    # Fixed at 8 segments for 1-minute video
    num_segments = 8
    
    return story_topic, audience, duration_minutes, num_segments

# For testing
if __name__ == "__main__":
    story_topic, audience, duration, num_segments = get_user_story_prompt()
    script = generate_story_script(story_topic, audience, duration, num_segments)
    print(json.dumps(script, indent=2))