#!/usr/bin/env python3
"""
Test script for Gemini Document Analysis
Usage: python test_gemini_document.py <file_path> <gemini_api_key>
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend src to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.document.document_processor import DocumentProcessor

async def test_gemini_document_analysis():
    """Test Gemini document analysis with various file types"""
    
    if len(sys.argv) < 3:
        print("Usage: python test_gemini_document.py <file_path> <gemini_api_key>")
        print("Example: python test_gemini_document.py sample.pdf your_gemini_api_key")
        return
    
    file_path = sys.argv[1]
    api_key = sys.argv[2]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return
    
    print(f"🚀 Testing Gemini Document Analysis")
    print(f"📄 File: {file_path}")
    print(f"🔑 API Key: {api_key[:8]}...")
    print("-" * 50)
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Detect file type
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # Fallback based on extension
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            mime_type = 'application/pdf'
        elif ext in ['.doc', '.docx']:
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext in ['.ppt', '.pptx']:
            mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        elif ext in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        elif ext == '.txt':
            mime_type = 'text/plain'
        else:
            mime_type = 'application/octet-stream'
    
    print(f"🔍 Detected MIME type: {mime_type}")
    print("-" * 50)
    
    try:
        # Process document
        result = await processor.process_document(
            file_path=file_path,
            mime_type=mime_type,
            ai_provider="gemini",
            api_key=api_key
        )
        
        # Display results
        if result["success"]:
            print("✅ SUCCESS: Document processed successfully")
            print("-" * 50)
            
            print("📝 EXTRACTED TEXT:")
            print(result["extracted_text"][:500] + "..." if len(result["extracted_text"]) > 500 else result["extracted_text"])
            print("-" * 50)
            
            print("🧠 AI ANALYSIS:")
            print(result["analysis"][:800] + "..." if len(result["analysis"]) > 800 else result["analysis"])
            print("-" * 50)
            
            print("📋 SUMMARY:")
            print(result["summary"])
            print("-" * 50)
            
            print("📊 METADATA:")
            for key, value in result.get("metadata", {}).items():
                print(f"  {key}: {value}")
            
        else:
            print("❌ FAILED: Document processing failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

def test_gemini_installation():
    """Test if Gemini library is properly installed"""
    print("🔧 Testing Gemini Installation...")
    
    try:
        from google import genai
        print("✅ google-genai library is installed")
        
        # Test basic import
        from google.genai import types
        print("✅ genai.types is available")
        
        print("✅ Gemini setup looks good!")
        return True
        
    except ImportError as e:
        print(f"❌ Gemini library not installed: {e}")
        print("💡 Install with: pip install google-genai>=0.3.0")
        return False
    
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return False

async def test_document_types():
    """Test supported document types"""
    print("📋 Supported Document Types:")
    
    processor = DocumentProcessor()
    
    print("\n🖼️  Image types:")
    for mime_type in sorted(processor.supported_image_types):
        print(f"  - {mime_type}")
    
    print("\n📄 Document types:")
    for mime_type in sorted(processor.supported_document_types):
        print(f"  - {mime_type}")
    
    print("\n🎬 Video types:")
    for mime_type in sorted(processor.supported_video_types):
        print(f"  - {mime_type}")
    
    print("\n🎵 Audio types:")
    for mime_type in sorted(processor.supported_audio_types):
        print(f"  - {mime_type}")

if __name__ == "__main__":
    print("🧪 Gemini Document Processor Test Suite")
    print("=" * 50)
    
    # Test installation first
    if not test_gemini_installation():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Show supported types
    asyncio.run(test_document_types())
    
    print("\n" + "=" * 50)
    
    # Run document analysis if file provided
    if len(sys.argv) >= 3:
        asyncio.run(test_gemini_document_analysis())
    else:
        print("💡 To test document analysis:")
        print("   python test_gemini_document.py <file_path> <gemini_api_key>")
        print("\n📋 Example commands:")
        print("   python test_gemini_document.py sample.pdf your_api_key")
        print("   python test_gemini_document.py image.jpg your_api_key")
        print("   python test_gemini_document.py document.docx your_api_key")
        print("   python test_gemini_document.py presentation.pptx your_api_key")
        print("\n⚠️  Note: All prompts use English (no Vietnamese)")
        print("   Textract dependency disabled to avoid installation issues")
