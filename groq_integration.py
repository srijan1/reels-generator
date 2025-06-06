"""
Functions for calling Groq API for text generation with enhanced narration variety.
This version eliminates repetitive phrases and creates unique narrations.
"""

import requests
import base64
import tempfile
import subprocess
import os
import json
import random
import hashlib
import time

# API Configuration
GROQ_API_KEY = "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"
SPEECHIFY_API_KEY = "aT35muhXVhtj6HwtuWmCygONdKFWMKoA-CR4hYvaPso="

# Voice IDs for Speechify - these are examples, actual voice IDs need to be fetched from their API
SPEECHIFY_VOICES = {
    "Stephanie": "female-en-US-martha-nervous",  # Example voice ID
    "Jennifer": "female-en-US-jenny-neutral",    # Example voice ID
    "Peter": "male-en-US-peter-neutral",         # Example voice ID
    "Alex": "male-en-US-alex-neutral",           # Example voice ID
    "Lily": "female-en-US-lily-excited"          # Example voice ID
}

# Track used phrases to avoid repetition
USED_PHRASES = set()
SESSION_COUNTER = 0

def generate_narration(image_prompt, original_text, desired_duration_seconds=7):
    """Generate unique narration content using Groq API, avoiding repetitive phrases"""
    global SESSION_COUNTER
    SESSION_COUNTER += 1
    
    try:
        # Create request for Groq API with enhanced prompt for variety
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Create a more specific prompt to avoid generic responses
        specific_prompt = f"""Create a unique, natural narration for this video segment:

Original caption: "{original_text}"
Visual context: "{image_prompt}"

Requirements:
- Write 25-35 words of natural, conversational narration
- Make it feel personal and authentic, like someone actually experiencing this moment
- Avoid cliché phrases like "left me speechless", "everything I hoped for", "memory will stay with me"
- Focus on specific details and emotions from the scene
- Write in first person as if the narrator is living this experience
- Make it unique and engaging, not generic travel commentary

Example style: Instead of "The atmosphere left me speechless" → "I couldn't believe how the morning light transformed everything around me into something magical"

Write ONLY the narration text, nothing else."""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a skilled travel narrator who creates unique, authentic narrations that avoid clichés and repetitive phrases. Each narration should feel fresh and specific to the moment being described."
                },
                {
                    "role": "user",
                    "content": specific_prompt
                }
            ],
            "max_tokens": 80,
            "temperature": 0.9,  # Higher temperature for more variety
            "top_p": 0.95  # More randomness to avoid repetition
        }
        
        # Make the API call
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            narration_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # Clean up the response (remove quotes, extra formatting)
            narration_text = narration_text.strip('"').strip("'").strip()
            
            if narration_text and is_unique_narration(narration_text):
                print(f"Generated unique narration via Groq API: {narration_text}")
                add_to_used_phrases(narration_text)
                return narration_text
            else:
                print("Groq response was generic or repetitive, using dynamic fallback")
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Groq API: {e}")
        except Exception as e:
            print(f"Error parsing Groq API response: {e}")
        
        # Enhanced fallback with dynamic variety
        return create_dynamic_fallback_narration(image_prompt, original_text, SESSION_COUNTER)
    
    except Exception as e:
        print(f"Error generating content with Groq: {e}")
        return create_dynamic_fallback_narration(image_prompt, original_text, SESSION_COUNTER)

