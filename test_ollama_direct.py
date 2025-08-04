#!/usr/bin/env python3
"""
Test Ollama API directly to understand response structure
"""

import requests
import json

def test_ollama_api():
    print("🦙 Testing Ollama API directly...")
    
    try:
        # Test if Ollama is responsive
        print("📡 Checking Ollama health...")
        health_response = requests.get('http://localhost:11434/api/tags', timeout=5)
        print(f"Health check: {health_response.status_code}")
        
        if health_response.status_code == 200:
            tags = health_response.json()
            print(f"Available models: {[model['name'] for model in tags.get('models', [])]}")
        
        # Test actual generation
        print("\n🤖 Testing Ollama generation...")
        
        payload = {
            "model": "gemma3:1b",  # Use available model
            "prompt": "Tạo một câu chuyện ngắn về pha cafe. Viết khoảng 100 từ.",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 500
            }
        }
        
        print(f"📤 Sending request to Ollama...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=payload,
            timeout=60
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 Ollama response structure:")
            print(f"   Keys: {list(result.keys())}")
            
            ai_text = result.get('response', '').strip()
            print(f"   Response text length: {len(ai_text)}")
            print(f"   Response preview: '{ai_text[:200]}...'")
            
            # Show what our backend would create
            print(f"\n🏗️ Backend would create this structure:")
            generated_content = {
                "type": "ollama_asset_generation",
                "description": "Test description",
                "output_format": "PNG",
                "generated_url": "https://ollama-assets.local/png/1234.png",
                "ai_response": ai_text,  # ⭐ This is the key field!
                "metadata": {
                    "model": "llama3.2",
                    "provider": "ollama",
                    "quality": "local_generation",
                    "size": "1024x1024",
                    "processing_time": f"{result.get('total_duration', 0) / 1000000:.1f}ms",
                    "tokens_evaluated": result.get('eval_count', 0),
                    "eval_duration": f"{result.get('eval_duration', 0) / 1000000:.1f}ms"
                },
                "prompt_used": payload["prompt"][:200] + "..."
            }
            
            print(f"   Structure keys: {list(generated_content.keys())}")
            print(f"   ai_response field: '{generated_content['ai_response'][:100]}...'")
            
            # Test our extraction logic on this structure
            print(f"\n🔍 Testing extraction logic:")
            ai_response = generated_content
            
            if "ai_response" in ai_response and isinstance(ai_response["ai_response"], str):
                extracted_text = ai_response["ai_response"]
                print(f"   ✅ SUCCESS: Extracted '{extracted_text[:100]}...' (length: {len(extracted_text)})")
            else:
                print(f"   ❌ FAILED: Could not extract ai_response")
        
        else:
            print(f"❌ Ollama error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ollama_api()
