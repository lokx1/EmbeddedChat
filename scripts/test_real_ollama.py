#!/usr/bin/env python3
"""
Test Real Ollama with Available Model
"""

import requests
import json
import time

def test_ollama_with_available_model():
    """Test Ollama with the actually available model"""
    print("🚀 Testing Ollama with qwen3:8b")
    print("="*40)
    
    try:
        # Test direct Ollama API
        print("🧪 Testing direct Ollama API...")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:8b",
                "prompt": "Based on this asset request: A beautiful sunset over mountain landscape\n\nGenerate a comprehensive asset specification including technical details and style guidelines.",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            print(f"✅ Ollama generation successful!")
            print(f"📝 Generated text ({len(generated_text)} chars):")
            print(f"   {generated_text[:200]}...")
            return True
        else:
            print(f"❌ Ollama API failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_backend_with_qwen():
    """Test backend AIProcessingComponent with qwen3:8b"""
    print(f"\n🔧 Testing Backend with qwen3:8b")
    print("="*40)
    
    try:
        # Import the component
        from src.api.routes.workflow import component_registry
        
        # Get AIProcessingComponent
        ai_component = component_registry.get_component("ai_processing")
        
        if not ai_component:
            print("❌ AIProcessingComponent not found")
            return False
        
        # Test with qwen3:8b
        print("🧪 Testing AIProcessingComponent with qwen3:8b...")
        
        config = {
            "provider": "ollama",
            "model": "qwen3:8b",
            "prompt": "Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including technical details and style guidelines.",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        input_data = {
            "input": "A beautiful sunset over mountain landscape"
        }
        
        result = ai_component.execute(config, input_data)
        
        if result.get("success"):
            output = result.get("output", {})
            generated_content = output.get("generated_content", "")
            provider_used = output.get("provider", "unknown")
            model_used = output.get("model", "unknown")
            
            print(f"✅ AIProcessingComponent successful!")
            print(f"🤖 Provider: {provider_used}")
            print(f"📦 Model: {model_used}")
            print(f"📝 Generated content ({len(generated_content)} chars):")
            print(f"   {generated_content[:200]}...")
            
            # Check if it really used Ollama
            if provider_used == "ollama" and "simulation" not in generated_content.lower():
                print(f"🎯 REAL OLLAMA INTEGRATION WORKING!")
                return True
            else:
                print(f"⚠️  Still using simulation mode")
                return False
        else:
            print(f"❌ AIProcessingComponent failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Real Ollama Integration Test")
    print("="*45)
    
    # Test 1: Direct Ollama API
    ollama_works = test_ollama_with_available_model()
    
    if ollama_works:
        # Test 2: Backend integration
        backend_works = test_backend_with_qwen()
        
        if backend_works:
            print(f"\n🎉 REAL OLLAMA INTEGRATION CONFIRMED!")
            print(f"✅ Ollama API working with qwen3:8b")
            print(f"✅ Backend AIProcessingComponent using real Ollama")
            print(f"🎯 Ready for real AI workflow execution!")
        else:
            print(f"\n⚠️  Ollama works but backend still simulating")
    else:
        print(f"\n❌ Ollama API not working properly")