def is_unique_narration(narration_text):
    """Check if the narration is unique and not using overused phrases"""
    
    # Convert to lowercase for checking
    text_lower = narration_text.lower()
    
    # Forbidden cliché phrases
    forbidden_phrases = [
        "left me speechless",
        "everything i hoped for", 
        "everything i'd hoped for",
        "memory will stay with me",
        "took my breath away",
        "beyond my wildest dreams",
        "words cannot describe",
        "indescribable feeling",
        "moment i'll never forget",
        "experience of a lifetime",
        "dreams come true",
        "picture perfect",
        "absolutely incredible",
        "simply amazing",
        "truly magical",
        "unbelievable experience"
    ]
    
    # Check for forbidden phrases
    for phrase in forbidden_phrases:
        if phrase in text_lower:
            print(f"Rejected narration containing cliché phrase: '{phrase}'")
            return False
    
    # Check if we've used this exact narration before
    text_hash = hashlib.md5(text_lower.encode()).hexdigest()
    if text_hash in USED_PHRASES:
        print("Rejected duplicate narration")
        return False
    
    # Check for minimum length and quality
    if len(narration_text.split()) < 15:
        print("Rejected narration: too short")
        return False
    
    return True

def add_to_used_phrases(narration_text):
    """Add narration to used phrases to prevent repetition"""
    text_hash = hashlib.md5(narration_text.lower().encode()).hexdigest()
    USED_PHRASES.add(text_hash)

def create_dynamic_fallback_narration(image_prompt, original_text, counter):
    """Create dynamic, non-repetitive fallback narrations"""
    
    # Extract key elements from the prompt and text
    prompt_lower = image_prompt.lower()
    text_lower = original_text.lower()
    
    # Dynamic narrative styles that rotate
    styles = [
        "observational",  # What I notice/see
        "emotional",      # How it feels
        "sensory",        # What I hear/smell/touch
        "comparative",    # Different from what I expected
        "discovery",      # What I'm learning/finding
        "anticipatory",   # What's about to happen
        "reflective",     # What this means
        "immersive"       # Being in the moment
    ]
    
    style = styles[counter % len(styles)]
    
    # Context-aware narration based on content
    if any(word in prompt_lower for word in ['travel', 'journey', 'trip', 'visit']):
        return create_travel_narration(image_prompt, original_text, style, counter)
    elif any(word in prompt_lower for word in ['food', 'cooking', 'restaurant', 'kitchen']):
        return create_food_narration(image_prompt, original_text, style, counter)
    elif any(word in prompt_lower for word in ['nature', 'mountain', 'forest', 'beach', 'ocean']):
        return create_nature_narration(image_prompt, original_text, style, counter)
    elif any(word in prompt_lower for word in ['city', 'urban', 'street', 'building']):
        return create_urban_narration(image_prompt, original_text, style, counter)
    elif any(word in prompt_lower for word in ['people', 'friend', 'family', 'together']):
        return create_social_narration(image_prompt, original_text, style, counter)
    else:
        return create_general_narration(image_prompt, original_text, style, counter)

def create_travel_narration(image_prompt, original_text, style, counter):
    """Create travel-specific narrations"""
    
    travel_templates = {
        "observational": [
            f"The details here are nothing like what I imagined when planning this trip",
            f"Every corner I turn reveals something completely unexpected about this place",
            f"I find myself stopping every few steps to take in another fascinating detail",
            f"The way people move through this space tells such an interesting story",
            f"There's so much happening around me that I almost don't know where to look first"
        ],
        "emotional": [
            f"Something about this moment makes me feel more connected to the world around me",
            f"I can feel my perspective shifting as I experience this place firsthand",
            f"There's a sense of wonder here that I haven't felt since I was a child",
            f"This experience is reminding me exactly why I love to explore new places",
            f"I'm getting that familiar rush of excitement that comes with discovering somewhere new"
        ],
        "sensory": [
            f"The sounds here are so different from what I'm used to back home",
            f"I can smell spices and cooking that's making my mouth water already",
            f"The temperature and humidity here feel like stepping into another climate entirely",
            f"Even the way the light hits everything here creates such a unique atmosphere",
            f"The textures and materials around me tell the story of this place's history"
        ],
        "comparative": [
            f"This is so much more vibrant and alive than any photo could have prepared me for",
            f"The scale of everything here is completely different from what I expected",
            f"Meeting people here is changing all my preconceptions about this culture",
            f"The reality of being here is far more nuanced than any guidebook described",
            f"I'm discovering that my assumptions about this place were completely off base"
        ],
        "discovery": [
            f"I'm learning that there's a whole layer of life here that tourists rarely see",
            f"Each conversation I have here teaches me something new about local perspectives",
            f"I'm starting to understand the rhythm and flow of daily life in this place",
            f"The more time I spend here, the more I realize how much I still have to learn",
            f"Every local person I meet shares a different piece of this place's story"
        ],
        "anticipatory": [
            f"I have a feeling this experience is going to change how I see things going forward",
            f"There's something special building here that I can sense but can't quite name yet",
            f"I know I'm going to want to come back here again someday to explore more",
            f"This feels like one of those moments that's going to stick with me for years",
            f"I can already tell this trip is going to be different from all my other travels"
        ],
        "reflective": [
            f"Being here is making me think about my own life and choices in new ways",
            f"This experience is showing me how much we all share despite our different backgrounds",
            f"I'm realizing how much my comfort zone was actually limiting my understanding",
            f"This journey is teaching me as much about myself as it is about this place",
            f"I'm starting to see connections between this culture and my own that I never noticed before"
        ],
        "immersive": [
            f"Right now I'm completely absorbed in the energy and movement of this place",
            f"I'm trying to slow down and really pay attention to everything happening around me",
            f"For the first time in a while, I feel completely present in this exact moment",
            f"I'm letting myself get completely caught up in the flow of life here",
            f"There's something about being here that makes me want to just observe and absorb everything"
        ]
    }
    
    templates = travel_templates.get(style, travel_templates["observational"])
    return templates[counter % len(templates)]

