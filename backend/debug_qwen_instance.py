#!/usr/bin/env python3
"""
Debug Workflow Instance Details
"""

import requests
import json

def debug_workflow_instance():
    """Debug the latest Qwen workflow instance"""
    print("🔍 Debugging Workflow Instance")
    print("="*35)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    try:
        # Get all instances
        response = requests.get(f"{base_url}/instances")
        
        if response.status_code == 200:
            data = response.json()
            instances = data.get("data", {}).get("instances", [])
            
            # Find latest Qwen instance
            qwen_instances = [
                inst for inst in instances 
                if "qwen" in inst.get("name", "").lower()
            ]
            
            if qwen_instances:
                latest = qwen_instances[0]
                instance_id = latest.get("id")
                
                print(f"🎯 Latest Qwen Instance: {latest.get('name')}")
                print(f"   ID: {instance_id}")
                print(f"   Status: {latest.get('status')}")
                print(f"   Created: {latest.get('created_at')}")
                
                # Get detailed instance info
                detail_response = requests.get(f"{base_url}/instances/{instance_id}")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    instance = detail_data.get("data", {}).get("instance", {})
                    
                    print(f"\n📊 Detailed Information:")
                    print(f"   Status: {instance.get('status')}")
                    print(f"   Started: {instance.get('started_at')}")
                    print(f"   Completed: {instance.get('completed_at')}")
                    
                    # Check for errors
                    if instance.get('error_message'):
                        print(f"\n❌ Error Message:")
                        print(f"   {instance.get('error_message')}")
                    
                    # Check output data
                    output_data = instance.get('output_data')
                    if output_data:
                        print(f"\n📤 Output Data Found:")
                        print(f"   Keys: {list(output_data.keys())}")
                        
                        # Check node_outputs
                        if 'node_outputs' in output_data:
                            node_outputs = output_data['node_outputs']
                            print(f"\n🔗 Node Outputs:")
                            print(f"   Nodes executed: {list(node_outputs.keys())}")
                            
                            # Check AI processing node
                            ai_node_key = None
                            for key in node_outputs.keys():
                                if 'ai-processing' in key or 'ai_processing' in key:
                                    ai_node_key = key
                                    break
                            
                            if ai_node_key:
                                ai_output = node_outputs[ai_node_key]
                                print(f"\n🤖 AI Processing Node Output:")
                                print(f"   Success: {ai_output.get('success')}")
                                print(f"   Error: {ai_output.get('error')}")
                                
                                ai_output_data = ai_output.get('output_data', {})
                                if ai_output_data:
                                    print(f"   Output Keys: {list(ai_output_data.keys())}")
                                    
                                    if 'processed_results' in ai_output_data:
                                        results = ai_output_data['processed_results']
                                        print(f"   Processed Results: {len(results)} items")
                                        
                                        for i, result in enumerate(results[:2]):
                                            print(f"\n   Result {i+1}:")
                                            print(f"     Status: {result.get('status')}")
                                            print(f"     Provider: {result.get('provider')}")
                                            print(f"     Model: {result.get('model')}")
                                            
                                            if result.get('ai_response'):
                                                ai_resp = result['ai_response']
                                                if isinstance(ai_resp, dict):
                                                    print(f"     AI Type: {ai_resp.get('type', 'unknown')}")
                                                    print(f"     AI Provider: {ai_resp.get('metadata', {}).get('provider', 'unknown')}")
                                                    print(f"     Model Used: {ai_resp.get('metadata', {}).get('model', 'unknown')}")
                                                    
                                                    # Check for real Ollama vs simulation
                                                    ai_content = ai_resp.get('ai_response', '')
                                                    if ai_content:
                                                        print(f"     Content Length: {len(str(ai_content))} chars")
                                                        print(f"     Content Preview: {str(ai_content)[:150]}...")
                                                        
                                                        # Determine if real Ollama
                                                        if ai_resp.get('metadata', {}).get('provider') == 'ollama' and len(str(ai_content)) > 100:
                                                            print(f"     🎯 REAL OLLAMA RESPONSE DETECTED!")
                                                        elif 'simulation' in str(ai_content).lower():
                                                            print(f"     🎭 Simulation response")
                                                        else:
                                                            print(f"     ❓ Response type unclear")
                                                else:
                                                    print(f"     AI Response: {str(ai_resp)[:100]}...")
                                            
                                            if result.get('error'):
                                                print(f"     Error: {result['error']}")
                            
                            # Check GoogleSheetsWrite node
                            sheets_write_key = None
                            for key in node_outputs.keys():
                                if 'sheets-write' in key or 'google_sheets_write' in key:
                                    sheets_write_key = key
                                    break
                            
                            if sheets_write_key:
                                sheets_output = node_outputs[sheets_write_key]
                                print(f"\n📊 Google Sheets Write Node Output:")
                                print(f"   Success: {sheets_output.get('success')}")
                                print(f"   Error: {sheets_output.get('error')}")
                                
                                sheets_output_data = sheets_output.get('output_data', {})
                                if sheets_output_data:
                                    print(f"   Sheet Output Keys: {list(sheets_output_data.keys())}")
                                    print(f"   Rows Written: {sheets_output_data.get('rows_written', 'unknown')}")
                                    print(f"   Sheet URL: {sheets_output_data.get('sheet_url', 'none')}")
                        
                        # Check for processed results at top level
                        if 'processed_results' in output_data:
                            results = output_data['processed_results']
                            print(f"   Processed Results: {len(results)} items")
                            
                            for i, result in enumerate(results[:3]):
                                print(f"\n   Result {i+1}:")
                                print(f"     Status: {result.get('status')}")
                                print(f"     Provider: {result.get('provider')}")
                                print(f"     Model: {result.get('model')}")
                                
                                if result.get('ai_response'):
                                    ai_resp = result['ai_response']
                                    if isinstance(ai_resp, dict):
                                        print(f"     AI Response Type: {ai_resp.get('type', 'unknown')}")
                                        print(f"     AI Provider: {ai_resp.get('metadata', {}).get('provider', 'unknown')}")
                                        print(f"     AI Content: {str(ai_resp.get('ai_response', ''))[:100]}...")
                                    else:
                                        print(f"     AI Response: {str(ai_resp)[:100]}...")
                                
                                if result.get('error'):
                                    print(f"     Error: {result['error']}")
                    
                    # Check input data
                    input_data = instance.get('input_data')
                    if input_data:
                        print(f"\n📥 Input Data:")
                        print(f"   Keys: {list(input_data.keys())}")
                    
                else:
                    print(f"❌ Could not get instance details: {detail_response.status_code}")
            else:
                print(f"❌ No Qwen instances found")
        else:
            print(f"❌ Could not get instances: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_workflow_instance()
