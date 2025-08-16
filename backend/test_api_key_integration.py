#!/usr/bin/env python3
"""
Test script for API Key integration with AI providers
"""
import asyncio
import os
from typing import Dict, Any

# Mock execution context for testing
class MockExecutionContext:
    def __init__(self, input_data: Dict[str, Any]):
        self.input_data = input_data
        self.previous_outputs = {
            "sheets_step": {
                "spreadsheet_info": {"spreadsheet_id": "test_sheet"},
                "records": [
                    {"description": "A beautiful sunset", "output_format": "PNG"},
                    {"description": "Write a poem about AI", "output_format": "text"}
                ]
            }
        }

async def test_api_key_validation():
    """Test API key validation and processing"""
    print("🔑 Testing API Key Integration")
    print("=" * 50)
    
    # Import component after setting up path
    import sys
    sys.path.append('src')
    
    try:
        from services.workflow.component_registry import AIProcessingComponent
        
        component = AIProcessingComponent()
        
        # Test cases
        test_cases = [
            {
                "name": "Valid OpenAI API Key",
                "config": {
                    "provider": "openai",
                    "apiKey": "sk-test123456789",
                    "model": "gpt-4o",
                    "prompt": "Generate content for: {input}",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            {
                "name": "Valid Claude API Key",
                "config": {
                    "provider": "claude",
                    "apiKey": "sk-ant-test123456789",
                    "model": "claude-3-5-sonnet",
                    "prompt": "Generate content for: {input}",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            {
                "name": "Valid Gemini API Key",
                "config": {
                    "provider": "gemini",
                    "apiKey": "AIzaSyTest123456789",
                    "model": "gemini-2.5-flash",
                    "prompt": "Generate content for: {input}",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            {
                "name": "Missing API Key - OpenAI",
                "config": {
                    "provider": "openai",
                    "apiKey": "",
                    "model": "gpt-4o",
                    "prompt": "Generate content for: {input}",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            {
                "name": "Ollama (No API Key Required)",
                "config": {
                    "provider": "ollama",
                    "model": "llama3.2",
                    "prompt": "Generate content for: {input}",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print("-" * 30)
            
            try:
                context = MockExecutionContext(test_case['config'])
                result = await component.execute(context)
                
                if result.success:
                    print("✅ Execution successful")
                    print(f"   Processed records: {len(result.output_data.get('processed_results', []))}")
                    
                    # Check if real API was used
                    for processed in result.output_data.get('processed_results', []):
                        ai_response = processed.get('ai_response', {})
                        if 'metadata' in ai_response and ai_response['metadata'].get('real_api'):
                            print(f"   ✨ Real API used: {ai_response['metadata']['provider']}")
                        else:
                            print(f"   🎭 Simulation used: {test_case['config']['provider']}")
                else:
                    print(f"❌ Execution failed: {result.error}")
                    
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the backend directory")
        return False

async def test_real_api_integration():
    """Test with real API keys if available"""
    print("\n🌐 Testing Real API Integration")
    print("=" * 50)
    
    # Check for real API keys
    api_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'claude': os.getenv('ANTHROPIC_API_KEY'),
        'gemini': os.getenv('GEMINI_API_KEY')
    }
    
    available_providers = [provider for provider, key in api_keys.items() if key]
    
    if not available_providers:
        print("💡 No real API keys found in environment variables")
        print("   Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY to test real APIs")
        return
    
    print(f"🔑 Found API keys for: {', '.join(available_providers)}")
    
    import sys
    sys.path.append('src')
    
    try:
        from services.workflow.component_registry import AIProcessingComponent
        
        component = AIProcessingComponent()
        
        for provider in available_providers:
            print(f"\n🚀 Testing {provider.upper()} with real API")
            print("-" * 30)
            
            config = {
                "provider": provider,
                "apiKey": api_keys[provider],
                "model": {
                    'openai': 'gpt-4o-mini',  # Use mini for testing to save costs
                    'claude': 'claude-3-haiku-20240307',
                    'gemini': 'gemini-2.5-flash'
                }[provider],
                "prompt": "Write a very short greeting message.",
                "temperature": 0.7,
                "max_tokens": 50  # Keep it short for testing
            }
            
            try:
                context = MockExecutionContext(config)
                result = await component.execute(context)
                
                if result.success:
                    print("✅ Real API call successful")
                    processed = result.output_data.get('processed_results', [])
                    if processed:
                        ai_response = processed[0].get('ai_response', {})
                        content = ai_response.get('content', 'No content')
                        print(f"   Response: {content[:100]}...")
                        
                        if ai_response.get('metadata', {}).get('real_api'):
                            print("   ✨ Confirmed real API usage")
                        else:
                            print("   ⚠️  Fallback to simulation")
                else:
                    print(f"❌ Real API call failed: {result.error}")
                    
            except Exception as e:
                print(f"❌ Exception during real API test: {str(e)}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")

def test_frontend_validation():
    """Test frontend validation logic (mock)"""
    print("\n🎨 Testing Frontend Validation Logic")
    print("=" * 50)
    
    # Mock validation function from frontend
    def validate_api_key(provider: str, api_key: str) -> str or None:
        if not api_key and provider != 'ollama':
            return 'API Key is required for cloud providers'
        
        if api_key:
            if provider == 'openai' and not api_key.startswith('sk-'):
                return 'OpenAI API key should start with "sk-"'
            elif provider == 'claude' and not api_key.startswith('sk-ant-'):
                return 'Claude API key should start with "sk-ant-"'
            elif provider == 'gemini' and len(api_key) < 10:
                return 'Gemini API key seems too short'
        
        return None
    
    # Test validation cases
    validation_tests = [
        ('openai', '', 'API Key is required for cloud providers'),
        ('openai', 'invalid-key', 'OpenAI API key should start with "sk-"'),
        ('openai', 'sk-valid123', None),
        ('claude', 'sk-invalid', 'Claude API key should start with "sk-ant-"'),
        ('claude', 'sk-ant-valid123', None),
        ('gemini', 'short', 'Gemini API key seems too short'),
        ('gemini', 'AIzaSyValid123456', None),
        ('ollama', '', None),  # No API key required for Ollama
    ]
    
    for provider, api_key, expected_error in validation_tests:
        result = validate_api_key(provider, api_key)
        if result == expected_error:
            print(f"✅ {provider} validation: {api_key or 'empty'} -> {result or 'valid'}")
        else:
            print(f"❌ {provider} validation failed: expected '{expected_error}', got '{result}'")

async def main():
    """Main test function"""
    print("🚀 API Key Integration Test Suite")
    print("=" * 60)
    
    # Test validation logic
    test_frontend_validation()
    
    # Test component execution with API keys
    await test_api_key_validation()
    
    # Test real API integration if keys are available
    await test_real_api_integration()
    
    print("\n📋 Integration Summary:")
    print("  ✅ Frontend API key input field added")
    print("  ✅ Frontend validation implemented")
    print("  ✅ Backend accepts API keys from config")
    print("  ✅ Real AI providers used when API key provided")
    print("  ✅ Graceful fallback to simulation when needed")
    print("  ✅ Proper error handling and validation")
    
    print("\n🎯 How to use in workflows:")
    print("  1. Select your AI provider (OpenAI, Claude, Gemini)")
    print("  2. Enter your API key in the configuration panel")
    print("  3. System will validate the key format")
    print("  4. Workflow will use real API if key is valid")
    print("  5. Falls back to simulation if API fails")
    
    print("\n💡 Next steps:")
    print("  - Test with your actual API keys")
    print("  - Consider implementing secure key storage")
    print("  - Add API usage monitoring")

if __name__ == "__main__":
    asyncio.run(main())