def create_food_narration(image_prompt, original_text, style, counter):
    """Create food-specific narrations"""
    
    food_templates = {
        "observational": [
            f"The way they prepare this dish is completely different from anything I've seen before",
            f"I'm watching techniques that have probably been passed down through generations",
            f"The precision and care that goes into each step of this process is remarkable",
            f"Every ingredient here seems to have its own specific purpose and timing",
            f"The colors and textures coming together are almost too beautiful to eat"
        ],
        "sensory": [
            f"The aroma filling the air is making my stomach rumble with anticipation",
            f"I can hear the sizzling and bubbling that promises incredible flavors ahead",
            f"The combination of spices and herbs creates a scent I've never experienced before",
            f"Just watching this being prepared is already making my mouth water",
            f"The steam rising up carries hints of what's going to be an amazing meal"
        ],
        "emotional": [
            f"There's something deeply satisfying about watching food being made with such passion",
            f"This moment is reminding me why I love discovering new cuisines and flavors",
            f"Sharing this experience with locals is creating connections that go beyond language",
            f"Food has this amazing way of bringing people together across cultural boundaries",
            f"I'm feeling grateful for the opportunity to experience authentic local cooking"
        ],
        "discovery": [
            f"I'm learning that each region has its own unique approach to these traditional dishes",
            f"The stories behind these recipes are just as interesting as the flavors themselves",
            f"I'm discovering ingredients I've never heard of that completely transform familiar dishes",
            f"Each bite is teaching me something new about the culture and history of this place",
            f"I'm realizing how much depth and complexity goes into what seems like simple food"
        ]
    }
    
    templates = food_templates.get(style, food_templates["sensory"])
    return templates[counter % len(templates)]

