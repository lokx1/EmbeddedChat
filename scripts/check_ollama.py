#!/usr/bin/env python3
"""
Check Ollama status and setup
"""
import requests
import json

def check_ollama():
    """Check if Ollama is running and what models are available"""
    print("🔍 Checking Ollama Status")
    print("="*30)
    
    try:
        # Check if Ollama server is running
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✅ Ollama is running on localhost:11434")
            print(f"📦 Available models: {len(models)}")
            
            if models:
                for model in models[:5]:  # Show first 5 models
                    print(f"   - {model['name']} ({model.get('size', 'Unknown size')})")
            else:
                print("⚠️  No models installed")
                print("💡 Install a model with: ollama pull llama3.2")
            
            return True, models
        else:
            print(f"❌ Ollama server responded with status: {response.status_code}")
            return False, []
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama server is not running")
        print("💡 Start Ollama with: ollama serve")
        return False, []
    except Exception as e:
        print(f"❌ Error checking Ollama: {str(e)}")
        return False, []

def test_ollama_generation():
    """Test Ollama text generation"""
    print(f"\n🤖 Testing Ollama Generation")
    print("="*35)
    
    # Try to use a common model
    test_models = ['llama3.2', 'llama2', 'codellama', 'mistral']
    
    for model in test_models:
        try:
            print(f"🧪 Testing model: {model}")
            
            payload = {
                "model": model,
                "prompt": "Generate a brief description for a beautiful sunset image:",
                "stream": False
            }
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                
                print(f"✅ Success with {model}!")
                print(f"📝 Generated: {generated_text[:100]}...")
                return model, generated_text
            else:
                print(f"❌ Failed with {model}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with {model}: {str(e)}")
            continue
    
    print("⚠️  No working models found")
    return None, None

if __name__ == "__main__":
    print("🚀 Ollama Integration Check")
    print("="*40)
    
    # Check status
    running, models = check_ollama()
    
    if running and models:
        # Test generation
        working_model, sample_text = test_ollama_generation()
        
        if working_model:
            print(f"\n🎉 Ollama is ready for integration!")
            print(f"✅ Recommended model: {working_model}")
            print(f"✅ Generation working")
        else:
            print(f"\n⚠️  Ollama is running but no models work")
    else:
        print(f"\n❌ Ollama setup needed")
        print(f"📋 Setup steps:")
        print(f"   1. Install Ollama: https://ollama.ai")
        print(f"   2. Start server: ollama serve")
        print(f"   3. Install model: ollama pull llama3.2")
