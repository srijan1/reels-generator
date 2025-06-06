"""
Pexels API integration for fetching stock photos.
This module handles searching and downloading images from Pexels.
"""

import requests
import os
from PIL import Image
import io
import random

# Pexels API configuration
PEXELS_API_KEY = "MiAVhSDsukGp9HVcWRLQpxm6kjh2gWZo1MnzDtOexze5OmYYlTpq0VnI"
PEXELS_BASE_URL = "https://api.pexels.com/v1/search"

def extract_keywords_from_prompt(image_prompt):
    """
    Extract relevant search keywords from an AI image generation prompt
    
    Parameters:
    - image_prompt: The detailed prompt used for AI image generation
    
    Returns:
    - String of keywords suitable for Pexels search
    """
    # Common keywords to remove that don't help with stock photo search
    remove_words = [
        'vertical', '9:16', 'format', 'aspect', 'ratio', 'detailed', 'cinematic', 
        'lighting', 'professional', 'high', 'quality', 'authentic', 'realistic',
        'photorealistic', 'photography', 'style', 'candid', 'moment', 'scene',
        'composition', 'framing', 'shot', 'angle', 'perspective', 'view', 'image',
        'photo', 'picture', 'visual', 'illustration', 'render', 'artwork'
    ]
    
    # Keywords that often work well for stock photos
    travel_keywords = {
        'kyoto': 'kyoto japan temple',
        'japan': 'japan travel culture',
        'train station': 'train station travel',
        'torii': 'torii gates japan shrine',
        'shrine': 'japanese shrine temple',
        'temple': 'japanese temple architecture',
        'architecture': 'traditional architecture',
        'tea house': 'japanese tea ceremony',
        'travel': 'travel adventure journey',
        'backpack': 'backpacker travel adventure',
        'golden hour': 'sunset golden hour',
        'dawn': 'sunrise dawn morning',
        'misty': 'fog mist atmospheric',
        'traditional': 'traditional culture heritage'
    }
    
    # Convert to lowercase for processing
    prompt_lower = image_prompt.lower()
    
    # Find relevant keywords
    found_keywords = []
    for keyword, replacement in travel_keywords.items():
        if keyword in prompt_lower:
            found_keywords.append(replacement)
    
    # If we found specific keywords, use them
    if found_keywords:
        return ' '.join(found_keywords[:2])  # Use top 2 keyword groups
    
    # Fallback: extract important words manually
    words = image_prompt.split()
    important_words = []
    
    for word in words:
        word_clean = word.lower().strip('.,!?()[]{}":;')
        if (len(word_clean) > 3 and 
            word_clean not in remove_words and
            not word_clean.isdigit()):
            important_words.append(word_clean)
    
    # Return first few important words
    return ' '.join(important_words[:3])