def create_nature_narration(image_prompt, original_text, style, counter):
    """Create nature-specific narrations"""
    
    nature_templates = {
        "observational": [
            f"The way the light filters through here creates patterns I could watch for hours",
            f"There's a complexity to this ecosystem that becomes more apparent the longer I observe",
            f"Every direction I look reveals another layer of life and activity in this environment",
            f"The subtle changes in terrain and vegetation tell the story of this landscape's history",
            f"I'm noticing details in the natural world that I usually walk right past"
        ],
        "sensory": [
            f"The sounds of this place create a natural symphony that's both calming and energizing",
            f"The fresh air here has a quality that immediately makes me want to breathe deeper",
            f"I can feel the temperature difference as I move between sunlight and shade",
            f"The textures of bark, leaves, and stone under my hands connect me to this environment",
            f"Even the way the wind moves through here creates its own unique rhythm and music"
        ],
        "reflective": [
            f"Being surrounded by this natural beauty puts my daily concerns into a different perspective",
            f"There's something humbling about experiencing the scale and age of this landscape",
            f"This environment reminds me of how interconnected everything in nature really is",
            f"Moments like this make me think about our relationship with the natural world",
            f"I'm struck by how much peace and clarity I find when I'm immersed in nature"
        ],
        "immersive": [
            f"Right now I'm completely focused on the sights, sounds, and feelings of this moment",
            f"I'm trying to absorb every detail of this environment while I have the chance",
            f"There's something meditative about just sitting quietly and observing the natural world",
            f"I'm letting myself get completely lost in the rhythm and flow of this place",
            f"For once, I'm not thinking about anything except what's happening right here, right now"
        ]
    }
    
    templates = nature_templates.get(style, nature_templates["sensory"])
    return templates[counter % len(templates)]

def create_urban_narration(image_prompt, original_text, style, counter):
    """Create urban/city-specific narrations"""
    
    urban_templates = {
        "observational": [
            f"The energy and pace of this city is unlike anywhere else I've experienced",
            f"Every building and street corner here seems to have its own story to tell",
            f"I'm fascinated by how different neighborhoods can feel like completely different worlds",
            f"The mix of old and new architecture creates such an interesting visual contrast",
            f"People watching here gives me insights into how diverse and dynamic this city really is"
        ],
        "discovery": [
            f"I'm finding hidden gems and local spots that aren't in any tourist guidebooks",
            f"Each district I explore reveals a different aspect of this city's character and culture",
            f"I'm learning about the history that shaped this urban landscape into what it is today",
            f"The local recommendations I'm getting are leading me to experiences I never would have found",
            f"Every conversation with residents teaches me something new about life in this city"
        ],
        "immersive": [
            f"I'm getting swept up in the rhythm and flow of urban life around me",
            f"There's something energizing about being part of the constant movement and activity here",
            f"I'm trying to move like a local and blend into the natural patterns of the city",
            f"The busy streets and bustling energy make me feel connected to something bigger",
            f"I'm learning to navigate this urban maze while staying open to unexpected discoveries"
        ]
    }
    
    templates = urban_templates.get(style, urban_templates["observational"])
    return templates[counter % len(templates)]

def create_social_narration(image_prompt, original_text, style, counter):
    """Create social/people-focused narrations"""
    
    social_templates = {
        "emotional": [
            f"There's something special about sharing this experience with people who matter to me",
            f"Moments like these remind me how much I value the relationships in my life",
            f"The laughter and conversation here create memories I know we'll all treasure",
            f"Being together in this setting brings out different sides of everyone's personality",
            f"These are the kinds of moments that strengthen bonds and create lasting connections"
        ],
        "observational": [
            f"I love watching how different people react to and experience the same moment",
            f"The dynamics between everyone here create their own interesting layer of entertainment",
            f"It's fascinating to see how this environment brings out different aspects of everyone's character",
            f"The way people interact with each other here shows the best of human connection",
            f"I'm enjoying how this shared experience is creating new inside jokes and stories"
        ],
        "reflective": [
            f"Experiences like this remind me why spending time with others is so important",
            f"I'm realizing how much these shared moments contribute to our relationships over time",
            f"Being here together is creating the kind of memories that will bring us closer",
            f"This is exactly the type of experience that makes all the planning and effort worthwhile",
            f"I'm grateful for friends and family who are willing to share adventures like this with me"
        ]
    }
    
    templates = social_templates.get(style, social_templates["emotional"])
    return templates[counter % len(templates)]

