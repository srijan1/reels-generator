from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, Response
import os
import time
import threading
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()
import uuid

# Import your existing modules
try:
    from groq_script_generator import generate_story_script, get_user_story_prompt
    from updated_main_groq import main as generate_video_main
    from piper_tts_integration import clear_tts, convert_text_to_speech, get_audio_duration
    import groq_reel_generator
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this to a secure secret key

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'txt', 'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variables to track video generation status
video_generation_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with the video generation interface"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_video():
    """Handle video generation request"""
    try:
        # Get form data
        story_topic = request.form.get('story_topic', '').strip()
        audience = request.form.get('audience', 'general')
        duration = float(request.form.get('duration', 1.0))
        language = request.form.get('language', 'en')
        
        if not story_topic:
            return jsonify({'error': 'Story topic is required'}), 400
        
        # Generate unique ID for this request
        generation_id = str(uuid.uuid4())
        
        # Initialize status
        video_generation_status[generation_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing video generation...',
            'video_path': None,
            'error': None
        }
        
        # Start video generation in background thread
        thread = threading.Thread(
            target=generate_video_background,
            args=(generation_id, story_topic, audience, duration, language)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'generation_id': generation_id, 'status': 'started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_video_background(generation_id, story_topic, audience, duration, language):
    """Background task to generate video"""
    try:
        from groq_script_generator import generate_story_script
        from updated_main_groq import main as generate_video_main
        # Update status
        video_generation_status[generation_id].update({
            'status': 'generating_script',
            'progress': 10,
            'message': 'Generating story script...'
        })
        
        # Generate script using Groq API
        print(f"Generating script for: {story_topic}")
        script_data = generate_story_script(
            story_topic=story_topic,
            audience=audience,
            duration_minutes=duration,
            num_segments=8
        )
        
        if not script_data or 'segments' not in script_data:
            raise Exception("Failed to generate script")
        
        # Update status
        video_generation_status[generation_id].update({
            'status': 'generating_images',
            'progress': 25,
            'message': 'Creating AI-generated images...'
        })
        
        # Small delay to show progress
        import time
        time.sleep(1)
        
        # Update status
        video_generation_status[generation_id].update({
            'status': 'generating_audio',
            'progress': 40,
            'message': 'Generating crystal-clear audio narration...'
        })
        
        time.sleep(1)
        
        # Update status
        video_generation_status[generation_id].update({
            'status': 'creating_video',
            'progress': 60,
            'message': 'Assembling video with effects and transitions...'
        })
        
        # Generate video using the main function
        print(f"Starting video generation with script: {script_data.get('title', 'Custom Story')}")
        result = generate_video_main(script_data)
        
        # Update status
        video_generation_status[generation_id].update({
            'status': 'finalizing',
            'progress': 85,
            'message': 'Finalizing video and audio synchronization...'
        })
        
        # Look for the generated video in common locations
        video_path = None
        possible_paths = [
            result,  # Direct result from main function
            "narrative_story_final_with_audio.mp4",  # Common output name
            "./narrative_story_final_with_audio.mp4",  # With relative path
        ]
        
        # Also check for timestamped directories
        import glob
        timestamped_videos = glob.glob("./story_reel_*/5_final/*.mp4")
        if timestamped_videos:
            # Get the most recent one
            timestamped_videos.sort(key=os.path.getmtime, reverse=True)
            possible_paths.extend(timestamped_videos[:3])  # Add top 3 most recent
        
        # Add any recent MP4 files in current directory
        current_time = time.time()
        for file in glob.glob("*.mp4"):
            file_time = os.path.getmtime(file)
            # If file was created in the last 10 minutes
            if current_time - file_time < 600:
                possible_paths.append(file)
        
        print(f"Searching for video in paths: {possible_paths}")
        
        # Find the actual video file
        for path in possible_paths:
            if path and os.path.exists(str(path)):
                video_path = str(path)
                print(f"✅ Found video at: {video_path}")
                break
        
        if video_path and os.path.exists(video_path):
            # Copy to outputs directory for easier access
            output_filename = f"video_{generation_id}.mp4"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            try:
                import shutil
                shutil.copy2(video_path, output_path)
                print(f"📁 Video copied to: {output_path}")
                final_video_path = output_path
            except Exception as e:
                print(f"⚠️ Failed to copy video: {e}, using original path")
                final_video_path = video_path
            
            # Update status - success
            video_generation_status[generation_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Video generation completed successfully!',
                'video_path': final_video_path
            })
            print(f"🎉 Video generation completed successfully: {final_video_path}")
        else:
            print(f"❌ Video not found in any of these locations: {possible_paths}")
            # List all MP4 files for debugging
            all_mp4s = glob.glob("**/*.mp4", recursive=True)
            print(f"🔍 All MP4 files found: {all_mp4s}")
            raise Exception(f"Video generation completed but output file not found. Searched: {len(possible_paths)} locations")
            
    except Exception as e:
        print(f"❌ Video generation error: {e}")
        # Update status - error
        video_generation_status[generation_id].update({
            'status': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}',
            'error': str(e)
        })

