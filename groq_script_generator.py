'''
"""
Complete Groq API integration for generating custom narrative scripts with bilingual support.
Compatible version that works with existing groq_reel_generator.py
KEY FEATURE: Always generates image prompts in English, even when script text is in Hindi.
REMOVED: All narrative enhancements - uses original text only
"""

import requests
import json
import time
import random
import os
import datetime
from groq import Groq

# API Key for Groq API
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Initialize Groq client
GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)

def detect_language_preference(story_topic):
    """Detect if user wants Hindi or English script"""
    topic_lower = story_topic.lower()
    
    # Check for Hindi language indicators
    hindi_indicators = [
        'hindi', 'हिंदी', 'हिन्दी', 'in hindi', 'hindi me', 'hindi mein',
        'देवनागरी', 'भारतीय', 'indian language', 'hindi video', 'hindi script'
    ]
    
    # Check for Devanagari characters
    hindi_chars = set('अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहािीुूृॄेैोौंःँ़ऽ।॥०१२३४५६७८९')
    has_hindi_chars = any(char in hindi_chars for char in story_topic)
    
    # Check for explicit indicators
    has_hindi_indicators = any(indicator in topic_lower for indicator in hindi_indicators)
    
    if has_hindi_chars or has_hindi_indicators:
        return 'hindi'
    else:
        return 'english'

def write_output_to_file(content, label="output"):
    """Write content to a timestamped txt file in an outputs directory."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = "groq_outputs"
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{label}_{timestamp}.txt"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] {label} written to {filepath}")
        return filepath
    except Exception as e:
        print(f"[WARNING] Could not write output file: {e}")
        return None

def generate_brand_brief(product_name_or_complex_topic, duration_minutes, num_segments, segment_seconds, language='english'):
    """
    LLM1: Research Agent - Generates a simple brand brief without narrative enhancements.
    """
    
    if language == 'hindi':
        prompt = f"""'{product_name_or_complex_topic}' के लिए {duration_minutes*60}-सेकंड के वीडियो का विश्लेषण करें, जो {num_segments} खंडों में है, प्रत्येक लगभग {segment_seconds} सेकंड का।

    सरल आउटपुट आवश्यक:
    - शीर्षक: विषय के लिए एक संक्षिप्त शीर्षक।
    - शैली: सुझाई गई शैली।
    - मुख्य बिंदु: विषय के बारे में 3-5 मुख्य बिंदु।
    - लक्षित दर्शक: प्राथमिक दर्शकों का वर्णन।
    - विशेषताएं: विषय की 3 मुख्य विशेषताएं।
    - रंग: 5 HEX रंग कोड।
    - टोन: वांछित टोन (जैसे उत्साह: 0-10, विश्वास: 0-10)।
    - दृश्य: {num_segments} दृश्यों की सरल रूपरेखा।

    एक सरल विज्ञापन ब्रीफ के रूप में फॉर्मेट करें।"""
    
    else:  # English
        prompt = f"""Analyze '{product_name_or_complex_topic}' for a {duration_minutes*60}-second video creation, structured into {num_segments} segments of approximately {segment_seconds} seconds each.

    Simple Output Required:
    - Title: A concise title for the video.
    - Style: Suggested overall style.
    - Core Points: 3-5 main points about the topic.
    - Target Demographics: Describe the primary target audience.
    - Key Features: 3 unique aspects of the topic.
    - Visual Colors: Suggest 5 HEX color codes relevant to the topic.
    - Tone: Define the desired tone (e.g., excitement: 0-10, trust: 0-10).
    - Scene Outline: Simple outline of {num_segments} distinct scenes, each approximately {segment_seconds} seconds.

    Format as a simple brief without narrative enhancements."""

    print(f"LLM1 (Research Agent): Generating {language.upper()} simple brief for '{product_name_or_complex_topic}'...")
    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama3-70b-8192", # Research model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,        # Lower temperature for factual research
            max_tokens=2048
        )
        brief_content = response.choices[0].message.content
        # write_output_to_file(brief_content, label=f"llm1_simple_brief_{language}")
        print(f"LLM1 (Research Agent): {language.upper()} simple brief generated.")
        return brief_content
    except Exception as e:
        print(f"Error calling Groq API (LLM1 - Research Agent): {e}")
        return None

def create_script_treatment(brief, segment_seconds, num_segments, language='english'):
    """
    LLM2: Simple Script Generator - Transforms the brief into a direct script without enhancements.
    CRITICAL: Always generates image prompts in English, regardless of text language.
    """
    
    if language == 'hindi':
        creative_prompt = f"""इस ब्रीफ को एक सरल {int(segment_seconds * num_segments)}-सेकंड के वीडियो स्क्रिप्ट में बदलें जिसमें बिल्कुल {num_segments} खंड हों।

    विज्ञापन ब्रीफ:
    {brief}

    सरल आवश्यकताएं:
    - ब्रीफ के अनुसार {num_segments} दृश्यों में प्रति खंड {segment_seconds} सेकंड।
    - प्रत्येक दृश्य के लिए सरल विवरण प्रदान करें:
      * "text": खंड के लिए सरल हिंदी टेक्स्ट (10-20 शब्द)।
      * "image_prompt": अंग्रेजी में सरल दृश्य विवरण। वर्टिकल 9:16 फॉर्मेट निर्दिष्ट करें।
      * "zoom_direction": कैमरा मूवमेंट।
      * "transition": अगले दृश्य के लिए संक्रमण।

    आउटपुट प्रारूप:
    केवल एक वैध JSON ऑब्जेक्ट:
    {{
      "title": "सरल शीर्षक",
      "style": "सरल शैली",
      "aspect_ratio": "9:16",
      "segments": [
        {{
          "text": "सरल हिंदी टेक्स्ट (10-20 शब्द)",
          "text_overlay": true,
          "text_style": "modern",
          "duration_seconds": {segment_seconds},
          "image_prompt": "Simple scene description in English, vertical 9:16 format",
          "zoom_direction": "camera movement",
          "transition": "transition effect",
          "subtitle_mode": true
        }}
      ]
    }}
    महत्वपूर्ण: "text" हिंदी में हो लेकिन "image_prompt" अंग्रेजी में हो।"""
    
    else:  # English
        creative_prompt = f"""Transform this brief into a simple {int(segment_seconds * num_segments)}-second video script consisting of exactly {num_segments} segments.

    BRIEF:
    {brief}

    Simple Requirements:
    - Follow the brief for {num_segments} scenes with {segment_seconds} seconds per segment.
    - For each scene, provide simple details:
      * "text": Simple text for the segment (10-20 words).
      * "image_prompt": Simple visual descriptions in English. Specify vertical 9:16 format.
      * "zoom_direction": Camera movement.
      * "transition": Transition effect to next scene.

    Output Format:
    Respond with ONLY a valid JSON object:
    {{
      "title": "Simple title",
      "style": "Simple style",
      "aspect_ratio": "9:16",
      "segments": [
        {{
          "text": "Simple text for segment (10-20 words)",
          "text_overlay": true,
          "text_style": "modern",
          "duration_seconds": {segment_seconds},
          "image_prompt": "Simple scene description, vertical 9:16 format",
          "zoom_direction": "camera movement",
          "transition": "transition effect",
          "subtitle_mode": true
        }}
      ]
    }}
    CRITICAL: Keep "image_prompt" simple and always in English."""

    print(f"LLM2 (Creative Agent): Generating {language.upper()} simple script from brief...")
    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama3-8b-8192", # Creative model
            messages=[{"role": "user", "content": creative_prompt}],
            temperature=0.8,          # Higher temperature for creativity
            max_tokens=3500           # Increased to accommodate detailed JSON for 8 segments
        )
        script_content = response.choices[0].message.content
        # write_output_to_file(script_content, label=f"llm2_simple_script_{language}")
        print(f"LLM2 (Creative Agent): {language.upper()} simple script generated.")
        return script_content
    except Exception as e:
        print(f"Error calling Groq API (LLM2 - Creative Agent): {e}")
        return None

def generate_story_script(story_topic, audience="general", duration_minutes=1, num_segments=8, language=None):
    """
    Generate a simple script using Groq API with bilingual support - NO narrative enhancements
    
    Parameters:
    - story_topic: Story theme, topic, or complete creative brief from user input
    - audience: Target audience ("children", "adult", "general")
    - duration_minutes: Target duration in minutes
    - num_segments: Number of video segments to create (fixed at 8 for 1-minute videos)
    - language: Force specific language ('english' or 'hindi'), or None for auto-detection
    
    Returns:
    - Dictionary with script data structure
    """
    
    # Detect language preference
    if language is None:
        language = detect_language_preference(story_topic)
    
    print(f"🌍 Generating {language.upper()} simple script for '{story_topic[:50]}...'")
    print(f"📝 Text: {language.upper()}, Image Prompts: ENGLISH (always)")
    
    # Calculate segment duration based on total video length
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Determine if this is a simple topic or a complex creative brief (potential product/brand)
    is_complex_brief = detect_complex_brief(story_topic)
    
    try:
        script_text = None
        if is_complex_brief:
            # --- Two-Agent Pipeline for Complex Briefs/Products ---
            print("Using Simple Two-Agent Pipeline for script generation...")
            # Agent 1: Generate Simple Brief
            brand_brief = generate_brand_brief(story_topic, duration_minutes, num_segments, segment_seconds, language)
            if not brand_brief:
                print("Failed to generate brief from LLM1. Using fallback script.")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback

            # Agent 2: Create Simple Script from Brief
            script_text = create_script_treatment(brand_brief, segment_seconds, num_segments, language)
            if not script_text:
                print("Failed to generate script from LLM2. Using fallback script.")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback
        else:
            # --- Simple Single-Agent Pipeline for Simple Topics ---
            print("Using Simple Single-Agent Pipeline for topic script generation...")
            prompt = create_simple_topic_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds, language)
            system_message = create_simple_system_message(story_topic, audience, is_complex_brief=False, language=language)
            
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
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "temperature": 0.8,
                "max_tokens": 3000,
                "top_p": 0.9
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                print(f"Error calling Groq API (Single-Agent): {response.status_code}")
                print(f"Response: {response.text}")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback
            
            result = response.json()
            script_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            write_output_to_file(script_text, label=f"single_agent_simple_script_{language}")

        if not script_text:
            print("Empty response from Groq API.")
            fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
            write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
            return fallback

        # Extract JSON from the response text (common for both pipelines)
        script_json = extract_json_from_text(script_text)
        if not script_json:
            print("Could not extract valid JSON from Groq response.")
            print(f"Raw response preview: {script_text[:500]}...")
            fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
            write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
            return fallback
            
        # Simple validation without enhancements
        clean_script = simple_script_validation(script_json, story_topic, audience, language)
        write_output_to_file(json.dumps(clean_script, indent=2), label=f"final_simple_script_{language}")
        print(f"✅ Successfully generated {language.upper()} simple script!")
        return clean_script
        
    except requests.exceptions.RequestException as e:
        print(f"Network error generating script with Groq API: {e}")
        fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
        write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
        return fallback
    except Exception as e:
        print(f"Overall error in generate_story_script: {e}")
        fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
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
        'advertisement', 'showcase', 'demonstrate', 'highlight', 'promote',
        # Hindi indicators
        'अभियान', 'प्रचार', 'व्यावसायिक', 'ब्रांड', 'लॉन्च', 'उत्पाद',
        'शुरू होना चाहिए', 'समाप्त होना चाहिए', 'टैगलाइन', 'मिशन', 'संदेश'
    ]
    
    # Check length (complex briefs are usually longer)
    if len(story_topic) > 200:
        return True
    
    # Check for complex indicators
    return any(indicator in topic_lower for indicator in complex_indicators)

def create_simple_topic_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds, language):
    """Create simple prompt for story topics with language support - NO enhancements"""
    
    if language == 'hindi':
        return f""""{story_topic}" के बारे में एक सरल {duration_minutes}-मिनट की हिंदी वीडियो स्क्रिप्ट बनाएं।

REQUIREMENTS:
- टेक्स्ट हिंदी में उत्पन्न करें
- image_prompt केवल अंग्रेजी में उत्पन्न करें
- "{story_topic}" के बारे में सरल वीडियो बनाएं

REQUIREMENTS:
- बिल्कुल {num_segments} खंड बनाएं, प्रत्येक {int(segment_seconds)} सेकंड लंबा
- प्रत्येक खंड सरल और स्पष्ट होना चाहिए

FORMAT: केवल वैध JSON:
{{
  "title": "{story_topic} के बारे में सरल हिंदी शीर्षक",
  "style": "simple video about {story_topic}",
  "aspect_ratio": "9:16",
  "segments": [
    {{
      "text": "सरल हिंदी टेक्स्ट (10-20 शब्द) {story_topic} के बारे में",
      "text_overlay": true,
      "text_style": "modern",
      "duration_seconds": {int(segment_seconds)},
      "image_prompt": "Simple image description about {story_topic}, vertical 9:16 format",
      "zoom_direction": "camera movement",
      "transition": "transition style",
      "subtitle_mode": true
    }}
  ]
}}

महत्वपूर्ण: 
- सभी "text" फील्ड हिंदी में होने चाहिए
- सभी "image_prompt" फील्ड केवल अंग्रेजी में होने चाहिए"""

    else:  # English
        return f"""Create a simple {duration_minutes}-minute video script about "{story_topic}".

AUDIENCE: {audience}

REQUIREMENTS:
- Create exactly {num_segments} segments, each {int(segment_seconds)} seconds long
- Each segment must be simple and clear about "{story_topic}"
- Keep it direct and straightforward

FORMAT: Respond with ONLY valid JSON:
{{
  "title": "Simple title about {story_topic}",
  "style": "simple video about {story_topic}",
  "aspect_ratio": "9:16",
  "segments": [
    {{
      "text": "Simple text about {story_topic} (10-20 words)",
      "text_overlay": true,
      "text_style": "modern",
      "duration_seconds": {int(segment_seconds)},
      "image_prompt": "Simple image description about {story_topic}, vertical 9:16 format",
      "zoom_direction": "camera movement",
      "transition": "transition style",
      "subtitle_mode": true
    }}
  ]
}}

CRITICAL: Keep it simple and direct about "{story_topic}"."""

def create_simple_system_message(story_topic, audience, is_complex_brief, language):
    """Create simple system message - NO narrative enhancements"""
    
    if language == 'hindi':
        if is_complex_brief:
            return f"""आप एक सरल हिंदी वीडियो स्क्रिप्ट जेनरेटर हैं। आप सीधे और स्पष्ट वीडियो स्क्रिप्ट बनाते हैं।

CRITICAL: हमेशा हिंदी में टेक्स्ट और केवल अंग्रेजी में image_prompt उत्पन्न करें।
हमेशा पूर्ण रूप से स्वरूपित JSON के साथ जवाब दें।"""

        else:
            return f"""आप {audience} सामग्री के लिए एक सरल हिंदी स्क्रिप्ट जेनरेटर हैं जो {story_topic} के बारे में है। आप सरल, स्पष्ट हिंदी स्क्रिप्ट बनाते हैं।

CRITICAL: हमेशा हिंदी में टेक्स्ट और केवल अंग्रेजी में image_prompt उत्पन्न करें।
हमेशा केवल वैध JSON के साथ जवाब दें।"""

    else:  # English
        if is_complex_brief:
            return f"""You are a simple video script generator. You create direct and clear video scripts without enhancements.

Always respond with perfectly formatted JSON. Be simple, direct, and clear."""

        else:
            return f"""You are a simple script generator for {audience} content about {story_topic}. You create simple, clear scripts.

Always respond with valid JSON only. Be direct and straightforward."""

def extract_json_from_text(text):
    """Extract JSON object from text that might contain markdown and other content"""
    try:
        import re
        
        # Look for JSON wrapped in code blocks
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
        
        return None
        
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return None

def simple_script_validation(script_json, story_topic, audience, language):
    """Simple validation without enhancements"""
    
    # Ensure required fields exist
    if "title" not in script_json:
        if language == 'hindi':
            script_json["title"] = f"{story_topic[:30]}"
        else:
            script_json["title"] = f"{story_topic[:30]}"
    
    if "style" not in script_json:
        script_json["style"] = f"simple video about {story_topic[:50]}"
    
    if "aspect_ratio" not in script_json:
        script_json["aspect_ratio"] = "9:16"
    
    # Validate segments
    segments = script_json.get("segments", [])
    
    # Ensure we have the right number of segments
    while len(segments) < 8:
        if language == 'hindi':
            segments.append({
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern", 
                "duration_seconds": 7.5,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
                "zoom_direction": "gentle_pulse",
                "transition": "smooth_fade",
                "subtitle_mode": True
            })
        else:
            segments.append({
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern",
                "duration_seconds": 7.5,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
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
        
        # CRITICAL: Ensure image prompts are ALWAYS in English
        if "image_prompt" in segment:
            original_prompt = segment["image_prompt"]
            # Make sure it's in English and has proper format
            if "vertical 9:16 format" not in original_prompt:
                segment["image_prompt"] = f"{original_prompt}, vertical 9:16 format"
        else:
            segment["image_prompt"] = f"{story_topic}, vertical 9:16 format"
        
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

def fallback_script(story_topic, audience="general", duration_minutes=1, num_segments=8, language='english'):
    """Generate a simple fallback script without enhancements"""
    print(f"Using simple fallback script generator for '{story_topic[:50]}...' in {language.upper()}")
    
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Create a simple title based on story topic and language
    if language == 'hindi':
        title = f"{story_topic}"
    else:
        title = f"{story_topic}"
    
    # Create simple segments
    segments = create_simple_segments(story_topic, audience, segment_seconds, num_segments, language)
    
    # Assemble the script
    story_script = {
        "title": title,
        "style": f"simple video about {story_topic}",
        "aspect_ratio": "9:16",
        "segments": segments
    }
    
    return story_script

def create_simple_segments(story_topic, audience, segment_seconds, num_segments, language):
    """Create simple segments without narrative enhancements"""
    
    motions = ["in", "forward_push", "slow_pan", "gentle_zoom_out", "drift", "gentle_pulse", "looking_up", "focus_in"]
    transitions = ["smooth_fade", "slide_up", "color_pulse", "slide_left", "whip_pan", "gradient_wipe", "smooth_fade", "smooth_fade"]
    
    segments = []
    for i in range(min(num_segments, 8)):
        if language == 'hindi':
            segment = {
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern",
                "duration_seconds": segment_seconds,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
                "zoom_direction": motions[i % len(motions)],
                "transition": transitions[i % len(transitions)],
                "subtitle_mode": True
            }
        else:
            segment = {
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern", 
                "duration_seconds": segment_seconds,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
                "zoom_direction": motions[i % len(motions)],
                "transition": transitions[i % len(transitions)],
                "subtitle_mode": True
            }
        segments.append(segment)
    
    return segments

def get_user_story_prompt():
    """Get user input for narrative story topic and target audience - COMPATIBLE WITH EXISTING CODE"""
    print("\n===== Simple Bilingual Video Generator =====")
    print("🌍 Languages: English & Hindi (हिंदी)")
    print("🎯 Key Feature: Hindi text + English image prompts")
    print("💡 You can input:")
    print("   • Simple topics (e.g., 'overcoming fear')")
    print("   • Hindi topics (e.g., 'डर पर काबू पाना')")
    print("   • Direct descriptions without enhancements")
    print()
    
    story_topic = input("📝 Enter your simple topic: ")
    
    print("\nChoose a target audience:")
    print("1. Children (child-friendly)")
    print("2. Adults (mature)")
    print("3. General (all ages)")
    
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
    print("🧪 Testing Simple Groq Script Generator...")
    
    # Test with simple topic
    print("\n1. Testing simple English topic...")
    script1 = generate_story_script("visit new york skyline", "adult", 1, 8, "english")
    print(f"Generated: {script1['title']}")
    
    # Test with Hindi topic  
    print("\n2. Testing Hindi topic...")
    script2 = generate_story_script("दोस्ती", "general", 1, 8, "hindi")
    print(f"Generated: {script2['title']}")
    
    print("\n✅ Testing complete!")
'''
"""
Complete Groq API integration for generating custom narrative scripts with bilingual support.
Compatible version that works with existing groq_reel_generator.py
KEY FEATURE: Always generates image prompts in English, even when script text is in Hindi.
REMOVED: All narrative enhancements - uses original text only
"""

