#!/usr/bin/env python3
"""
Simple script to install document processing dependencies
No textract - just the essential packages
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🚀 Installing Document Processing Dependencies")
    print("=" * 50)
    
    # Essential packages (no system dependencies)
    packages = [
        "python-pptx>=0.6.21",
        "pylatexenc>=2.10", 
        "striprtf>=0.0.26",
        "odfpy>=1.4.0",
        "google-genai>=0.3.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "PyPDF2>=3.0.1",
        "PyMuPDF>=1.23.0", 
        "python-docx>=0.8.11",
        "openpyxl>=3.1.2",
        "Pillow>=10.0.0",
        "aiohttp>=3.8.0",
        "httpx>=0.24.0"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary: {success_count}/{len(packages)} packages installed")
    
    if success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("\n💡 You can now test with:")
        print("   python test_gemini_document.py <file> <api_key>")
    else:
        print("⚠️  Some packages failed to install")
        print("   You may still be able to use basic functionality")
    
    print("\n🔧 Supported formats:")
    print("  📄 PDF, DOCX, PPTX, LaTeX, RTF, ODT")
    print("  🖼️  Images (JPG, PNG, GIF, WebP)")
    print("  🎬 Videos (MP4, MOV, AVI, WebM) - Gemini only")
    print("  🎵 Audio (MP3, WAV, AAC, OGG) - Gemini only")

if __name__ == "__main__":
    main()
