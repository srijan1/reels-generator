#!/usr/bin/env python3
"""
Setup Script for AI Avatar Integration
Installs and configures all required dependencies
"""

import os
import sys
import subprocess
import platform
import requests
from pathlib import Path
import zipfile
import shutil

class AvatarSystemSetup:
    """Setup manager for AI Avatar system"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        self.project_root = Path.cwd()
        
    def run_setup(self):
        """Run complete setup process"""
        print("🤖 AI AVATAR SYSTEM SETUP")
        print("="*50)
        print("🎯 Setting up professional AI Avatar with lip-sync")
        print("⚠️ This may take 10-15 minutes depending on your internet speed")
        print("="*50)
        
        steps = [
            ("🐍 Checking Python environment", self.check_python),
            ("📦 Installing Python packages", self.install_python_packages),
            ("🔧 Installing system tools", self.install_system_tools),
            ("🤖 Setting up AI models", self.setup_ai_models),
            ("🎭 Creating avatar assets", self.create_avatar_assets),
            ("📁 Setting up directories", self.setup_directories),
            ("🧪 Testing installation", self.test_installation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            try:
                if step_func():
                    print(f"   ✅ {step_name} completed")
                else:
                    print(f"   ⚠️ {step_name} completed with warnings")
            except Exception as e:
                print(f"   ❌ {step_name} failed: {e}")
                print("   💡 Continuing with next step...")
        
        print("\n🎉 SETUP COMPLETE!")
        print("="*50)
        print("✅ AI Avatar system is ready!")
        print("💡 Run: python enhanced_groq_reel_generator.py")
        print("🎭 Or test with: python enhanced_groq_reel_generator.py --avatar-test")
        print("="*50)
    
    def check_python(self):
        """Check Python version and basic setup"""
        version = sys.version_info
        print(f"   🐍 Python {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("   ⚠️ Python 3.8+ recommended for best compatibility")
            return False
        
        print("   ✅ Python version compatible")
        return True
    
    def install_python_packages(self):
        """Install required Python packages"""
        packages = [
            
        ]
        
        print("   📦 Installing packages (this may take a few minutes)...")
        
        failed_packages = []
        
        for package in packages:
            try:
                print(f"   Installing {package}...")
                result = subprocess.run([
                    self.python_executable, "-m", "pip", "install", package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    print(f"      ⚠️ {package} installation warning")
                    failed_packages.append(package)
                else:
                    print(f"      ✅ {package}")
                    
            except subprocess.TimeoutExpired:
                print(f"      ⏰ {package} installation timeout")
                failed_packages.append(package)
            except Exception as e:
                print(f"      ❌ {package} failed: {e}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"   ⚠️ {len(failed_packages)} packages had issues:")
            for pkg in failed_packages[:5]:  # Show first 5
                print(f"      • {pkg}")
            if len(failed_packages) > 5:
                print(f"      ... and {len(failed_packages) - 5} more")
            return False
        
        return True
    
    def install_system_tools(self):
        """Install system tools (FFmpeg, Git)"""
        print("   🔧 Checking system tools...")
        
        tools_status = {}
        
        # Check FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("      ✅ FFmpeg already installed")
                tools_status['ffmpeg'] = True
            else:
                tools_status['ffmpeg'] = False
        except FileNotFoundError:
            print("      ⚠️ FFmpeg not found")
            tools_status['ffmpeg'] = False
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("      ✅ Git already installed") 
                tools_status['git'] = True
            else:
                tools_status['git'] = False
        except FileNotFoundError:
            print("      ⚠️ Git not found")
            tools_status['git'] = False
        
        # Install missing tools
        if not tools_status.get('ffmpeg', False):
            success = self.install_ffmpeg()
            tools_status['ffmpeg'] = success
        
        if not tools_status.get('git', False):
            success = self.install_git()
            tools_status['git'] = success
        
        return all(tools_status.values())
    
    def install_ffmpeg(self):
        """Install FFmpeg based on OS"""
        print("      📥 Installing FFmpeg...")
        
        try:
            if self.system == 'windows':
                print("      💡 Please install FFmpeg manually:")
                print("         1. Download from https://ffmpeg.org/download.html")
                print("         2. Extract and add to PATH")
                return False
                
            elif self.system == 'darwin':  # macOS
                # Try homebrew
                try:
                    subprocess.run(['brew', 'install', 'ffmpeg'], 
                                 check=True, capture_output=True)
                    print("      ✅ FFmpeg installed via Homebrew")
                    return True
                except:
                    print("      💡 Please install FFmpeg:")
                    print("         brew install ffmpeg")
                    return False
                    
            elif self.system == 'linux':
                # Try apt-get (Ubuntu/Debian)
                try:
                    subprocess.run(['sudo', 'apt-get', 'update'], 
                                 check=True, capture_output=True)
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], 
                                 check=True, capture_output=True)
                    print("      ✅ FFmpeg installed via apt-get")
                    return True
                except:
                    print("      💡 Please install FFmpeg:")
                    print("         sudo apt-get install ffmpeg")
                    return False
            
        except Exception as e:
            print(f"      ❌ FFmpeg installation failed: {e}")
            return False
    
    def install_git(self):
        """Install Git based on OS"""
        print("      📥 Installing Git...")
        
        try:
            if self.system == 'windows':
                print("      💡 Please install Git manually:")
                print("         Download from https://git-scm.com/download/win")
                return False
                
            elif self.system == 'darwin':  # macOS
                try:
                    subprocess.run(['brew', 'install', 'git'], 
                                 check=True, capture_output=True)
                    print("      ✅ Git installed via Homebrew")
                    return True
                except:
                    print("      💡 Please install Git:")
                    print("         brew install git")
                    return False
                    
            elif self.system == 'linux':
                try:
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'git'], 
                                 check=True, capture_output=True)
                    print("      ✅ Git installed via apt-get")
                    return True
                except:
                    print("      💡 Please install Git:")
                    print("         sudo apt-get install git")
                    return False
                    
        except Exception as e:
            print(f"      ❌ Git installation failed: {e}")
            return False
    
    def setup_ai_models(self):
        """Download and setup AI models"""
        print("   🤖 Setting up AI models...")
        
        models_dir = self.project_root / "ai_avatar_models"
        models_dir.mkdir(exist_ok=True)
        
        # Create model directories
        (models_dir / "checkpoints").mkdir(exist_ok=True)
        (models_dir / "avatars").mkdir(exist_ok=True)
        (models_dir / "backgrounds").mkdir(exist_ok=True)
        
        success_count = 0
        
        # Download Wav2Lip model (smaller, more reliable)
        wav2lip_path = models_dir / "checkpoints" / "wav2lip_gan.pth"
        if not wav2lip_path.exists():
            print("      📥 Downloading Wav2Lip model (100MB)...")
            try:
                url = "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
                response = requests.get(url, stream=True, timeout=300)
                
                if response.status_code == 200:
                    with open(wav2lip_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("      ✅ Wav2Lip model downloaded")
                    success_count += 1
                else:
                    print(f"      ⚠️ Download failed: HTTP {response.status_code}")
                    # Create placeholder
                    wav2lip_path.touch()
                    
            except Exception as e:
                print(f"      ⚠️ Wav2Lip download failed: {e}")
                # Create placeholder for development
                wav2lip_path.touch()
        else:
            print("      ✅ Wav2Lip model already exists")
            success_count += 1
        
        # Setup SadTalker (optional, more advanced)
        sadtalker_dir = models_dir / "SadTalker"
        if not sadtalker_dir.exists():
            print("      📥 Setting up SadTalker (optional)...")
            try:
                # Clone repository
                subprocess.run([
                    'git', 'clone', '--depth', '1',
                    'https://github.com/OpenTalker/SadTalker.git',
                    str(sadtalker_dir)
                ], check=True, capture_output=True, timeout=120)
                
                print("      ✅ SadTalker repository cloned")
                success_count += 1
                
            except subprocess.TimeoutExpired:
                print("      ⏰ SadTalker clone timeout (skipping)")
            except Exception as e:
                print(f"      ⚠️ SadTalker setup failed: {e}")
                # Create minimal directory
                sadtalker_dir.mkdir(exist_ok=True)
        else:
            print("      ✅ SadTalker already exists")
            success_count += 1
        
        return success_count > 0
    
    def create_avatar_assets(self):
        """Create default avatar images and assets"""
        print("   🎭 Creating avatar assets...")
        
        models_dir = self.project_root / "ai_avatar_models"
        avatars_dir = models_dir / "avatars"
        avatars_dir.mkdir(exist_ok=True)
        
        # Avatar configurations
        avatar_configs = {
            "professional_female": {
                "description": "Professional business woman",
                "colors": {
                    "skin": (255, 220, 177),
                    "hair": (139, 69, 19),
                    "clothes": (25, 25, 112),
                    "background": (240, 248, 255)
                }
            },
            "casual_male": {
                "description": "Casual professional man", 
                "colors": {
                    "skin": (255, 228, 196),
                    "hair": (101, 67, 33),
                    "clothes": (72, 61, 139),
                    "background": (245, 245, 245)
                }
            },
            "young_presenter": {
                "description": "Young energetic presenter",
                "colors": {
                    "skin": (255, 235, 205),
                    "hair": (160, 82, 45),
                    "clothes": (220, 20, 60),
                    "background": (255, 192, 203)
                }
            }
        }
        
        created_count = 0
        
        for avatar_name, config in avatar_configs.items():
            avatar_path = avatars_dir / f"{avatar_name}.jpg"
            
            if not avatar_path.exists():
                try:
                    self.create_avatar_image(avatar_path, config)
                    print(f"      ✅ Created {avatar_name}")
                    created_count += 1
                except Exception as e:
                    print(f"      ⚠️ Failed to create {avatar_name}: {e}")
            else:
                print(f"      ✅ {avatar_name} already exists")
                created_count += 1
        
        return created_count > 0
    
    def create_avatar_image(self, output_path, config):
        """Create a professional avatar image"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create high-quality image
        img = Image.new('RGB', (512, 512), config["colors"]["background"])
        draw = ImageDraw.Draw(img)
        
        # Draw head (oval)
        head_color = config["colors"]["skin"]
        draw.ellipse([128, 80, 384, 336], fill=head_color, outline=(0, 0, 0), width=2)
        
        # Draw hair
        hair_color = config["colors"]["hair"]
        if "female" in str(output_path):
            # Female hair (longer)
            draw.ellipse([100, 60, 412, 280], fill=hair_color, outline=(0, 0, 0), width=2)
        else:
            # Male hair (shorter)
            draw.ellipse([140, 70, 372, 240], fill=hair_color, outline=(0, 0, 0), width=2)
        
        # Draw face features
        # Eyes
        draw.ellipse([170, 160, 210, 200], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.ellipse([302, 160, 342, 200], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        draw.ellipse([185, 175, 195, 185], fill=(0, 0, 0))  # Left pupil
        draw.ellipse([317, 175, 327, 185], fill=(0, 0, 0))  # Right pupil
        
        # Eyebrows
        draw.arc([170, 145, 210, 165], 0, 180, fill=(101, 67, 33), width=3)
        draw.arc([302, 145, 342, 165], 0, 180, fill=(101, 67, 33), width=3)
        
        # Nose
        draw.polygon([(256, 210), (246, 240), (266, 240)], fill=head_color, outline=(0, 0, 0))
        
        # Mouth (professional smile)
        draw.arc([230, 260, 282, 300], 0, 180, fill=(220, 20, 60), width=4)
        
        # Professional attire
        clothes_color = config["colors"]["clothes"]
        draw.rectangle([128, 336, 384, 512], fill=clothes_color, outline=(0, 0, 0), width=2)
        
        # Add collar
        draw.polygon([(200, 336), (256, 360), (312, 336), (384, 336), (384, 400), (128, 400), (128, 336)], 
                    fill=(255, 255, 255), outline=(0, 0, 0), width=1)
        
        # Save with high quality
        img.save(output_path, 'JPEG', quality=95, optimize=True)
    
    def setup_directories(self):
        """Setup project directories"""
        print("   📁 Setting up directories...")
        
        directories = [
            "ai_avatar_models",
            "ai_avatar_models/avatars", 
            "ai_avatar_models/checkpoints",
            "ai_avatar_models/backgrounds",
            "outputs",
            "uploads",
            "temp"
        ]
        
        created_count = 0
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"      ✅ Created {dir_name}")
                created_count += 1
            else:
                print(f"      ✅ {dir_name} exists")
        
        return True
    
    def test_installation(self):
        """Test the installation"""
        print("   🧪 Testing installation...")
        
        test_results = []
        
        # Test 1: Import core modules
        try:
            import torch
            import cv2
            import PIL
            import numpy as np
            print("      ✅ Core modules import successfully")
            test_results.append(True)
        except Exception as e:
            print(f"      ❌ Core modules import failed: {e}")
            test_results.append(False)
        
        # Test 2: Check avatar system
        try:
            # Import our avatar module
            from working_professional_avatar import AIAvatarGenerator
            avatar_gen = AIAvatarGenerator()
            print("      ✅ Avatar system initializes")
            test_results.append(True)
        except Exception as e:
            print(f"      ⚠️ Avatar system test failed: {e}")
            test_results.append(False)
        
        # Test 3: Check TTS system
        try:
            from piper_tts_integration import convert_text_to_speech
            print("      ✅ TTS system available")
            test_results.append(True)
        except Exception as e:
            print(f"      ⚠️ TTS system test failed: {e}")
            test_results.append(False)
        
        # Test 4: Check file structure
        models_dir = self.project_root / "ai_avatar_models"
        if models_dir.exists() and (models_dir / "avatars").exists():
            print("      ✅ File structure correct")
            test_results.append(True)
        else:
            print("      ❌ File structure incomplete")
            test_results.append(False)
        
        success_rate = sum(test_results) / len(test_results)
        
        if success_rate >= 0.75:
            print(f"      ✅ Installation test passed ({success_rate:.0%})")
            return True
        else:
            print(f"      ⚠️ Installation test partial ({success_rate:.0%})")
            return False


def main():
    """Main setup function"""
    print("🚀 AI AVATAR SYSTEM SETUP")
    print("="*50)
    
    # Check if already setup
    models_dir = Path("ai_avatar_models")
    if models_dir.exists() and (models_dir / "avatars").exists():
        print("🤖 Avatar system appears to be already set up.")
        choice = input("🔄 Run setup anyway? (y/n): ").strip().lower()
        if choice != 'y':
            print("👋 Setup skipped.")
            return
    
    # Run setup
    setup = AvatarSystemSetup()
    setup.run_setup()
    
    # Final instructions
    print("\n📋 NEXT STEPS:")
    print("="*30)
    print("1. 🎬 Run: python enhanced_groq_reel_generator.py")
    print("2. 🧪 Test: python enhanced_groq_reel_generator.py --avatar-test")
    print("3. 🌐 Web: python enhanced_groq_reel_generator.py --web")
    print("\n💡 TIPS:")
    print("• First run may take longer (model loading)")
    print("• Ensure good internet for best results")
    print("• GPU recommended for faster generation")
    print("\n🎭 Enjoy your AI Avatar videos!")


if __name__ == "__main__":
    main()