import requests
import json
import time
import random
import os
import datetime
from groq import Groq

# API Key for Groq API
GROQ_API_KEY = "add_key_ here"
# Initialize Groq client
GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)

def detect_language_preference(story_topic):
    """Detect if user wants Hindi or English script"""
    topic_lower = story_topic.lower()
    
    # Check for Hindi language indicators
    hindi_indicators = [
        'hindi', 'हिंदी', 'हिन्दी', 'in hindi', 'hindi me', 'hindi mein',
        'देवनागरी', 'भारतीय', 'indian language', 'hindi video', 'hindi script'
    ]
    
    # Check for Devanagari characters
    hindi_chars = set('अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहािीुूृॄेैोौंःँ़ऽ।॥०१२३४५६७८९')
    has_hindi_chars = any(char in hindi_chars for char in story_topic)
    
    # Check for explicit indicators
    has_hindi_indicators = any(indicator in topic_lower for indicator in hindi_indicators)
    
    if has_hindi_chars or has_hindi_indicators:
        return 'hindi'
    else:
        return 'english'

def write_output_to_file(content, label="output"):
    """Write content to a timestamped txt file in an outputs directory."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = "groq_outputs"
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{label}_{timestamp}.txt"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] {label} written to {filepath}")
        return filepath
    except Exception as e:
        print(f"[WARNING] Could not write output file: {e}")
        return None

def generate_brand_brief(product_name_or_complex_topic, duration_minutes, num_segments, segment_seconds, language='english'):
    """
    LLM1: Research Agent - Generates a simple brand brief without narrative enhancements.
    """
    
    if language == 'hindi':
        prompt = f"""'{product_name_or_complex_topic}' के लिए {duration_minutes*60}-सेकंड के वीडियो का विश्लेषण करें, जो {num_segments} खंडों में है, प्रत्येक लगभग {segment_seconds} सेकंड का।

    सरल आउटपुट आवश्यक:
    - शीर्षक: विषय के लिए एक संक्षिप्त शीर्षक।
    - शैली: सुझाई गई शैली।
    - मुख्य बिंदु: विषय के बारे में 3-5 मुख्य बिंदु।
    - लक्षित दर्शक: प्राथमिक दर्शकों का वर्णन।
    - विशेषताएं: विषय की 3 मुख्य विशेषताएं।
    - रंग: 5 HEX रंग कोड।
    - टोन: वांछित टोन (जैसे उत्साह: 0-10, विश्वास: 0-10)।
    - दृश्य: {num_segments} दृश्यों की सरल रूपरेखा।

    एक सरल विज्ञापन ब्रीफ के रूप में फॉर्मेट करें।"""
    
    else:  # English
        prompt = f"""Analyze '{product_name_or_complex_topic}' for a {duration_minutes*60}-second video creation, structured into {num_segments} segments of approximately {segment_seconds} seconds each.

    Simple Output Required:
    - Title: A concise title for the video.
    - Style: Suggested overall style.
    - Core Points: 3-5 main points about the topic.
    - Target Demographics: Describe the primary target audience.
    - Key Features: 3 unique aspects of the topic.
    - Visual Colors: Suggest 5 HEX color codes relevant to the topic.
    - Tone: Define the desired tone (e.g., excitement: 0-10, trust: 0-10).
    - Scene Outline: Simple outline of {num_segments} distinct scenes, each approximately {segment_seconds} seconds.

    Format as a simple brief without narrative enhancements."""

    print(f"LLM1 (Research Agent): Generating {language.upper()} simple brief for '{product_name_or_complex_topic}'...")
    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama3-70b-8192", # Research model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,        # Lower temperature for factual research
            max_tokens=2048
        )
        brief_content = response.choices[0].message.content
        write_output_to_file(brief_content, label=f"llm1_simple_brief_{language}")
        print(f"LLM1 (Research Agent): {language.upper()} simple brief generated.")
        return brief_content
    except Exception as e:
        print(f"Error calling Groq API (LLM1 - Research Agent): {e}")
        return None

def create_script_treatment(brief, segment_seconds, num_segments, language='english'):
    """
    LLM2: Simple Script Generator - Transforms the brief into a direct script without enhancements.
    CRITICAL: Always generates image prompts in English, regardless of text language.
    """
    
    if language == 'hindi':
        creative_prompt = f"""इस ब्रीफ को एक सरल {int(segment_seconds * num_segments)}-सेकंड के वीडियो स्क्रिप्ट में बदलें जिसमें बिल्कुल {num_segments} खंड हों।

    विज्ञापन ब्रीफ:
    {brief}

    सरल आवश्यकताएं:
    - ब्रीफ के अनुसार {num_segments} दृश्यों में प्रति खंड {segment_seconds} सेकंड।
    - प्रत्येक दृश्य के लिए सरल विवरण प्रदान करें:
      * "text": खंड के लिए सरल हिंदी टेक्स्ट (10-20 शब्द)।
      * "image_prompt": अंग्रेजी में सरल दृश्य विवरण। वर्टिकल 9:16 फॉर्मेट निर्दिष्ट करें।
      * "zoom_direction": कैमरा मूवमेंट।
      * "transition": अगले दृश्य के लिए संक्रमण।

    आउटपुट प्रारूप:
    केवल एक वैध JSON ऑब्जेक्ट:
    {{
      "title": "सरल शीर्षक",
      "style": "सरल शैली",
      "aspect_ratio": "9:16",
      "segments": [
        {{
          "text": "सरल हिंदी टेक्स्ट (10-20 शब्द)",
          "text_overlay": true,
          "text_style": "modern",
          "duration_seconds": {segment_seconds},
          "image_prompt": "Simple scene description in English, vertical 9:16 format",
          "zoom_direction": "camera movement",
          "transition": "transition effect",
          "subtitle_mode": true
        }}
      ]
    }}
    महत्वपूर्ण: "text" हिंदी में हो लेकिन "image_prompt" अंग्रेजी में हो।"""
    
    else:  # English
        creative_prompt = f"""Transform this brief into a simple {int(segment_seconds * num_segments)}-second video script consisting of exactly {num_segments} segments.

    BRIEF:
    {brief}

    Simple Requirements:
    - Follow the brief for {num_segments} scenes with {segment_seconds} seconds per segment.
    - For each scene, provide simple details:
      * "text": Simple text for the segment (10-20 words).
      * "image_prompt": Simple visual descriptions in English. Specify vertical 9:16 format.
      * "zoom_direction": Camera movement.
      * "transition": Transition effect to next scene.

    Output Format:
    Respond with ONLY a valid JSON object:
    {{
      "title": "Simple title",
      "style": "Simple style",
      "aspect_ratio": "9:16",
      "segments": [
        {{
          "text": "Simple text for segment (10-20 words)",
          "text_overlay": true,
          "text_style": "modern",
          "duration_seconds": {segment_seconds},
          "image_prompt": "Simple scene description, vertical 9:16 format",
          "zoom_direction": "camera movement",
          "transition": "transition effect",
          "subtitle_mode": true
        }}
      ]
    }}
    CRITICAL: Keep "image_prompt" simple and always in English."""

    print(f"LLM2 (Creative Agent): Generating {language.upper()} simple script from brief...")
    try:
        response = GROQ_CLIENT.chat.completions.create(
            model="llama3-8b-8192", # Creative model
            messages=[{"role": "user", "content": creative_prompt}],
            temperature=0.8,          # Higher temperature for creativity
            max_tokens=3500           # Increased to accommodate detailed JSON for 8 segments
        )
        script_content = response.choices[0].message.content
        write_output_to_file(script_content, label=f"llm2_simple_script_{language}")
        print(f"LLM2 (Creative Agent): {language.upper()} simple script generated.")
        return script_content
    except Exception as e:
        print(f"Error calling Groq API (LLM2 - Creative Agent): {e}")
        return None

def generate_story_script(story_topic, audience="general", duration_minutes=1, num_segments=8, language=None):
    """
    Generate a simple script using Groq API with bilingual support - NO narrative enhancements
    
    Parameters:
    - story_topic: Story theme, topic, or complete creative brief from user input
    - audience: Target audience ("children", "adult", "general")
    - duration_minutes: Target duration in minutes
    - num_segments: Number of video segments to create (fixed at 8 for 1-minute videos)
    - language: Force specific language ('english' or 'hindi'), or None for auto-detection
    
    Returns:
    - Dictionary with script data structure
    """
    
    # Detect language preference
    if language is None:
        language = detect_language_preference(story_topic)
    
    print(f"🌍 Generating {language.upper()} simple script for '{story_topic[:50]}...'")
    print(f"📝 Text: {language.upper()}, Image Prompts: ENGLISH (always)")
    
    # Calculate segment duration based on total video length
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Determine if this is a simple topic or complex creative brief
    is_complex_brief = detect_complex_brief(story_topic)
    
    try:
        script_text = None
        if is_complex_brief:
            # --- Two-Agent Pipeline for Complex Briefs/Products ---
            print("Using Simple Two-Agent Pipeline for script generation...")
            # Agent 1: Generate Simple Brief
            brand_brief = generate_brand_brief(story_topic, duration_minutes, num_segments, segment_seconds, language)
            if not brand_brief:
                print("Failed to generate brief from LLM1. Using fallback script.")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback

            # Agent 2: Create Simple Script from Brief
            script_text = create_script_treatment(brand_brief, segment_seconds, num_segments, language)
            if not script_text:
                print("Failed to generate script from LLM2. Using fallback script.")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback
        else:
            # --- Simple Single-Agent Pipeline for Simple Topics ---
            print("Using Simple Single-Agent Pipeline for topic script generation...")
            prompt = create_simple_topic_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds, language)
            system_message = create_simple_system_message(story_topic, audience, is_complex_brief=False, language=language)
            
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
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "temperature": 0.8,
                "max_tokens": 3000,
                "top_p": 0.9
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                print(f"Error calling Groq API (Single-Agent): {response.status_code}")
                print(f"Response: {response.text}")
                fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
                write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
                return fallback
            
            result = response.json()
            script_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            write_output_to_file(script_text, label=f"single_agent_simple_script_{language}")

        if not script_text:
            print("Empty response from Groq API.")
            fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
            write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
            return fallback

        # Extract JSON from the response text (common for both pipelines)
        script_json = extract_json_from_text(script_text)
        if not script_json:
            print("Could not extract valid JSON from Groq response.")
            print(f"Raw response preview: {script_text[:500]}...")
            fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
            write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
            return fallback
            
        # Simple validation without enhancements
        clean_script = simple_script_validation(script_json, story_topic, audience, language)
        write_output_to_file(json.dumps(clean_script, indent=2), label=f"final_simple_script_{language}")
        print(f"✅ Successfully generated {language.upper()} simple script!")
        return clean_script
        
    except requests.exceptions.RequestException as e:
        print(f"Network error generating script with Groq API: {e}")
        fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
        write_output_to_file(json.dumps(fallback, indent=2), label="fallback_script")
        return fallback
    except Exception as e:
        print(f"Overall error in generate_story_script: {e}")
        fallback = fallback_script(story_topic, audience, duration_minutes, num_segments, language)
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
        'advertisement', 'showcase', 'demonstrate', 'highlight', 'promote',
        # Hindi indicators
        'अभियान', 'प्रचार', 'व्यावसायिक', 'ब्रांड', 'लॉन्च', 'उत्पाद',
        'शुरू होना चाहिए', 'समाप्त होना चाहिए', 'टैगलाइन', 'मिशन', 'संदेश'
    ]
    
    # Check length (complex briefs are usually longer)
    if len(story_topic) > 200:
        return True
    
    # Check for complex indicators
    return any(indicator in topic_lower for indicator in complex_indicators)

def create_simple_topic_prompt(story_topic, audience, duration_minutes, num_segments, segment_seconds, language):
    """Create simple prompt for story topics with language support - NO enhancements"""
    
    if language == 'hindi':
        return f""""{story_topic}" के बारे में एक सरल {duration_minutes}-मिनट की हिंदी वीडियो स्क्रिप्ट बनाएं।

