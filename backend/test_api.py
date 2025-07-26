#!/usr/bin/env python3
"""
Simple test script for the chat API endpoints
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_endpoints():
    """Test various chat API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Chat API Endpoints...")
        
        # Test health endpoint
        try:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            print(f"✅ Health check: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test get providers
        try:
            response = await client.get(f"{BASE_URL}/api/v1/chat/providers")
            if response.status_code == 200:
                providers = response.json()
                print(f"✅ Get providers: {len(providers)} providers found")
                for provider in providers:
                    print(f"   - {provider['display_name']} ({provider['name']}): {'✅' if provider['is_enabled'] else '❌'}")
            else:
                print(f"❌ Get providers failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Get providers error: {e}")
        
        # Test get models
        try:
            response = await client.get(f"{BASE_URL}/api/v1/chat/models")
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Get models: {len(models)} models found")
            else:
                print(f"❌ Get models failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Get models error: {e}")
        
        # Test check provider availability (Ollama)
        try:
            response = await client.post(f"{BASE_URL}/api/v1/chat/providers/ollama/check")
            print(f"✅ Check Ollama: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Check Ollama error: {e}")
        
        # Test create conversation
        try:
            conversation_data = {
                "title": "Test Conversation",
                "description": "Testing the chat API",
                "ai_provider_name": "ollama",
                "model_name": "llama2",
                "system_prompt": "You are a helpful assistant.",
                "user_id": 1  # Assuming user exists
            }
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/conversations",
                json=conversation_data
            )
            if response.status_code == 201:
                conversation = response.json()
                conversation_id = conversation["id"]
                print(f"✅ Create conversation: ID {conversation_id}")
                
                # Test send message
                message_data = {
                    "content": "Hello, how are you?",
                    "conversation_id": conversation_id,
                    "user_id": 1
                }
                response = await client.post(
                    f"{BASE_URL}/api/v1/chat/messages",
                    json=message_data
                )
                if response.status_code == 201:
                    message = response.json()
                    print(f"✅ Send message: ID {message['id']}")
                else:
                    print(f"❌ Send message failed: {response.status_code}")
                
            else:
                print(f"❌ Create conversation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Conversation test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
