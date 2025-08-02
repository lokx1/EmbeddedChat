#!/usr/bin/env python3
"""
Debug Current Workflow Execution Issue
"""

import requests
import json
import time
from datetime import datetime

def debug_current_workflow():
    """Debug the currently running workflow"""
    print("🔍 Debugging Current Workflow Execution")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    try:
        # Get all instances
        response = requests.get(f"{base_url}/instances")
        
        if response.status_code == 200:
            data = response.json()
            instances = data.get("data", {}).get("instances", [])
            
            print(f"📊 Total instances: {len(instances)}")
            
            # Find running instances
            running_instances = [inst for inst in instances if inst.get("status") == "running"]
            
            if running_instances:
                print(f"🔄 Found {len(running_instances)} running instances:")
                
                for i, instance in enumerate(running_instances):
                    instance_id = instance.get("id")
                    name = instance.get("name", "Unnamed")
                    
                    print(f"\n   {i+1}. {name}")
                    print(f"      ID: {instance_id}")
                    print(f"      Status: {instance.get('status')}")
                    print(f"      Started: {instance.get('started_at')}")
                    
                    # Get detailed info
                    detail_response = requests.get(f"{base_url}/instances/{instance_id}")
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        detail_instance = detail_data.get("data", {}).get("instance", {})
                        
                        # Check output data
                        output_data = detail_instance.get('output_data', {})
                        if output_data:
                            node_outputs = output_data.get('node_outputs', {})
                            executed_nodes = output_data.get('executed_nodes', [])
                            
                            print(f"      Executed nodes: {executed_nodes}")
                            print(f"      Node outputs available: {list(node_outputs.keys())}")
                            
                            # Check specific nodes
                            for node_id, node_output in node_outputs.items():
                                if 'sheets' in node_id.lower():
                                    print(f"      📊 {node_id}: {type(node_output)} - {str(node_output)[:100]}...")
                                elif 'ai' in node_id.lower():
                                    print(f"      🤖 {node_id}: {type(node_output)} - {str(node_output)[:100]}...")
                        else:
                            print(f"      ⚠️  No output data yet")
                        
                        # Check error
                        error_msg = detail_instance.get('error_message')
                        if error_msg:
                            print(f"      ❌ Error: {error_msg}")
                    else:
                        print(f"      ❌ Could not get details: {detail_response.status_code}")
            else:
                print(f"⚠️  No running instances found")
                
                # Show recent completed/failed instances
                recent_instances = instances[:5]
                print(f"\n📋 Recent instances:")
                for i, instance in enumerate(recent_instances):
                    print(f"   {i+1}. {instance.get('name', 'Unnamed')} - {instance.get('status')} ({instance.get('id', 'no-id')[:8]}...)")
        
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def check_google_sheets_write():
    """Check if GoogleSheetsWrite component is working"""
    print(f"\n📊 Checking Google Sheets Write Component")
    print("="*45)
    
    try:
        from src.services.google_sheets_service import GoogleSheetsService
        
        service = GoogleSheetsService()
        
        if service.authenticate():
            print("✅ Google Sheets authentication successful")
            
            # Check if Result_Test sheet exists and has data
            try:
                results = service.read_sheet(
                    "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "Result_Test!A1:M10"
                )
                
                if results:
                    print(f"✅ Result_Test sheet accessible")
                    print(f"   Rows found: {len(results)}")
                    if len(results) > 1:
                        print(f"   Latest data row: {results[1][:4]}...")
                else:
                    print(f"⚠️  Result_Test sheet empty or not found")
            
            except Exception as e:
                print(f"❌ Error reading Result_Test sheet: {str(e)}")
                
                # Try to create the sheet
                print(f"🛠️  Attempting to create Result_Test sheet...")
                success = service.create_sheet(
                    "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "Result_Test"
                )
                
                if success:
                    print(f"✅ Result_Test sheet created")
                else:
                    print(f"❌ Failed to create Result_Test sheet")
        else:
            print(f"❌ Google Sheets authentication failed")
    
    except Exception as e:
        print(f"❌ Google Sheets component error: {str(e)}")

def check_backend_components():
    """Check if backend components are registered correctly"""
    print(f"\n🔧 Checking Backend Components")
    print("="*35)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    components_to_check = [
        "manual_trigger",
        "google_sheets", 
        "ai_processing",
        "google_sheets_write"
    ]
    
    for component_type in components_to_check:
        try:
            response = requests.get(f"{base_url}/components/{component_type}")
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                params = len(data.get('parameters', []))
                print(f"✅ {component_type}: {params} parameters")
            else:
                print(f"❌ {component_type}: Failed ({response.status_code})")
        
        except Exception as e:
            print(f"❌ {component_type}: Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 Workflow Execution Debug Suite")
    print("="*40)
    
    # Check current workflow
    debug_current_workflow()
    
    # Check Google Sheets
    check_google_sheets_write()
    
    # Check backend components
    check_backend_components()
    
    print(f"\n🎯 Debug Complete!")
    print(f"💡 If workflow is stuck, it might be:")
    print(f"   1. Ollama timeout (qwen3:8b too slow)")
    print(f"   2. GoogleSheetsWrite component error")
    print(f"   3. Network/authentication issues")
    print(f"   4. Backend execution engine hanging")