REQUIREMENTS:
- टेक्स्ट हिंदी में उत्पन्न करें
- image_prompt केवल अंग्रेजी में उत्पन्न करें
- "{story_topic}" के बारे में सरल वीडियो बनाएं

REQUIREMENTS:
- बिल्कुल {num_segments} खंड बनाएं, प्रत्येक {int(segment_seconds)} सेकंड लंबा
- प्रत्येक खंड सरल और स्पष्ट होना चाहिए

FORMAT: केवल वैध JSON:
{{
  "title": "{story_topic} के बारे में सरल हिंदी शीर्षक",
  "style": "simple video about {story_topic}",
  "aspect_ratio": "9:16",
  "segments": [
    {{
      "text": "सरल हिंदी टेक्स्ट (10-20 शब्द) {story_topic} के बारे में",
      "text_overlay": true,
      "text_style": "modern",
      "duration_seconds": {int(segment_seconds)},
      "image_prompt": "Simple image description about {story_topic}, vertical 9:16 format",
      "zoom_direction": "camera movement",
      "transition": "transition style",
      "subtitle_mode": true
    }}
  ]
}}

महत्वपूर्ण: 
- सभी "text" फील्ड हिंदी में होने चाहिए
- सभी "image_prompt" फील्ड केवल अंग्रेजी में होने चाहिए"""

    else:  # English
        return f"""Create a simple {duration_minutes}-minute video script about "{story_topic}".