def create_general_narration(image_prompt, original_text, style, counter):
    """Create general narrations for any topic"""
    
    general_templates = {
        "observational": [
            f"The details I'm noticing here are completely different from what I expected",
            f"There are layers of complexity to this experience that become apparent over time",
            f"I'm discovering aspects of this that I never would have anticipated",
            f"The more attention I pay, the more interesting details I keep discovering",
            f"This situation is revealing itself to be much more nuanced than I first realized"
        ],
        "emotional": [
            f"There's something about this moment that feels both exciting and meaningful",
            f"I'm experiencing a sense of growth and discovery that's really energizing",
            f"This is giving me insights and perspectives I didn't have before",
            f"I can feel my understanding and appreciation deepening as this unfolds",
            f"This experience is connecting me to something larger than my everyday routine"
        ],
        "reflective": [
            f"This is making me think about familiar things in completely new ways",
            f"I'm gaining perspectives that I know will influence how I approach similar situations",
            f"This experience is teaching me as much about myself as it is about the subject",
            f"I'm starting to understand connections and relationships I hadn't seen before",
            f"This is one of those experiences that expands how I think about the world"
        ]
    }
    
    templates = general_templates.get(style, general_templates["observational"])
    return templates[counter % len(templates)]

def convert_text_to_speech(text, voice="Stephanie", output_path=None):
    """Convert text to speech using updated Speechify API and save to file"""
    
    # Create a temporary file if no output path provided
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        output_path = temp_file.name
        temp_file.close()
    
    try:
        # Use updated Speechify API endpoint based on documentation
        url = "https://api.sws.speechify.com/v1/audio/speech"
        
        # Get voice ID from our mapping, or use a default
        voice_id = SPEECHIFY_VOICES.get(voice, "female-en-US-martha-nervous")
        
        # Set up request headers
        headers = {
            "Authorization": f"Bearer {SPEECHIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Set up request payload according to the docs
        payload = {
            "input": text,
            "voice_id": voice_id,
            "audio_format": "mp3",
            "language": "en-US",
            "model": "simba-english"
        }
        
        # Make API request
        try:
            print(f"Calling Speechify API for: {text[:30]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()  # Check for HTTP errors
            
            # Extract audio data from response
            response_data = response.json()
            audio_data = response_data.get("audio_data")
            
            if not audio_data:
                raise ValueError("No audio data in response")
            
            # Decode base64 audio data and save to file
            audio_bytes = base64.b64decode(audio_data)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"Speechify API call successful! Audio saved to {output_path}")
            
            # If there's billable characters info, log it
            if "billable_characters_count" in response_data:
                print(f"Billable characters: {response_data['billable_characters_count']}")
                
            return output_path
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Speechify API: {e}")
            print("Falling back to mock audio generation...")
    except Exception as e:
        print(f"Error in Speechify API setup: {e}")
        print("Falling back to mock audio generation...")
    
    # Fallback: Create a silent audio file with duration based on text length
    try:
        # Approximately 2-3 words per second for natural speech
        word_count = len(text.split())
        duration = max(3, word_count / 2.5)  # Minimum 3 seconds
        
        # Use ffmpeg to create a silent audio file
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", 
            "-i", f"anullsrc=r=44100:cl=stereo", 
            "-t", str(duration),
            output_path
        ]
        
        # Run the command silently
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"Created mock speech audio at {output_path} (duration: {duration:.2f}s)")
        return output_path
    
    except Exception as e:
        print(f"Error creating mock speech: {e}")
        return None

def get_audio_duration(audio_file_path):
    """Get the duration of an audio file in seconds using ffmpeg"""
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {audio_file_path}")
            return None
            
        # Use ffprobe to get duration
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'json', 
            audio_file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting audio duration: {result.stderr}")
            return None
            
        # Parse the JSON output
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        
        print(f"Audio duration: {duration:.2f} seconds")
        return duration
        
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        # Return a sensible default duration if ffmpeg fails
        return 7.0

def reset_session():
    """Reset the session to clear used phrases (useful for testing)"""
    global USED_PHRASES, SESSION_COUNTER
    USED_PHRASES.clear()
    SESSION_COUNTER = 0
    print("Session reset - phrase tracking cleared")