@app.route('/status/<generation_id>')
def check_status(generation_id):
    """Check the status of video generation"""
    if generation_id not in video_generation_status:
        return jsonify({'error': 'Invalid generation ID'}), 404
    
    return jsonify(video_generation_status[generation_id])

@app.route('/video/<generation_id>')
def stream_video(generation_id):
    """Stream video for preview with range support"""
    if generation_id not in video_generation_status:
        return jsonify({'error': 'Invalid generation ID'}), 404
    
    status = video_generation_status[generation_id]
    
    if status['status'] != 'completed' or not status['video_path']:
        return jsonify({'error': 'Video not ready'}), 400
    
    video_path = status['video_path']
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    # Get file size
    file_size = os.path.getsize(video_path)
    
    # Handle range requests for video streaming
    range_header = request.headers.get('Range', None)
    if range_header:
        # Parse range header
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Read the requested chunk
        with open(video_path, 'rb') as f:
            f.seek(start)
            chunk_size = end - start + 1
            data = f.read(chunk_size)
        
        response = Response(
            data,
            206,  # Partial Content
            headers={
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(chunk_size),
                'Content-Type': 'video/mp4',
            }
        )
        return response
    else:
        # Serve entire file
        return send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=False,
            download_name=f'video_{generation_id}.mp4'
        )

@app.route('/download/<generation_id>')
def download_video(generation_id):
    """Download the generated video"""
    if generation_id not in video_generation_status:
        return jsonify({'error': 'Invalid generation ID'}), 404
    
    status = video_generation_status[generation_id]
    
    if status['status'] != 'completed' or not status['video_path']:
        return jsonify({'error': 'Video not ready for download'}), 400
    
    if not os.path.exists(status['video_path']):
        return jsonify({'error': 'Video file not found'}), 404
    
    return send_file(
        status['video_path'],
        as_attachment=True,
        download_name=f'generated_video_{generation_id}.mp4'
    )

