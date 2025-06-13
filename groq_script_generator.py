"""
Complete Groq API integration for generating custom narrative scripts based on user prompts.
This version handles both simple topics and complex professional creative briefs.
"""

import requests
import json
import time
import random
import os
import datetime
from groq import Groq

# API Key for Groq API
GROQ_API_KEY = "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"
# Initialize Groq client
GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)


def write_output_to_file(content, label="output"):
    """Write content to a timestamped txt file in an outputs directory."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = "groq_outputs"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{label}_{timestamp}.txt"
    filepath = os.path.join(out_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] {label} written to {filepath}")
    return filepath

def generate_brand_brief(product_name_or_complex_topic, duration_minutes, num_segments, segment_seconds):
    """
    LLM1: Research Agent - Generates a detailed brand brief.
    """
    prompt = f"""Analyze '{product_name_or_complex_topic}' for a {duration_minutes*60}-second commercial/video creation, structured into {num_segments} segments of approximately {segment_seconds} seconds each.

    Research Output Required (Advertising Brief Format):
    - Title: A concise and catchy title for the campaign/video.
    - Style: Suggested overall style (e.g., "cinematic heartfelt narrative", "energetic product showcase", "inspirational mini-documentary").
    - Core Brand/Topic Values: 3-5 bullet points describing the core message or values to convey. Include an emotional impact score (1-10) for each.
    - Target Demographics: Describe the primary target audience (age ranges, key psychographics, relevant interests, or spending patterns if applicable).
    - Competitive Differentiation/Unique Angle: 3 unique selling propositions or unique aspects of the topic that make it stand out.
    - Visual Identity Cues: Suggest 5 HEX color codes relevant to the brand/topic with brief psychological associations (e.g., #FFD700 - Gold: optimism, warmth).
    - Emotional Tone Matrix: Define the desired emotional journey or overall tone (e.g., excitement: 0-10, trust: 0-10, urgency: 0-10, inspiration: 0-10, humor: 0-10).
    - Scene Architecture: Outline {num_segments} distinct scenes. For each scene, specify its purpose (e.g., "Introduction", "Problem Setup", "Solution Reveal", "Benefit Showcase", "Call to Action") and a suggested transition type to the next scene (e.g., "smooth_fade", "slide_left", "whip_pan"). Each scene should be approximately {segment_seconds} seconds.

    Format the entire output as a structured advertising brief. This brief will be used by a creative agent to generate a full video script.
    Ensure all requested sections are thoroughly addressed with measurable parameters where applicable."""

    print(f"LLM1 (Research Agent): Generating brand brief for '{product_name_or_complex_topic}'...")
    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama3-70b-8192", # Research model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,        # Lower temperature for factual research
            max_tokens=2048
        )
        brief_content = response.choices[0].message.content
        write_output_to_file(brief_content, label="llm1_brand_brief")
        print("LLM1 (Research Agent): Brand brief generated.")
        # print(f"LLM1 Output (Brief):\n{brief_content}\n") # Optional: for debugging
        return brief_content
    except Exception as e:
        print(f"Error calling Groq API (LLM1 - Research Agent): {e}")
        return None

def create_script_treatment(brief, segment_seconds, num_segments):
    """
    LLM2: Creative Treatment Generator - Transforms the brief into a script.
    """
    creative_prompt = f"""Transform this comprehensive advertising brief into a compelling {int(segment_seconds * num_segments)}-second video script consisting of exactly {num_segments} segments.

    ADVERTISING BRIEF:
    {brief}

    Creative Requirements:
    - Adhere strictly to the number of segments ({num_segments}) and approximate duration per segment ({segment_seconds} seconds) outlined in the brief's Scene Architecture.
    - Develop a fresh, unconventional creative treatment based on the brief.
    - For each of the {num_segments} scenes, provide a detailed scene-by-scene breakdown. Each scene must include:
      * "text": Exact voiceover/caption text for the segment (15-30 words, engaging and relevant to the scene's purpose from the brief).
      * "image_prompt": Precise visual descriptions suitable for an AI image generator (cinematic quality, detailed elements, mood, and ensuring it aligns with the scene's purpose and visual identity cues from the brief). Specify vertical 9:16 format.
      * "camera_specifications": Suggested camera shot (e.g., "wide shot establishing location", "medium close-up on character's face", "dynamic tracking shot") and camera movement (e.g., "slow zoom in", "pan right", "static").
      * "lighting_requirements": Brief description of lighting style (e.g., "bright and airy", "dramatic low-key", "golden hour", "Arri Alexa style soft cinematic").
      * "transition_to_next": The transition effect to the next scene (should match the transition type suggested in the brief's Scene Architecture for this scene). For the last segment, this can be "ends".

    Style Parameters (interpret creatively):
    - Stylization: 300 (aim for high visual impact and a polished, professional look)
    - Weirdness: 0 (ensure the treatment is commercially appropriate and aligns with the brief's tone)
    - Variety: 50 (provide balanced visual diversity across scenes, avoiding monotony)

    Output Format:
    Respond with ONLY a valid JSON object. The JSON structure should be:
    {{
      "title": "Extracted or creatively derived Campaign Title from Brief",
      "style": "Extracted or creatively derived video style from Brief (e.g., cinematic commercial narrative)",
      "aspect_ratio": "9:16",
      "segments": [
        {{
          "text": "Exact voiceover/caption text for segment 1 (15-30 words)",
          "text_overlay": true,
          "text_style": "modern", // Default, can be refined later
          "duration_seconds": {segment_seconds}, // Use the segment_seconds value
          "image_prompt": "Detailed, cinematic scene description for segment 1, vertical 9:16 format, reflecting brief's visual identity and scene purpose. Include camera_specifications and lighting_requirements implicitly or explicitly here.",
          "zoom_direction": "Derived from camera_specifications (e.g., 'slow_zoom_in', 'pan_right', 'static')", // Or a more general Ken Burns effect like 'in', 'out', 'pan'
          "transition": "Transition effect to next segment (from brief's Scene Architecture)",
          "subtitle_mode": true
        }}
        // ... (repeat for all {num_segments} segments)
      ]
    }}
    CRITICAL: Ensure the "image_prompt" for each segment is rich and descriptive, incorporating the camera and lighting details. The "zoom_direction" should be a simplified Ken Burns style effect based on the camera movement. The "transition" must match the brief.
    """
    print(f"LLM2 (Creative Agent): Generating script treatment from brief...")
    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama3-8b-8192", # Creative model (alternative to decommissioned Mixtral)
            messages=[{"role": "user", "content": creative_prompt}],
            temperature=0.8,          # Higher temperature for creativity
            max_tokens=3500           # Increased to accommodate detailed JSON for 8 segments
        )
        script_content = response.choices[0].message.content
        write_output_to_file(script_content, label="llm2_script_treatment")
        print("LLM2 (Creative Agent): Script treatment generated.")
        # print(f"LLM2 Output (Script Treatment):\n{script_content}\n") # Optional: for debugging
        return script_content
    except Exception as e:
        print(f"Error calling Groq API (LLM2 - Creative Agent): {e}")
        return None

def generate_story_script(story_topic, audience="general", duration_minutes=1, num_segments=8):
    """
    Generate a narrative story script using Groq API based on user prompt
    
    Parameters:
    - story_topic: Story theme, topic, or complete creative brief from user input
    - audience: Target audience ("children", "adult", "general")
    - duration_minutes: Target duration in minutes
    - num_segments: Number of video segments to create (fixed at 8 for 1-minute videos)
    
    Returns:
    - Dictionary with script data structure
    """
    print(f"Generating a {duration_minutes} minute {audience}-friendly narrative about '{story_topic[:50]}...' with {num_segments} segments...")
    
    # Calculate segment duration based on total video length
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Determine if this is a simple topic or a complex creative brief (potential product/brand)
    is_complex_brief = detect_complex_brief(story_topic)
    
    try:
        script_text = None
        if is_complex_brief:
            # --- New Two-Agent Pipeline for Complex Briefs/Products ---
            print("Using Advanced Two-Agent Pipeline for script generation...")
            # Agent 1: Generate Brand Brief
            brand_brief = generate_brand_brief(story_topic, duration_minutes, num_segments, segment_seconds)
            if not brand_brief:
                print("Failed to generate brand brief from LLM1. Using fallback script.")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback

            # Agent 2: Create Script Treatment from Brief
            # Pass segment_seconds and num_segments to ensure LLM2 adheres to the structure
            script_text = create_script_treatment(brand_brief, segment_seconds, num_segments)
            if not script_text:
                print("Failed to generate script treatment from LLM2. Using fallback script.")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback
        else:
            # --- Existing Single-Agent Pipeline for Simple Topics ---
            print("Using Single-Agent Pipeline for simple topic script generation...")
            prompt = create_topic_focused_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds)
            system_message = create_system_message(story_topic, audience, is_complex_brief=False)
            
            # Using the requests-based API call for the existing path
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "model": "meta-llama/llama-4-scout-17b-16e-instruct", # Existing model for this path
                # "model": "llama3-8b-8192", # Alternative: could use Llama 3 8B for faster simple topics
                "temperature": 0.8,
                "max_tokens": 3000,
                "top_p": 0.9
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                print(f"Error calling Groq API (Single-Agent): {response.status_code}")
                print(f"Response: {response.text}")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback
            
            result = response.json()
            script_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            write_output_to_file(script_text, label="single_agent_script_raw")

        if not script_text:
            print("Empty response from Groq API.")
            fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
            write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
            return fallback

        # Extract JSON from the response text (common for both pipelines)
        script_json = extract_json_from_text(script_text)
        if not script_json:
            print("Could not extract valid JSON from Groq response.")
            print(f"Raw response preview: {script_text[:500]}...")
            fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
            write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
            return fallback
            
        # Validate and enhance the script
        enhanced_script = validate_and_enhance_script(script_json, story_topic, audience)
        write_output_to_file(json.dumps(enhanced_script, indent=2), label="final_script_json")
        print("Successfully generated narrative script with Groq API!")
        return enhanced_script
        
    except requests.exceptions.RequestException as e:
        print(f"Network error generating script with Groq API: {e}")
        fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
        write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
        return fallback
    except Exception as e:
        print(f"Overall error in generate_story_script: {e}")
        fallback = fallback_script(story_topic, audience, duration_minutes, num_segments)
        write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
        return fallback

def detect_complex_brief(story_topic):
    """Detect if the input is a complex creative brief or simple topic"""
    topic_lower = story_topic.lower()
    
    # Indicators of complex creative brief
    complex_indicators = [
        'campaign', 'promo', 'commercial', 'brand', 'launch', 'product',
        'should begin with', 'should end with', 'follow multiple', 'the final scene',
        'introducing', 'tagline', 'mission', 'brand message', 'audience should',
        'tone should be', 'visual style', 'call to action', 'marketing',
        'advertisement', 'showcase', 'demonstrate', 'highlight', 'promote'
    ]
    
    # Check length (complex briefs are usually longer)
    if len(story_topic) > 200:
        return True
    
    # Check for complex indicators
    return any(indicator in topic_lower for indicator in complex_indicators)

def create_professional_brief_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds):
    """Create prompt for professional creative briefs"""
    return f"""You are a world-class creative director working on a premium video campaign. 

CREATIVE BRIEF: {story_topic}

TARGET AUDIENCE: {audience}
VIDEO SPECS: {duration_minutes} minute video, {num_segments} segments of {int(segment_seconds)} seconds each

Your task is to transform this creative brief into a cinematic narrative script that tells a compelling story while achieving the campaign objectives.

REQUIREMENTS:
- Extract key story beats from the brief and distribute across {num_segments} segments
- Create specific character arcs that serve the narrative
- Design each segment to build toward the campaign's climactic moment
- Include detailed, cinematic image descriptions for each scene
- Ensure the pacing builds emotional and visual stakes
- Make each segment visually distinct and cinematically engaging
- Include specific details that bring the brief to life

FORMAT: Respond with ONLY valid JSON:
{{
  "title": "Campaign Title from Brief",
  "style": "cinematic commercial narrative about [main campaign theme]",
  "aspect_ratio": "9:16",
  "segments": [
    {{
      "text": "Compelling caption (15-25 words) that advances the campaign story",
      "text_overlay": true,
      "text_style": "modern",
      "duration_seconds": {int(segment_seconds)},
      "image_prompt": "Highly detailed, cinematic scene description that serves the campaign narrative, professional video production quality, vertical 9:16 format. Incorporate camera specifications and lighting requirements here.",
      "zoom_direction": "cinematic camera movement",
      "transition": "professional transition style",
      "subtitle_mode": true
    }}
  ]
}}

CRITICAL: Extract the specific story structure, characters, and visual progression from the brief. Make each segment serve the campaign's narrative arc and emotional journey. This should feel like a professional commercial, not a generic story."""

def create_topic_focused_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds):
    """Create prompt for simple story topics"""
    audience_instructions = get_audience_specific_instructions(audience)
    topic_context = analyze_topic_and_create_context(story_topic, audience)
    
    return f"""Create a unique and engaging {duration_minutes}-minute narrative video script about "{story_topic}".

TOPIC ANALYSIS: {topic_context}

AUDIENCE: {audience} - {audience_instructions}

REQUIREMENTS:
- Create exactly {num_segments} distinct segments, each {int(segment_seconds)} seconds long
- Each segment must advance the story and be visually distinct
- Make the story specifically about "{story_topic}" - don't be generic
- Include specific details, settings, characters, and emotions related to this topic
- Create vivid, cinematic image descriptions that capture the essence of "{story_topic}"

STORY STRUCTURE:
Segment 1: Opening/Setup - Introduce the world of "{story_topic}"
Segment 2: Context/Background - Show what makes this "{story_topic}" story unique
Segment 3: Inciting Incident - What specific challenge/opportunity arises in "{story_topic}"?
Segment 4: Rising Action - How does the protagonist engage with "{story_topic}"?
Segment 5: Complications - What obstacles appear in this "{story_topic}" journey?
Segment 6: Climax/Turning Point - The crucial moment in the "{story_topic}" story
Segment 7: Resolution - How is the "{story_topic}" situation resolved?
Segment 8: Conclusion/Reflection - What was learned from this "{story_topic}" experience?

FORMAT: Respond with ONLY valid JSON:
{{
  "title": "Specific title about {story_topic}",
  "style": "{audience} narrative about {story_topic}",
  "aspect_ratio": "9:16",
  "segments": [
    {{
      "text": "Engaging caption text (15-25 words) that specifically relates to {story_topic}",
      "text_overlay": true,
      "text_style": "modern",
      "duration_seconds": {int(segment_seconds)},
      "image_prompt": "Detailed, specific image description for {story_topic} scene, realistic photography style, vertical 9:16 format",
      "zoom_direction": "camera movement",
      "transition": "transition style",
      "subtitle_mode": true
    }}
  ]
}}

CRITICAL: Make this story uniquely about "{story_topic}". Include specific details, scenarios, and imagery that could ONLY apply to "{story_topic}", not generic storytelling."""

def create_system_message(story_topic, audience, is_complex_brief):
    """Create appropriate system message based on input type"""
    if is_complex_brief:
        return f"""You are an award-winning creative director and screenwriter specializing in commercial storytelling. You create compelling narrative campaigns that serve brand objectives while telling engaging human stories. 

You excel at:
- Transforming creative briefs into cinematic narratives
- Building emotional arcs that serve commercial goals
- Creating visually stunning scene descriptions
- Balancing brand messaging with authentic storytelling
- Designing campaigns for {audience} audiences

Always respond with perfectly formatted JSON. Be specific, cinematic, and commercially effective."""
    else:
        return f"""You are an expert storyteller specializing in {audience} content about {story_topic}. You create highly specific, detailed narratives that are unique to the given topic. 

You excel at:
- Creating topic-specific stories that feel authentic and personal
- Avoiding generic narrative tropes
- Building emotional connections through specific details
- Designing visually compelling scenes
- Crafting stories perfect for {audience} audiences

Always respond with valid JSON only. Be creative, specific, and emotionally engaging."""

def get_audience_specific_instructions(audience):
    """Get detailed instructions for different audiences"""
    instructions = {
        "children": "Use simple, positive language. Include wonder, discovery, friendship, and gentle lessons. Avoid scary or complex themes. Focus on colorful, magical imagery and clear moral lessons.",
        
        "adult": "Use sophisticated language and complex themes. Include psychological depth, realistic challenges, moral ambiguity, and mature emotional content. Focus on authentic human experiences and meaningful conflicts.",
        
        "general": "Use accessible language that works for all ages. Include universal themes of growth, challenge, and discovery. Balance simplicity with depth. Focus on relatable experiences and positive messages."
    }
    return instructions.get(audience, instructions["general"])

def analyze_topic_and_create_context(story_topic, audience):
    """Analyze the topic and create specific context for the story"""
    topic_lower = story_topic.lower()
    
    # Topic-specific context mapping
    topic_contexts = {
        # Personal growth topics
        "hero's journey": "A transformative adventure where an ordinary person faces extraordinary challenges and emerges changed. Include specific trials, mentors, and moments of self-discovery.",
        
        "overcoming fear": "A deeply personal story about confronting specific fears and finding courage. Include the physical and emotional experience of fear, and the moment of breakthrough.",
        
        "friendship": "An authentic story about human connection, loyalty, and mutual support. Include specific moments of bonding, conflict resolution, and shared experiences.",
        
        "finding purpose": "A journey of self-discovery and meaning-making. Include moments of confusion, exploration, breakthrough insights, and purposeful action.",
        
        # Adventure topics  
        "travel adventure": "A specific journey to a real or imagined place with unique challenges and discoveries. Include cultural encounters, unexpected obstacles, and transformative experiences.",
        
        "survival story": "A gripping tale of overcoming extreme circumstances using wit, determination, and resourcefulness. Include specific survival challenges and problem-solving moments.",
        
        # Emotional topics
        "love story": "An authentic romance focusing on emotional connection, personal growth, and relationship challenges. Include specific moments of attraction, conflict, and resolution.",
        
        "family bonds": "A story exploring family relationships, traditions, conflicts, and unconditional love. Include specific family dynamics and generational perspectives.",
        
        # Creative topics
        "artistic journey": "A story about creative expression, artistic struggle, and breakthrough moments. Include specific artistic challenges, inspiration, and the creative process.",
        
        "innovation": "A story about problem-solving, invention, and bringing new ideas to life. Include specific technical challenges, creative solutions, and implementation."
    }
    
    # Look for exact matches first
    for key, context in topic_contexts.items():
        if key in topic_lower:
            return context
    
    # Look for partial matches
    for key, context in topic_contexts.items():
        if any(word in topic_lower for word in key.split()):
            return context
    
    # Generic context based on common themes
    if any(word in topic_lower for word in ['journey', 'adventure', 'travel', 'exploration']):
        return f"An adventure story specifically about {story_topic}. Include unique challenges, discoveries, and transformative experiences that are specific to this particular journey."
    
    elif any(word in topic_lower for word in ['love', 'relationship', 'romance', 'connection']):
        return f"A relationship story specifically about {story_topic}. Include authentic emotional moments, personal growth, and the unique aspects of this particular relationship dynamic."
    
    elif any(word in topic_lower for word in ['fear', 'courage', 'overcome', 'challenge']):
        return f"A story of personal growth specifically about {story_topic}. Include the emotional journey, specific obstacles, and moments of breakthrough and transformation."
    
    else:
        return f"A unique story specifically about {story_topic}. Include distinctive elements, specific scenarios, and detailed imagery that could only apply to {story_topic}. Make every aspect of the story directly relevant to this particular topic."

def extract_json_from_text(text):
    """Extract JSON object from text that might contain markdown and other content"""
    try:
        # First try to find JSON wrapped in code blocks
        import re
        
        # Look for JSON wrapped in ```json...``` or ```...```
        code_block_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        # Try to find content between curly braces
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx:end_idx+1]
            try:
                script_data = json.loads(json_str)
                return script_data
            except json.JSONDecodeError:
                pass
        
        # If that fails, try to extract just the segments array
        segments_match = re.search(r'"segments":\s*\[(.*?)\]', text, re.DOTALL)
        if segments_match:
            # Try to reconstruct the JSON
            segments_text = segments_match.group(1)
            reconstructed_json = f'{{"title": "Generated Story", "style": "narrative", "aspect_ratio": "9:16", "segments": [{segments_text}]}}'
            try:
                return json.loads(reconstructed_json)
            except json.JSONDecodeError:
                pass
                
        return None
        
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return None

def validate_and_enhance_script(script_json, story_topic, audience):
    """Validate and enhance the generated script to ensure quality and topic relevance"""
    
    # Ensure required fields exist
    if "title" not in script_json:
        script_json["title"] = f"The Story of {story_topic[:30]}..."
    
    if "style" not in script_json:
        script_json["style"] = f"{audience} narrative about {story_topic[:50]}..."
    
    if "aspect_ratio" not in script_json:
        script_json["aspect_ratio"] = "9:16"
    
    # Validate and enhance segments
    segments = script_json.get("segments", [])
    
    # Ensure we have the right number of segments
    while len(segments) < 8:
        # Add generic segments if needed
        segments.append({
            "text": f"The journey of {story_topic} continues with new discoveries",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": 7.5,
            "image_prompt": f"Scene continuing the {story_topic} narrative, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "smooth_fade",
            "subtitle_mode": True
        })
    
    # Limit to 8 segments
    segments = segments[:8]
    
    for i, segment in enumerate(segments):
        # Ensure all required fields
        segment.setdefault("text_overlay", True)
        segment.setdefault("text_style", "modern")
        segment.setdefault("subtitle_mode", True)
        segment.setdefault("duration_seconds", 7.5)
        
        # Enhance image prompts to be more specific
        if "image_prompt" in segment:
            original_prompt = segment["image_prompt"]
            # Add topic-specific details if missing
            if len(story_topic) < 100 and story_topic.lower() not in original_prompt.lower():
                segment["image_prompt"] = f"{original_prompt}, specifically related to {story_topic}, professional photography, vertical 9:16 format"
        else:
            segment["image_prompt"] = f"Scene from {story_topic} story, professional photography, vertical 9:16 format"
        
        # Ensure variety in camera movements
        camera_movements = ["in", "forward_push", "slow_pan", "gentle_zoom_out", "drift", "gentle_pulse", "looking_up", "focus_in"]
        if "zoom_direction" not in segment:
            segment["zoom_direction"] = camera_movements[i % len(camera_movements)]
        
        # Ensure variety in transitions
        transitions = ["smooth_fade", "slide_up", "color_pulse", "slide_left", "whip_pan", "gradient_wipe"]
        if "transition" not in segment:
            segment["transition"] = transitions[i % len(transitions)]
    
    script_json["segments"] = segments
    return script_json

def fallback_script(story_topic, audience="general", duration_minutes=1, num_segments=8):
    """Generate a topic-specific fallback script if the API call fails"""
    print(f"Using enhanced fallback script generator for '{story_topic[:50]}...'")
    
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Create a title based on story topic
    if len(story_topic) > 100:  # Complex brief
        title = "Brand Campaign Story"
    else:
        title = f"The Journey of {story_topic}"
    
    # Create topic-specific segments
    segments = create_topic_specific_segments(story_topic, audience, segment_seconds, num_segments)
    
    # Assemble the script
    story_script = {
        "title": title,
        "style": f"narrative about {story_topic[:50]}{'...' if len(story_topic) > 50 else ''}, {audience}-friendly",
        "aspect_ratio": "9:16",
        "segments": segments
    }
    
    return story_script

def create_topic_specific_segments(story_topic, audience, segment_seconds, num_segments):
    """Create segments that are specifically tailored to the given topic"""
    
    topic_lower = story_topic.lower()
    
    # Check if it's a complex brief
    if detect_complex_brief(story_topic):
        return create_complex_brief_segments(story_topic, audience, segment_seconds, num_segments)
    
    # For simple topics, use topic-based templates
    if "travel" in topic_lower or "journey" in topic_lower:
        return create_travel_segments(story_topic, audience, segment_seconds, num_segments)
    elif "love" in topic_lower or "romance" in topic_lower:
        return create_love_segments(story_topic, audience, segment_seconds, num_segments)
    elif "friendship" in topic_lower:
        return create_friendship_segments(story_topic, audience, segment_seconds, num_segments)
    elif "fear" in topic_lower or "courage" in topic_lower or "overcome" in topic_lower:
        return create_courage_segments(story_topic, audience, segment_seconds, num_segments)
    elif "family" in topic_lower:
        return create_family_segments(story_topic, audience, segment_seconds, num_segments)
    elif "hero" in topic_lower:
        return create_hero_segments(story_topic, audience, segment_seconds, num_segments)
    else:
        # Generic but topic-focused segments
        return create_generic_topic_segments(story_topic, audience, segment_seconds, num_segments)

def create_complex_brief_segments(story_topic, audience, segment_seconds, num_segments):
    """Create segments for complex creative briefs"""
    # Extract key elements from the brief
    topic_lower = story_topic.lower()
    
    # Try to identify the brand/product
    brand = "the brand"
    if "uber" in topic_lower:
        brand = "Uber"
    elif "nike" in topic_lower:
        brand = "Nike"
    elif "apple" in topic_lower:
        brand = "Apple"
    
    return [
        {
            "text": f"In a world where everyday challenges test our limits",
            "image_prompt": f"Establishing shot showing common problems mentioned in brief, everyday struggle, relatable situation, cinematic lighting, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Multiple people face the same frustrating obstacles",
            "image_prompt": f"Different characters experiencing the challenges described in brief, parallel struggles, emotional frustration, dramatic lighting, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Each searches for a solution to their unique crisis",
            "image_prompt": f"Characters actively seeking solutions, determination visible, problem-solving in action, hopeful lighting beginning, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"A breakthrough moment changes everything for everyone",
            "image_prompt": f"Characters discovering the solution offered by {brand}, moment of realization, phones or devices in use, relief beginning, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Lives transform as the solution proves its worth",
            "image_prompt": f"Characters successfully using {brand} solution, problems being solved, satisfaction and relief, positive transformation, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Success stories multiply across different scenarios",
            "image_prompt": f"Multiple success stories happening simultaneously, {brand} solution working in various contexts, community of satisfied users, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"But {brand} has even bigger aspirations",
            "image_prompt": f"Hint at something bigger, mysterious setup, character looking expectant, anticipation building, {brand} branding subtle, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Introducing the next level of innovation",
            "image_prompt": f"Big reveal of new product/service from brief, aspirational moment, premium quality, breakthrough innovation, cinematic brand showcase, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_travel_segments(story_topic, audience, segment_seconds, num_segments):
    """Create travel-specific segments"""
    return [
        {
            "text": f"The journey of {story_topic} begins with a single step into the unknown",
            "image_prompt": f"Person standing at departure gate or train platform, holding travel documents, excited expression, {story_topic} destination signs visible, golden hour lighting, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"New landscapes unfold, each mile bringing fresh discoveries about {story_topic}",
            "image_prompt": f"Scenic view from train or plane window showing destination landscape related to {story_topic}, traveler's reflection in glass, changing scenery, natural lighting, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"First encounters with local culture reveal the true essence of {story_topic}",
            "image_prompt": f"Cultural interaction scene related to {story_topic}, local people sharing traditions, authentic cultural setting, warm natural lighting, candid moment, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Challenges arise that test resolve and deepen understanding of {story_topic}",
            "image_prompt": f"Traveler facing unexpected challenge related to {story_topic}, problem-solving moment, determination visible in expression, dramatic lighting, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Hidden gems are discovered, revealing the secret beauty of {story_topic}",
            "image_prompt": f"Discovery of hidden location or experience related to {story_topic}, sense of wonder and amazement, unique perspective, magical lighting, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Connections form with fellow travelers who share the passion for {story_topic}",
            "image_prompt": f"Group of diverse travelers bonding over shared experience of {story_topic}, laughter and conversation, authentic social moment, warm lighting, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The climax of the journey brings profound insights about {story_topic}",
            "image_prompt": f"Peak moment of travel experience related to {story_topic}, emotional breakthrough, spectacular setting, dramatic golden hour lighting, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Returning home forever changed by the transformative power of {story_topic}",
            "image_prompt": f"Traveler at home reflecting on journey, photo memories of {story_topic} visible, peaceful expression, soft natural lighting, sense of completion, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_courage_segments(story_topic, audience, segment_seconds, num_segments):
    """Create courage/overcoming fear specific segments"""
    return [
        {
            "text": f"The shadow of fear looms large, making {story_topic} seem impossible",
            "image_prompt": f"Person standing before intimidating challenge related to {story_topic}, visible anxiety, daunting obstacle ahead, dramatic shadows, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Past experiences whisper doubts about conquering {story_topic}",
            "image_prompt": f"Flashback-style image showing previous failures or fears related to {story_topic}, person in contemplative pose, muted colors, melancholic lighting, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"A moment of clarity reveals that {story_topic} is worth fighting for",
            "image_prompt": f"Person having realization moment about {story_topic}, eyes showing determination, symbolic light breaking through darkness, hopeful expression, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The first small step toward {story_topic} breaks the paralysis of fear",
            "image_prompt": f"Person taking literal or metaphorical first step toward {story_topic}, foot stepping forward, breaking through barrier, courage building, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Support appears from unexpected places, strengthening resolve for {story_topic}",
            "image_prompt": f"Supportive figures appearing to help with {story_topic} challenge, encouraging gestures, community support, warm encouraging lighting, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The greatest obstacle in {story_topic} becomes the defining moment of growth",
            "image_prompt": f"Person facing the biggest challenge related to {story_topic}, intense focus, muscles tensed, moment of greatest difficulty, dramatic lighting, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Breakthrough! The barriers around {story_topic} crumble before newfound courage",
            "image_prompt": f"Moment of triumph over {story_topic} challenge, person celebrating breakthrough, obstacles literally or metaphorically breaking, victorious pose, bright lighting, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Forever changed, ready to inspire others to embrace their own {story_topic}",
            "image_prompt": f"Transformed person now helping others with {story_topic}, mentoring role, confidence radiating, inspiring others, hopeful future vision, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_friendship_segments(story_topic, audience, segment_seconds, num_segments):
    """Create friendship-specific segments"""
    return [
        {
            "text": f"Two strangers cross paths, unaware that {story_topic} will bind them forever",
            "image_prompt": f"Two people meeting for first time in context of {story_topic}, casual encounter, neither realizing significance, natural everyday lighting, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Shared experiences around {story_topic} create the first bonds of trust",
            "image_prompt": f"Friends beginning to bond over shared interest in {story_topic}, laughing together, finding common ground, warm friendly lighting, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Their different perspectives on {story_topic} lead to heated disagreement",
            "image_prompt": f"Friends arguing about different approaches to {story_topic}, tension visible, conflicting viewpoints, dramatic lighting showing division, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Crisis strikes, and only by combining their views of {story_topic} can they survive",
            "image_prompt": f"Friends facing emergency related to {story_topic}, forced to work together, putting aside differences, urgent cooperation, intense lighting, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Working together, they discover that {story_topic} is stronger when shared",
            "image_prompt": f"Friends successfully collaborating on {story_topic} challenge, complementing each other's strengths, teamwork in action, harmonious lighting, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Sacrifice tests the limits of their dedication to both {story_topic} and each other",
            "image_prompt": f"One friend sacrificing for the other in context of {story_topic}, ultimate test of loyalty, emotional moment, dramatic sacrificial lighting, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Through {story_topic}, they learn that true friendship conquers all obstacles",
            "image_prompt": f"Friends triumphant together, having overcome challenges through {story_topic}, celebrating their bond, victory pose, bright celebratory lighting, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Years later, their friendship around {story_topic} continues to inspire others",
            "image_prompt": f"Friends years later, still connected by {story_topic}, now mentoring others, wisdom gained, peaceful mature lighting, legacy continuing, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_love_segments(story_topic, audience, segment_seconds, num_segments):
    """Create love story specific segments"""
    return [
        {
            "text": f"In the midst of {story_topic}, two hearts find an unexpected connection",
            "image_prompt": f"Two people meeting in setting related to {story_topic}, instant chemistry, eye contact, romantic tension, soft romantic lighting, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Their shared passion for {story_topic} becomes the foundation of romance",
            "image_prompt": f"Couple bonding over {story_topic}, sharing intimate moments, discovering compatibility, growing closer, warm intimate lighting, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Misunderstandings about {story_topic} threaten to tear them apart",
            "image_prompt": f"Couple in conflict over {story_topic}, emotional distance, hurt expressions, miscommunication visible, cold separated lighting, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Distance tests whether their love can survive without {story_topic} to unite them",
            "image_prompt": f"Couple separated by circumstances related to {story_topic}, longing expressions, physical distance, missing each other, melancholic lighting, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"A grand gesture involving {story_topic} proves the depth of true love",
            "image_prompt": f"Romantic gesture or surprise related to {story_topic}, one partner going to great lengths, preparation for reunion, anticipatory lighting, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Reconciliation shows how {story_topic} brought them together for a reason",
            "image_prompt": f"Couple reuniting, emotional reconciliation in setting of {story_topic}, tears of joy, embrace, understanding reached, golden reunion lighting, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Their wedding celebrates not just love, but their journey through {story_topic}",
            "image_prompt": f"Wedding ceremony incorporating elements of {story_topic}, celebration of love and shared passion, joyful faces, community celebration, radiant lighting, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Together they build a future where {story_topic} and love intertwine forever",
            "image_prompt": f"Couple in their future life, {story_topic} integrated into their daily happiness, family moments, legacy of love, peaceful future lighting, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_family_segments(story_topic, audience, segment_seconds, num_segments):
    """Create family-specific segments"""
    return [
        {
            "text": f"Three generations gather, each with different views on {story_topic}",
            "image_prompt": f"Multi-generational family meeting, different ages showing varied perspectives on {story_topic}, family dinner or gathering, warm family lighting, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Old traditions around {story_topic} clash with modern approaches",
            "image_prompt": f"Generational conflict over {story_topic}, older family member representing tradition, younger challenging conventions, tension at family table, contrasting lighting, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"A family crisis forces everyone to reconsider what {story_topic} really means",
            "image_prompt": f"Family emergency or crisis related to {story_topic}, bringing family together in concern, putting differences aside, urgent family lighting, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Working together, each generation contributes unique wisdom about {story_topic}",
            "image_prompt": f"Family collaborating on {story_topic} solution, each generation sharing their expertise, teamwork across ages, collaborative lighting, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The youngest family member surprises everyone with fresh insights on {story_topic}",
            "image_prompt": f"Child or young person offering unexpected wisdom about {story_topic}, family listening with surprise and respect, learning from youth, enlightened lighting, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Through {story_topic}, they discover that love transcends all differences",
            "image_prompt": f"Family moment of understanding about {story_topic}, embracing despite differences, unity in diversity, emotional family bond, loving lighting, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"A new family tradition is born, blending old and new approaches to {story_topic}",
            "image_prompt": f"Family creating new tradition around {story_topic}, combining generational wisdom, celebration of unity, establishing new legacy, ceremonial lighting, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The family legacy of {story_topic} continues to the next generation",
            "image_prompt": f"Family passing down knowledge of {story_topic} to newest generation, cycle continuing, wisdom preserved and evolved, timeless family lighting, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_hero_segments(story_topic, audience, segment_seconds, num_segments):
    """Create hero's journey specific segments"""
    return [
        {
            "text": f"An ordinary person receives a call to embrace their destiny with {story_topic}",
            "image_prompt": f"Ordinary person in mundane setting suddenly encountering call to adventure related to {story_topic}, moment of revelation, destiny calling, transformative lighting, vertical 9:16 format",
            "zoom_direction": "in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Refusing the call, they try to ignore the growing importance of {story_topic}",
            "image_prompt": f"Character turning away from {story_topic} opportunity, denial, fear visible, trying to return to normal life, shadows of doubt, vertical 9:16 format",
            "zoom_direction": "slow_pan",
            "transition": "slide_up",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"A wise mentor appears, revealing the true significance of {story_topic}",
            "image_prompt": f"Wise mentor figure explaining importance of {story_topic} to reluctant hero, sharing wisdom, guidance being offered, enlightening conversation, wise lighting, vertical 9:16 format",
            "zoom_direction": "forward_push",
            "transition": "color_pulse",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Crossing the threshold, they enter the challenging world of {story_topic}",
            "image_prompt": f"Hero stepping into new world related to {story_topic}, crossing literal or metaphorical threshold, leaving comfort zone, dramatic transition lighting, vertical 9:16 format",
            "zoom_direction": "gentle_zoom_out",
            "transition": "slide_left",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Tests and trials push the hero to master the mysteries of {story_topic}",
            "image_prompt": f"Hero facing multiple challenges related to {story_topic}, training montage, growing stronger, overcoming obstacles, progressive improvement lighting, vertical 9:16 format",
            "zoom_direction": "looking_up",
            "transition": "whip_pan",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The final battle tests everything learned about {story_topic} and themselves",
            "image_prompt": f"Climactic confrontation where hero must use all knowledge of {story_topic}, ultimate test, highest stakes, everything on the line, epic lighting, vertical 9:16 format",
            "zoom_direction": "gentle_pulse",
            "transition": "gradient_wipe",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Victory achieved, the hero masters {story_topic} and gains the ultimate reward",
            "image_prompt": f"Hero triumphant, having mastered {story_topic}, receiving reward or recognition, transformation complete, achievement realized, victorious lighting, vertical 9:16 format",
            "zoom_direction": "focus_in",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Returning home, they share the wisdom of {story_topic} with their community",
            "image_prompt": f"Hero back home as changed person, teaching others about {story_topic}, sharing wisdom gained, inspiring community, legacy lighting, vertical 9:16 format",
            "zoom_direction": "drift",
            "transition": "smooth_fade",
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ][:num_segments]

def create_generic_topic_segments(story_topic, audience, segment_seconds, num_segments):
    """Create generic but topic-focused segments for any topic"""
    # Use different transition types
    transitions = ["smooth_fade", "slide_up", "color_pulse", "slide_left", "whip_pan", "gradient_wipe"]
    motions = ["in", "forward_push", "slow_pan", "gentle_zoom_out", "drift", "gentle_pulse", "looking_up", "focus_in"]
    
    generic_segments = [
        {
            "text": f"In a world where {story_topic} shapes everything, our story begins",
            "image_prompt": f"Establishing shot of world where {story_topic} is central theme, setting the stage, atmospheric lighting, introducing the environment of {story_topic}, vertical 9:16 format",
            "zoom_direction": motions[0],
            "transition": transitions[0],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The protagonist encounters {story_topic} for the first time, everything changes",
            "image_prompt": f"Character first meeting or discovering {story_topic}, moment of recognition, life-changing encounter, emotional reaction, significant lighting change, vertical 9:16 format",
            "zoom_direction": motions[1],
            "transition": transitions[1],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Understanding {story_topic} requires sacrifice and dedication beyond imagination",
            "image_prompt": f"Character struggling to comprehend or master {story_topic}, intense study or practice, dedication visible, challenging learning process, focused lighting, vertical 9:16 format",
            "zoom_direction": motions[2],
            "transition": transitions[2],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Obstacles emerge that threaten to destroy everything related to {story_topic}",
            "image_prompt": f"Major conflict threatening {story_topic}, antagonistic forces, character facing seemingly impossible odds, dramatic tension, storm-like lighting, vertical 9:16 format",
            "zoom_direction": motions[3],
            "transition": transitions[3],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Hidden allies reveal themselves, united by their connection to {story_topic}",
            "image_prompt": f"Unexpected helpers appearing to support {story_topic} cause, diverse group coming together, moment of unity, hopeful expressions, warm collaborative lighting, vertical 9:16 format",
            "zoom_direction": motions[4],
            "transition": transitions[4],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The true power of {story_topic} is revealed in the darkest hour",
            "image_prompt": f"Climactic revelation about {story_topic}, character discovering hidden truth or power, moment of enlightenment, transformation beginning, divine or magical lighting, vertical 9:16 format",
            "zoom_direction": motions[5],
            "transition": transitions[5],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"Victory over adversity proves that {story_topic} can change the world",
            "image_prompt": f"Triumphant resolution involving {story_topic}, character achieving goal, positive transformation complete, celebration of success, bright victorious lighting, vertical 9:16 format",
            "zoom_direction": motions[6],
            "transition": transitions[6],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        },
        {
            "text": f"The legacy of {story_topic} continues, inspiring future generations",
            "image_prompt": f"Long-term impact of {story_topic} story, character as mentor or inspiration, cycle continuing, wisdom passed on, timeless and hopeful lighting, vertical 9:16 format",
            "zoom_direction": motions[7],
            "transition": transitions[0],
            "text_overlay": True,
            "text_style": "modern",
            "duration_seconds": segment_seconds,
            "subtitle_mode": True
        }
    ]
    
    return generic_segments[:num_segments]

def get_user_story_prompt():
    """Get user input for narrative story topic and target audience"""
    print("\n===== Professional Narrative Video Generator =====")
    print("💡 You can input either:")
    print("   • Simple topics (e.g., 'overcoming fear of public speaking')")
    print("   • Complex creative briefs (like professional campaign descriptions)")
    print()
    
    story_topic = input("📝 Enter your story topic or creative brief: ")
    
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
    print("🧪 Testing Groq Script Generator...")
    
    # Test with simple topic
    print("\n1. Testing simple topic...")
    script1 = generate_story_script("learning to cook like my grandmother", "general", 1, 8)
    print(f"Generated: {script1['title']}")
    
    # Test with complex brief
    print("\n2. Testing complex creative brief...")
    uber_brief = "Uber is launching a helicopter ride service a premium, limited-access feature that extends its mission: 'Whatever the ride, Uber has you covered.' The promo should begin with relatable, everyday commuting chaos: traffic jams, rain-soaked roads, last-minute emergencies, missed autos, and frustrated people. We follow multiple characters, each facing a transport crisis – all finding a solution through Uber. The final scene should escalate the visual and emotional stakes by introducing something unexpected: a character booking and boarding an Uber Helicopter – seamlessly reinforcing that Uber isn't just for roads anymore."
    
    script2 = generate_story_script(uber_brief, "general", 1, 8)
    print(f"Generated: {script2['title']}")
    
    print("\n✅ Testing complete!")
