"""
Simple API Test for Google Sheets Integration
"""

import requests
import json

def test_api():
    print("🔍 Testing API Integration...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        print(f"Health Check: {response.status_code} - {response.text}")
        
        # Test templates endpoint
        response = requests.get("http://localhost:8000/api/v1/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Found {len(templates)} templates")
            for template in templates:
                print(f"   - {template['name']} (ID: {template['id']})")
        else:
            print(f"❌ Templates failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_api()
