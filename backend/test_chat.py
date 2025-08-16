import requests
import json

def test_chat():
    url = "http://localhost:8000/api/v1/chat/send"
    
    payload = {
        "provider": "openai",
        "model": "gpt-4o", 
        "apiKey": "test-key",
        "temperature": 0.7,
        "maxTokens": 2000,
        "systemPrompt": "You are a helpful AI assistant.",
        "message": "Hello",
        "conversationHistory": []
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()
