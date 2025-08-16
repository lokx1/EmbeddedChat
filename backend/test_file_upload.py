#!/usr/bin/env python3
"""
Simple test script for file upload and analysis functionality
"""
import asyncio
import aiohttp
import json
import sys
from pathlib import Path
import os

API_BASE_URL = "http://localhost:8000/api/v1"

async def test_file_upload():
    """Test file upload functionality"""
    print("🚀 Testing File Upload and Analysis API...")
    
    # Test file path - you can create a simple test file
    test_file_path = Path("test_document.txt")
    
    # Create a test document if it doesn't exist
    if not test_file_path.exists():
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("""
            This is a test document for AI analysis.
            
            It contains some sample text that demonstrates:
            1. Basic text content
            2. Multiple paragraphs
            3. Lists and formatting
            
            The AI should be able to analyze this content and provide insights.
            """)
        print(f"📝 Created test file: {test_file_path}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Upload document
            print("\n1️⃣ Testing document upload...")
            
            data = aiohttp.FormData()
            data.add_field('file', 
                          open(test_file_path, 'rb'),
                          filename='test_document.txt',
                          content_type='text/plain')
            data.add_field('ai_provider', 'openai')
            # Add your OpenAI API key here for testing
            data.add_field('api_key', 'sk-your-openai-api-key-here')
            
            async with session.post(f"{API_BASE_URL}/documents/upload", data=data) as response:
                if response.status == 201:
                    upload_result = await response.json()
                    print(f"✅ Upload successful! Document ID: {upload_result['id']}")
                    print(f"   Status: {upload_result['status']}")
                    print(f"   Original filename: {upload_result['original_filename']}")
                    if upload_result.get('summary'):
                        print(f"   AI Summary: {upload_result['summary'][:100]}...")
                    
                    document_id = upload_result['id']
                    
                    # Test 2: Get document content
                    print(f"\n2️⃣ Testing document content retrieval...")
                    async with session.get(f"{API_BASE_URL}/documents/{document_id}/content") as content_response:
                        if content_response.status == 200:
                            content_result = await content_response.json()
                            print(f"✅ Content retrieved successfully!")
                            print(f"   Content length: {len(content_result['content'])} characters")
                            print(f"   Content preview: {content_result['content'][:100]}...")
                        else:
                            print(f"❌ Failed to get content: {content_response.status}")
                    
                    # Test 3: Test chat with attached document
                    print(f"\n3️⃣ Testing chat with attached document...")
                    chat_payload = {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "apiKey": "sk-your-openai-api-key-here",  # Replace with actual key
                        "temperature": 0.7,
                        "maxTokens": 1000,
                        "systemPrompt": "You are a helpful AI assistant.",
                        "message": "Please analyze the attached document and provide a summary.",
                        "conversationHistory": [],
                        "attachedDocuments": [document_id]
                    }
                    
                    async with session.post(f"{API_BASE_URL}/chat/send", 
                                          json=chat_payload,
                                          headers={'Content-Type': 'application/json'}) as chat_response:
                        if chat_response.status == 200:
                            chat_result = await chat_response.json()
                            print(f"✅ Chat with document successful!")
                            print(f"   AI Response: {chat_result['content'][:200]}...")
                        else:
                            error_text = await chat_response.text()
                            print(f"❌ Chat failed: {chat_response.status}")
                            print(f"   Error: {error_text}")
                    
                    # Test 4: Get documents list
                    print(f"\n4️⃣ Testing documents list...")
                    async with session.get(f"{API_BASE_URL}/documents/") as list_response:
                        if list_response.status == 200:
                            list_result = await list_response.json()
                            print(f"✅ Documents list retrieved!")
                            print(f"   Total documents: {list_result['total']}")
                            print(f"   Documents in response: {len(list_result['documents'])}")
                        else:
                            print(f"❌ Failed to get documents list: {list_response.status}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Upload failed: {response.status}")
                    print(f"   Error: {error_text}")
                    
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
            print("   Make sure the backend server is running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Cleanup
    if test_file_path.exists():
        test_file_path.unlink()
        print(f"\n🧹 Cleaned up test file: {test_file_path}")
    
    print("\n✨ Test completed!")

def print_setup_instructions():
    """Print setup instructions"""
    print("""
📋 Setup Instructions:

1. Make sure your backend server is running:
   cd backend
   python -m uvicorn main:app --reload --port 8000

2. Install required dependencies in backend:
   pip install PyPDF2 PyMuPDF Pillow python-docx openpyxl anthropic openai

3. Set your OpenAI API key in the test script above (line with 'sk-your-openai-api-key-here')

4. Run this test script:
   python test_file_upload.py

🚨 Important Notes:
- Replace 'sk-your-openai-api-key-here' with your actual OpenAI API key
- Make sure you have authentication disabled or properly configured
- The test creates a temporary text file for testing
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_setup_instructions()
    else:
        print_setup_instructions()
        print("\n" + "="*60)
        asyncio.run(test_file_upload())