AUDIENCE: {audience}

REQUIREMENTS:
- Create exactly {num_segments} segments, each {int(segment_seconds)} seconds long
- Each segment must be simple and clear about "{story_topic}"
- Keep it direct and straightforward

FORMAT: Respond with ONLY valid JSON:
{{
  "title": "Simple title about {story_topic}",
  "style": "simple video about {story_topic}",
  "aspect_ratio": "9:16",
  "segments": [
    {{
      "text": "Simple text about {story_topic} (10-20 words)",
      "text_overlay": true,
      "text_style": "modern",
      "duration_seconds": {int(segment_seconds)},
      "image_prompt": "Simple image description about {story_topic}, vertical 9:16 format",
      "zoom_direction": "camera movement",
      "transition": "transition style",
      "subtitle_mode": true
    }}
  ]
}}

CRITICAL: Keep it simple and direct about "{story_topic}"."""

def create_simple_system_message(story_topic, audience, is_complex_brief, language):
    """Create simple system message - NO narrative enhancements"""
    
    if language == 'hindi':
        if is_complex_brief:
            return f"""आप एक सरल हिंदी वीडियो स्क्रिप्ट जेनरेटर हैं। आप सीधे और स्पष्ट वीडियो स्क्रिप्ट बनाते हैं।

CRITICAL: हमेशा हिंदी में टेक्स्ट और केवल अंग्रेजी में image_prompt उत्पन्न करें।
हमेशा पूर्ण रूप से स्वरूपित JSON के साथ जवाब दें।"""

        else:
            return f"""आप {audience} सामग्री के लिए एक सरल हिंदी स्क्रिप्ट जेनरेटर हैं जो {story_topic} के बारे में है। आप सरल, स्पष्ट हिंदी स्क्रिप्ट बनाते हैं।