@app.route('/test-audio', methods=['POST'])
def test_audio():
    """Test audio generation"""
    try:
        # Test English audio
        english_test_text = "Hello, this is a test of the English audio system. The speech should be crystal clear."
        english_output = "test_english_clarity.mp3"
        
        print("🔊 Generating English test audio...")
        result_en = convert_text_to_speech(
            english_test_text, 
            english_output, 
            'female',
            'en'
        )
        
        # Test Hindi audio
        hindi_test_text = "यह हिंदी ऑडियो की गुणवत्ता का परीक्षण है।"
        hindi_output = "test_hindi_clarity.mp3"
        
        print("🔊 Generating Hindi test audio...")
        result_hi = convert_text_to_speech(
            hindi_test_text, 
            hindi_output, 
            'female',
            'hi'
        )
        
        result = {
            'status': 'success',
            'message': 'Audio test completed',
            'english_audio': english_output if result_en and os.path.exists(english_output) else None,
            'hindi_audio': hindi_output if result_hi and os.path.exists(hindi_output) else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/system-status')
def system_status():
    """Check system status and dependencies"""
    try:
        # Import check function
        from groq_reel_generator import check_system_status
        
        # This will print to console, but we'll return a JSON response
        # You might want to modify check_system_status to return data instead of printing
        
        import sys
        
        # Basic dependency check
        dependencies = [
            ('pyttsx3', 'Text-to-Speech Engine'),
            ('pydub', 'Audio Processing'),
            ('torch', 'PyTorch for AI Models'),
            ('transformers', 'Hugging Face Transformers'),
            ('langdetect', 'Language Detection'),
            ('groq', 'Groq API Client'),
            ('requests', 'HTTP Requests'),
            ('PIL', 'Image Processing'),
            ('cv2', 'OpenCV for Video'),
            ('numpy', 'Numerical Computing')
        ]
        
        status_results = []
        
        for module_name, description in dependencies:
            try:
                __import__(module_name)
                status_results.append({
                    'module': module_name,
                    'description': description,
                    'status': 'OK'
                })
            except ImportError:
                status_results.append({
                    'module': module_name,
                    'description': description,
                    'status': 'MISSING'
                })
        
        return jsonify({
            'python_version': sys.version,
            'dependencies': status_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio-settings')
def audio_settings():
    """Get current audio settings"""
    try:
        from piper_tts_integration import clear_tts, PYTTSX3_AVAILABLE, TORCH_AVAILABLE
        
        settings = {
            'voice_settings': clear_tts.clarity_settings if hasattr(clear_tts, 'clarity_settings') else {},
            'model_configs': clear_tts.language_models if hasattr(clear_tts, 'language_models') else {},
            'initialized_languages': list(clear_tts.supported_languages) if hasattr(clear_tts, 'supported_languages') else [],
            'pyttsx3_available': PYTTSX3_AVAILABLE,
            'torch_available': TORCH_AVAILABLE
        }
        
        return jsonify(settings)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-script', methods=['POST'])
def upload_script():
    """Upload a custom script file"""
    try:
        if 'script_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['script_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Try to parse the script
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    if filename.endswith('.json'):
                        script_data = json.load(f)
                    else:
                        # Assume it's a text file with story topic
                        content = f.read()
                        script_data = {'story_topic': content}
                
                return jsonify({
                    'status': 'success',
                    'filename': filename,
                    'script_data': script_data
                })
                
            except Exception as e:
                return jsonify({'error': f'Failed to parse script: {str(e)}'}), 400
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/<generation_id>')
def debug_generation(generation_id):
    """Debug endpoint to check video generation details"""
    if generation_id not in video_generation_status:
        return jsonify({'error': 'Invalid generation ID'}), 404
    
    status = video_generation_status[generation_id]
    
    # Search for video files
    import glob
    all_mp4s = glob.glob("**/*.mp4", recursive=True)
    recent_mp4s = []
    
    import time
    current_time = time.time()
    for file in all_mp4s:
        try:
            file_time = os.path.getmtime(file)
            if current_time - file_time < 1800:  # Last 30 minutes
                recent_mp4s.append({
                    'path': file,
                    'size': os.path.getsize(file),
                    'modified': time.ctime(file_time)
                })
        except:
            pass
    
    debug_info = {
        'generation_status': status,
        'all_mp4_files': all_mp4s,
        'recent_mp4_files': recent_mp4s,
        'working_directory': os.getcwd(),
        'outputs_directory': app.config['OUTPUT_FOLDER'],
        'outputs_exists': os.path.exists(app.config['OUTPUT_FOLDER'])
    }
    
    return jsonify(debug_info)

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import sys
    
    # Get port from command line arguments
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 5000
    
    print("🎬 GROQ REEL GENERATOR - Flask Web Application")
    print("="*60)
    print("🌐 Starting web server...")
    print(f"📱 Access the application at: http://localhost:{port}")
    print("🎯 Features:")
    print("   ✅ Web-based video generation")
    print("   ✅ Real-time progress tracking")
    print("   ✅ Audio quality testing")
    print("   ✅ System status monitoring")
    print("   ✅ Custom script upload")
    print("="*60)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=port)
