#!/usr/bin/env python3
"""
Debug AI to Sheets Data Flow
"""

import requests
import json
from datetime import datetime

def debug_data_flow():
    """Debug the data flow from AI to Sheets"""
    print("🔍 DEBUG: AI TO SHEETS DATA FLOW")
    print("="*45)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Simple workflow
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
                        "max_tokens": 200
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
                        "sheet_name": "Debug_Flow",
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
    
    # Input data
    input_data = {
        "sheets_data": {
            "records": [
                {
                    "Description": "Design a Task Manager app logo",
                    "Desired Output Format": "PNG",
                    "Model Specification": "OpenAI"
                }
            ]
        }
    }
    
    # Create and execute workflow
    save_payload = {
        "name": f"Debug Flow - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Debug data flow from AI to Sheets",
        "workflow_data": workflow_data,
        "category": "debug"
    }
    
    save_response = requests.post(f"{base_url}/workflow/editor/save", json=save_payload)
    
    if save_response.status_code == 200:
        template_data = save_response.json()
        template_id = template_data["data"]["workflow_id"]
        
        instance_payload = {
            "template_id": template_id,
            "name": f"Debug Instance - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": workflow_data,
            "input_data": input_data
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            
            if execute_response.status_code == 200:
                import time
                time.sleep(8)
                
                # Get detailed instance data
                status_response = requests.get(f"{base_url}/workflow/instances/{instance_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    instance = status_data["data"]["instance"]
                    
                    print(f"📊 Final Status: {instance['status']}")
                    
                    if instance.get('output_data'):
                        output = instance['output_data']
                        print(f"\n📤 Instance Output Keys: {list(output.keys())}")
                        
                        if 'node_outputs' in output:
                            node_outputs = output['node_outputs']
                            print(f"📊 Node Outputs: {list(node_outputs.keys())}")
                            
                            # Check AI processing output
                            if 'ai-1' in node_outputs:
                                ai_output = node_outputs['ai-1']
                                print(f"\n🤖 AI Processing Output:")
                                print(f"   Keys: {list(ai_output.keys())}")
                                
                                if 'results_for_sheets' in ai_output:
                                    results = ai_output['results_for_sheets']
                                    print(f"   ⭐ results_for_sheets: {type(results)}, length: {len(results)}")
                                    if results and len(results) > 0:
                                        print(f"   📝 Headers: {results[0]}")
                                        if "Prompt" in results[0]:
                                            print(f"   🎯 Prompt column found!")
                                        if len(results) > 1:
                                            print(f"   📝 Sample data: {results[1][:6]}...")
                                else:
                                    print(f"   ❌ No results_for_sheets found")
                                    
                            # Check Sheets write output
                            if 'sheets-write-1' in node_outputs:
                                sheets_output = node_outputs['sheets-write-1']
                                print(f"\n📊 Sheets Write Output:")
                                print(f"   Keys: {list(sheets_output.keys())}")
                                print(f"   Operation: {sheets_output.get('operation', 'N/A')}")
                                print(f"   Status: {sheets_output.get('status', 'N/A')}")
                                
                                if sheets_output.get('data_written'):
                                    data_written = sheets_output['data_written']
                                    print(f"   Rows written: {data_written.get('rows_count', 'N/A')}")
                                    print(f"   Columns: {data_written.get('columns_count', 'N/A')}")
                    
                    # Get logs for more details
                    logs_response = requests.get(f"{base_url}/workflow/instances/{instance_id}/logs")
                    if logs_response.status_code == 200:
                        logs_data = logs_response.json()
                        steps = logs_data.get("data", {}).get("steps", [])
                        
                        print(f"\n📋 Detailed Logs:")
                        for step in steps:
                            if step['step_type'] in ['ai_processing', 'google_sheets_write']:
                                print(f"\n🔹 {step['step_type'].upper()} - {step['status']}")
                                
                                if step.get('error_message'):
                                    print(f"   ❌ Error: {step['error_message']}")
                                    
                                if step.get('logs'):
                                    print(f"   📝 Logs:")
                                    for log in step['logs']:
                                        print(f"      - {log}")
                                        
                                if step.get('output_data'):
                                    output_data = step['output_data']
                                    print(f"   📊 Output keys: {list(output_data.keys())}")
                                    
                                    if step['step_type'] == 'ai_processing' and 'results_for_sheets' in output_data:
                                        results = output_data['results_for_sheets']
                                        print(f"   ⭐ AI generated results_for_sheets: {len(results)} rows")
                                        if results:
                                            headers = results[0]
                                            print(f"      Headers: {headers}")
                                            if "Prompt" in headers:
                                                print(f"      🎯 Prompt column at index: {headers.index('Prompt')}")

if __name__ == "__main__":
    debug_data_flow()