CRITICAL: हमेशा हिंदी में टेक्स्ट और केवल अंग्रेजी में image_prompt उत्पन्न करें।
हमेशा केवल वैध JSON के साथ जवाब दें।"""

    else:  # English
        if is_complex_brief:
            return f"""You are a simple video script generator. You create direct and clear video scripts without enhancements.

Always respond with perfectly formatted JSON. Be simple, direct, and clear."""

        else:
            return f"""You are a simple script generator for {audience} content about {story_topic}. You create simple, clear scripts.

Always respond with valid JSON only. Be direct and straightforward."""

def extract_json_from_text(text):
    """Extract JSON object from text that might contain markdown and other content"""
    try:
        import re
        
        # Look for JSON wrapped in code blocks
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
        
        return None
        
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return None

def simple_script_validation(script_json, story_topic, audience, language):
    """Simple validation without enhancements"""
    
    # Ensure required fields exist
    if "title" not in script_json:
        if language == 'hindi':
            script_json["title"] = f"{story_topic[:30]}"
        else:
            script_json["title"] = f"{story_topic[:30]}"
    
    if "style" not in script_json:
        script_json["style"] = f"simple video about {story_topic[:50]}"
    
    if "aspect_ratio" not in script_json:
        script_json["aspect_ratio"] = "9:16"
    
    # Validate segments
    segments = script_json.get("segments", [])
    
    # Ensure we have the right number of segments
    while len(segments) < 8:
        if language == 'hindi':
            segments.append({
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern", 
                "duration_seconds": 7.5,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
                "zoom_direction": "gentle_pulse",
                "transition": "smooth_fade",
                "subtitle_mode": True
            })
        else:
            segments.append({
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern",
                "duration_seconds": 7.5,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
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
        
        # CRITICAL: Ensure image prompts are ALWAYS in English
        if "image_prompt" in segment:
            original_prompt = segment["image_prompt"]
            # Make sure it's in English and has proper format
            if "vertical 9:16 format" not in original_prompt:
                segment["image_prompt"] = f"{original_prompt}, vertical 9:16 format"
        else:
            segment["image_prompt"] = f"{story_topic}, vertical 9:16 format"
        
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

def fallback_script(story_topic, audience="general", duration_minutes=1, num_segments=8, language='english'):
    """Generate a simple fallback script without enhancements"""
    print(f"Using simple fallback script generator for '{story_topic[:50]}...' in {language.upper()}")
    
    segment_seconds = (duration_minutes * 60) / num_segments
    
    # Create a simple title based on story topic and language
    if language == 'hindi':
        title = f"{story_topic}"
    else:
        title = f"{story_topic}"
    
    # Create simple segments
    segments = create_simple_segments(story_topic, audience, segment_seconds, num_segments, language)
    
    # Assemble the script
    story_script = {
        "title": title,
        "style": f"simple video about {story_topic}",
        "aspect_ratio": "9:16",
        "segments": segments
    }
    
    return story_script

def create_simple_segments(story_topic, audience, segment_seconds, num_segments, language):
    """Create simple segments without narrative enhancements"""
    
    motions = ["in", "forward_push", "slow_pan", "gentle_zoom_out", "drift", "gentle_pulse", "looking_up", "focus_in"]
    transitions = ["smooth_fade", "slide_up", "color_pulse", "slide_left", "whip_pan", "gradient_wipe", "smooth_fade", "smooth_fade"]
    
    segments = []
    for i in range(min(num_segments, 8)):
        if language == 'hindi':
            segment = {
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern",
                "duration_seconds": segment_seconds,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
                "zoom_direction": motions[i % len(motions)],
                "transition": transitions[i % len(transitions)],
                "subtitle_mode": True
            }
        else:
            segment = {
                "text": f"{story_topic}",
                "text_overlay": True,
                "text_style": "modern", 
                "duration_seconds": segment_seconds,
                "image_prompt": f"{story_topic}, vertical 9:16 format",
                "zoom_direction": motions[i % len(motions)],
                "transition": transitions[i % len(transitions)],
                "subtitle_mode": True
            }
        segments.append(segment)
    
    return segments

def get_user_story_prompt():
    """Get user input for narrative story topic and target audience - COMPATIBLE WITH EXISTING CODE"""
    print("\n===== Simple Bilingual Video Generator =====")
    print("🌍 Languages: English & Hindi (हिंदी)")
    print("🎯 Key Feature: Hindi text + English image prompts")
    print("💡 You can input:")
    print("   • Simple topics (e.g., 'overcoming fear')")
    print("   • Hindi topics (e.g., 'डर पर काबू पाना')")
    print("   • Direct descriptions without enhancements")
    print()
    
    story_topic = input("📝 Enter your simple topic: ")
    
    print("\nChoose a target audience:")
    print("1. Children (child-friendly)")
    print("2. Adults (mature)")
    print("3. General (all ages)")
    
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
    print("🧪 Testing Simple Groq Script Generator...")
    
    # Test with simple topic
    print("\n1. Testing simple English topic...")
    script1 = generate_story_script("visit new york skyline", "adult", 1, 8, "english")
    print(f"Generated: {script1['title']}")
    
    # Test with Hindi topic  
    print("\n2. Testing Hindi topic...")
    script2 = generate_story_script("दोस्ती", "general", 1, 8, "hindi")
    print(f"Generated: {script2['title']}")
    
    print("\n✅ Testing complete!")

