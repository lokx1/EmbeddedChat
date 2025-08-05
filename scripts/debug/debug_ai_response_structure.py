#!/usr/bin/env python3
"""
Debug AI response structure to understand field mapping issues
"""

import asyncio
import json
import requests
import time

async def debug_ai_response_structure():
    print("🔍 Debugging AI response structure vs extraction logic...")
    
    # First, let's create a minimal workflow to test AI response structure
    test_config = {
        "name": "Debug AI Response Structure",
        "description": "Test to understand AI response fields",
        "version": "1.0",
        "components": [
            {
                "id": "sheets_read",
                "type": "google_sheets",
                "name": "Read Sheet",
                "config": {
                    "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "sheet_name": "HEYDO",
                    "range": "A1:Z100",
                    "mode": "read"
                },
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "ai_processing", 
                "type": "ai_processing",
                "name": "AI Processing",
                "config": {
                    "provider": "ollama",
                    "model": "llama3.2",
                    "prompt": "Tạo một câu chuyện ngắn về {input}. Hãy viết một đoạn văn từ 100-200 từ.",
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                "position": {"x": 300, "y": 100}
            }
        ],
        "connections": [
            {
                "source": "sheets_read",
                "sourceHandle": "output", 
                "target": "ai_processing",
                "targetHandle": "input"
            }
        ]
    }
    
    print("📤 Sending workflow execution request...")
    
    try:
        # Execute workflow via API
        response = requests.post(
            "http://localhost:8001/api/v1/workflows/execute",
            json={
                "name": "Debug AI Response Structure",
                "description": "Debug test",
                "config": test_config
            },
            timeout=120
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow executed successfully!")
            
            # Find AI processing step result
            for step in result.get("step_results", []):
                if "AI Processing" in step.get("step_name", ""):
                    print(f"\n🤖 AI Processing Step Results:")
                    output_data = step.get("output_data", {})
                    
                    # Check processed_results structure
                    processed_results = output_data.get("processed_results", [])
                    print(f"📊 Found {len(processed_results)} processed results")
                    
                    if processed_results:
                        first_result = processed_results[0]
                        print(f"\n🔍 First result structure:")
                        print(f"   Keys: {list(first_result.keys())}")
                        
                        # Check input_data
                        input_data = first_result.get("input_data", {})
                        print(f"\n📥 input_data structure:")
                        print(f"   Keys: {list(input_data.keys())}")
                        print(f"   Content: {input_data}")
                        
                        # Check ai_response structure  
                        ai_response = first_result.get("ai_response", {})
                        print(f"\n🤖 ai_response structure:")
                        print(f"   Type: {type(ai_response)}")
                        print(f"   Keys: {list(ai_response.keys()) if isinstance(ai_response, dict) else 'Not a dict'}")
                        
                        if isinstance(ai_response, dict):
                            for key, value in ai_response.items():
                                if isinstance(value, str):
                                    print(f"   {key}: {type(value)} - '{value[:100]}...' (length: {len(value)})")
                                else:
                                    print(f"   {key}: {type(value)} - {value}")
                        
                        # Check if results_for_sheets exists and its structure
                        results_for_sheets = output_data.get("results_for_sheets", [])
                        print(f"\n📊 results_for_sheets structure:")
                        print(f"   Type: {type(results_for_sheets)}")
                        print(f"   Length: {len(results_for_sheets) if isinstance(results_for_sheets, list) else 'Not a list'}")
                        
                        if isinstance(results_for_sheets, list) and len(results_for_sheets) > 0:
                            headers = results_for_sheets[0] if len(results_for_sheets) > 0 else []
                            print(f"   Headers: {headers}")
                            
                            if "Prompt" in headers:
                                prompt_index = headers.index("Prompt")
                                print(f"   ✅ Prompt column found at index: {prompt_index}")
                                
                                if len(results_for_sheets) > 1:
                                    first_row = results_for_sheets[1]
                                    if len(first_row) > prompt_index:
                                        prompt_content = first_row[prompt_index]
                                        print(f"   📝 Prompt content: '{prompt_content[:100]}...' (length: {len(prompt_content)})")
                                        
                                        if prompt_content and len(prompt_content) > 10:
                                            print(f"   ✅ SUCCESS: Prompt column has substantial content!")
                                        else:
                                            print(f"   ❌ ISSUE: Prompt column is empty or too short")
                                            print(f"   🔍 Let's check the extraction logic...")
                                            
                                            # Simulate the extraction logic
                                            print(f"\n🔧 Simulating extraction logic:")
                                            print(f"   Looking for 'ai_response' key in ai_response dict...")
                                            if "ai_response" in ai_response:
                                                nested_response = ai_response["ai_response"]
                                                print(f"   Found nested ai_response: {type(nested_response)}")
                                                if isinstance(nested_response, str):
                                                    print(f"   ✅ Found string: '{nested_response[:100]}...'")
                                                else:
                                                    print(f"   ❌ Not a string: {nested_response}")
                                            else:
                                                print(f"   ❌ No 'ai_response' key found")
                                                print(f"   🔍 Trying fallback keys...")
                                                for key in ["generated_text", "response", "content", "text"]:
                                                    if key in ai_response:
                                                        value = ai_response[key]
                                                        print(f"   Found {key}: {type(value)} - '{str(value)[:100]}...'")
                            else:
                                print(f"   ❌ No Prompt column found in headers!")
                        else:
                            print(f"   ❌ results_for_sheets is empty or not a list")
                    
                    break
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ai_response_structure())
