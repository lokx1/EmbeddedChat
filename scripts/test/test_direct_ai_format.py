#!/usr/bin/env python3
"""
Test Direct AI Response Format
"""

import requests
import json
from datetime import datetime

def test_direct_ai_format():
    """Test AI processing with manual input data"""
    print("🧪 TESTING DIRECT AI PROCESSING FORMAT")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Simple workflow: Manual Trigger -> AI Processing -> Google Sheets Write
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger", 
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Manual Input",
                    "type": "manual_trigger",
                    "config": {}
                }
            },
            {
                "id": "ai-1",
                "type": "ai_processing",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "AI Processing",
                    "type": "ai_processing", 
                    "config": {
                        "provider": "ollama",
                        "model": "qwen2.5:3b",
                        "prompt_template": "Generate specification for: {input}",
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                }
            },
            {
                "id": "sheets-write-1", 
                "type": "google_sheets_write",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Write to Sheets",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": "Direct_AI_Test",
                        "range": "A1", 
                        "mode": "overwrite",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "ai-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2",
                "source": "ai-1", 
                "target": "sheets-write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Manual input data that mimics Google Sheets data
    input_data = {
        "sheets_data": {
            "records": [
                {
                    "Description": "Design a Task Manager app logo",
                    "Example Asset URL": "https://example.com/logo.png",
                    "Desired Output Format": "PNG",
                    "Model Specification": "OpenAI"
                },
                {
                    "Description": "Summer Sale promotional banner",
                    "Example Asset URL": "https://example.com/banner.jpg", 
                    "Desired Output Format": "JPG",
                    "Model Specification": "Claude"
                }
            ]
        }
    }
    
    print("1️⃣ Creating workflow template...")
    save_payload = {
        "name": f"Direct AI Test - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test direct AI processing format",
        "workflow_data": workflow_data,
        "category": "test"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        print(f"   ✅ Template: {template_id}")
        
        print("\n2️⃣ Creating instance...")
        instance_payload = {
            "template_id": template_id,
            "name": f"Direct AI Instance - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": input_data
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            print(f"   ✅ Instance: {instance_id}")
            
            print("\n3️⃣ Executing...")
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                print("   ✅ Execution started")
                
                import time
                time.sleep(10)  # Wait for AI processing
                
                print("\n4️⃣ Checking results...")
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"   📊 Status: {instance['status']}")
                    
                    # Get detailed logs
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        print(f"\n   📋 Execution Steps:")
                        for step in steps:
                            print(f"      [{step['step_type']}] {step['status']}")
                            
                            if step['step_type'] == 'ai_processing':
                                if step['status'] == 'success' and step.get('output_data'):
                                    output = step['output_data'] 
                                    print(f"         📊 AI Output keys: {list(output.keys())}")
                                    
                                    if 'results_for_sheets' in output:
                                        results = output['results_for_sheets']
                                        print(f"         ⭐ results_for_sheets: {len(results)} rows")
                                        if results:
                                            headers = results[0]
                                            print(f"         📝 Headers: {headers}")
                                            if "Prompt" in headers:
                                                prompt_idx = headers.index("Prompt")
                                                print(f"         🎯 Prompt column at index {prompt_idx}")
                                                if len(results) > 1:
                                                    sample_prompt = results[1][prompt_idx]
                                                    print(f"         📝 Sample prompt: {sample_prompt[:100]}...")
                                            else:
                                                print(f"         ❌ No Prompt column in headers!")
                                    else:
                                        print(f"         ❌ No results_for_sheets in AI output!")
                                        
                                elif step.get('error_message'):
                                    print(f"         ❌ AI Error: {step['error_message']}")
                                    
                            elif step['step_type'] == 'google_sheets_write':
                                if step['status'] == 'success':
                                    if step.get('output_data'):
                                        write_output = step['output_data']
                                        print(f"         ✅ Write success: {write_output.get('operation', 'N/A')}")
                                        print(f"         📊 Rows written: {write_output.get('data_written', {}).get('rows_count', 'N/A')}")
                                elif step.get('error_message'):
                                    print(f"         ❌ Write Error: {step['error_message']}")
                                    
                                # Show write logs for debugging
                                if step.get('logs'):
                                    for log in step['logs'][-3:]:
                                        print(f"         📝 {log}")
                    
                    return instance['status'] == 'completed'
    
    return False

if __name__ == "__main__":
    success = test_direct_ai_format()
    
    if success:
        print(f"\n🎉 SUCCESS!")
        print(f"📊 Check Google Sheets tab: Direct_AI_Test")
        print(f"⭐ Look for Prompt column with AI responses")
    else:
        print(f"\n❌ FAILED - Check logs above")
