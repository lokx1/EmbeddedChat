#!/usr/bin/env python3
"""
Simple test for document upload API
"""
import requests
import json
from pathlib import Path

def test_upload():
    """Test file upload"""
    # Create test file
    test_file = Path("test.txt")
    test_file.write_text("This is a test document for analysis.", encoding="utf-8")
    
    try:
        # Test upload
        url = "http://localhost:8000/api/v1/documents/upload"
        files = {'file': ('test.txt', open(test_file, 'rb'), 'text/plain')}
        
        print("🧪 Testing document upload...")
        response = requests.post(url, files=files)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"Document ID: {result['id']}")
            print(f"Status: {result['status']}")
            return result['id']
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()

def test_documents_list():
    """Test getting documents list"""
    try:
        url = "http://localhost:8000/api/v1/documents/"
        print("\n🧪 Testing documents list...")
        response = requests.get(url)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Documents list retrieved!")
            print(f"Total: {result['total']}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting simple backend test...")
    print("Make sure backend is running on http://localhost:8000")
    print("-" * 50)
    
    doc_id = test_upload()
    test_documents_list()
    
    print("\n✨ Test completed!")