def search_pexels_images(query, per_page=10):
    """
    Search for images on Pexels
    
    Parameters:
    - query: Search query string
    - per_page: Number of results to return (max 80)
    
    Returns:
    - List of image data dictionaries
    """
    headers = {
        'Authorization': PEXELS_API_KEY
    }
    
    params = {
        'query': query,
        'per_page': min(per_page, 80),  # Pexels max is 80
        'orientation': 'portrait',  # For 9:16 format
        'size': 'large'
    }
    
    try:
        print(f"🔍 Searching Pexels for: '{query}'")
        response = requests.get(PEXELS_BASE_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        photos = data.get('photos', [])
        
        print(f"📸 Found {len(photos)} photos on Pexels")
        return photos
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error searching Pexels: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error with Pexels API: {e}")
        return []

def download_pexels_image(photo_data, output_path, target_width=288, target_height=512):
    """
    Download and resize a Pexels image
    
    Parameters:
    - photo_data: Photo data from Pexels API
    - output_path: Where to save the image
    - target_width: Target width for resizing
    - target_height: Target height for resizing
    
    Returns:
    - PIL Image object or None if failed
    """
    try:
        # Get the best size URL (prefer large, fallback to medium)
        image_url = photo_data['src'].get('large', photo_data['src'].get('medium'))
        
        if not image_url:
            print("❌ No suitable image URL found")
            return None
        
        print(f"📥 Downloading image from Pexels...")
        
        # Download the image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Open with PIL
        image = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to target dimensions (9:16 aspect ratio)
        # Use smart cropping to maintain aspect ratio
        image = resize_and_crop_smart(image, target_width, target_height)
        
        # Save the image
        image.save(output_path, format="PNG", compress_level=0)
        
        print(f"✅ Pexels image saved to {output_path}")
        print(f"📊 Photographer: {photo_data.get('photographer', 'Unknown')}")
        
        return image
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading image: {e}")
        return None
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def resize_and_crop_smart(image, target_width, target_height):
    """
    Resize and crop image to exact dimensions while preserving the best content
    
    Parameters:
    - image: PIL Image object
    - target_width: Desired width
    - target_height: Desired height
    
    Returns:
    - PIL Image object with exact target dimensions
    """
    original_width, original_height = image.size
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height
    
    if original_ratio > target_ratio:
        # Image is wider than target ratio - crop width
        new_height = target_height
        new_width = int(target_height * original_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop from center
        left = (new_width - target_width) // 2
        top = 0
        right = left + target_width
        bottom = target_height
        image = image.crop((left, top, right, bottom))
        
    else:
        # Image is taller than target ratio - crop height
        new_width = target_width
        new_height = int(target_width / original_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop from center (slightly favor top for portraits)
        left = 0
        top = max(0, (new_height - target_height) // 3)  # Favor upper portion
        right = target_width
        bottom = top + target_height
        image = image.crop((left, top, right, bottom))
    
    return image

def get_pexels_image(image_prompt, output_path, target_width=288, target_height=512):
    """
    Get an image from Pexels based on an image prompt
    
    Parameters:
    - image_prompt: The original AI image generation prompt
    - output_path: Where to save the downloaded image
    - target_width: Target width for the final image
    - target_height: Target height for the final image
    
    Returns:
    - PIL Image object or None if failed
    """
    # Extract search keywords from the prompt
    search_query = extract_keywords_from_prompt(image_prompt)
    
    # Search for images
    photos = search_pexels_images(search_query, per_page=20)
    
    if not photos:
        print(f"❌ No photos found for query: '{search_query}'")
        return None
    
    # Try multiple photos until one works
    random.shuffle(photos)  # Randomize for variety
    
    for photo in photos[:5]:  # Try up to 5 photos
        try:
            image = download_pexels_image(photo, output_path, target_width, target_height)
            if image:
                return image
        except Exception as e:
            print(f"⚠️  Failed to download photo, trying next one: {e}")
            continue
    
    print(f"❌ Failed to download any photos for: '{search_query}'")
    return None

def test_pexels_api():
    """Test the Pexels API connection"""
    print("🧪 Testing Pexels API...")
    
    headers = {
        'Authorization': PEXELS_API_KEY
    }
    
    try:
        response = requests.get(
            "https://api.pexels.com/v1/search?query=travel&per_page=1", 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            if photos:
                print("✅ Pexels API is working correctly!")
                print(f"📸 Test search returned {len(photos)} photo(s)")
                return True
            else:
                print("⚠️  API works but no photos returned")
                return False
        else:
            print(f"❌ Pexels API error: {response.status_code}")
            print(f"📤 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Pexels API test failed: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Test the API
    test_pexels_api()
    
    # Test keyword extraction
    test_prompt = "Young traveler with backpack arriving at Kyoto train station, looking excited and slightly tired, golden hour lighting, candid moment, Japanese signs visible, vertical format, 9:16 aspect ratio"
    keywords = extract_keywords_from_prompt(test_prompt)
    print(f"\n🔍 Test prompt: {test_prompt}")
    print(f"🎯 Extracted keywords: {keywords}")
    
    # Test image download (uncomment to test)
    # get_pexels_image(test_prompt, "test_pexels_image.png")
