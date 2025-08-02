#!/usr/bin/env python3
"""
Check frontend workflow execution
"""
import requests
import json

print("=== Checking Frontend Workflow Execution ===")

try:
    # Get workflow instances
    instances_response = requests.get('http://localhost:8000/api/v1/workflow/instances')
    print(f"Instances API status: {instances_response.status_code}")
    
    if instances_response.status_code == 200:
        instances_data = instances_response.json()
        
        # Handle different response formats
        if isinstance(instances_data, dict) and 'data' in instances_data:
            instances = instances_data['data']
        elif isinstance(instances_data, list):
            instances = instances_data
        else:
            instances = [instances_data] if instances_data else []
            
        print(f"Total instances found: {len(instances)}")
        
        if instances:
            # Show latest instances
            latest_instances = instances[-3:] if len(instances) >= 3 else instances
            
            for i, inst in enumerate(latest_instances, 1):
                name = inst.get('name', 'Unnamed')
                inst_id = inst.get('id', 'No ID')
                status = inst.get('status', 'Unknown')
                created = inst.get('created_at', 'No date')
                
                print(f"\n{i}. Workflow: {name}")
                print(f"   ID: {inst_id}")
                print(f"   Status: {status}")
                print(f"   Created: {created}")
                
                # Check if it has output data
                if inst.get('output_data'):
                    output_data = inst['output_data']
                    print(f"   Output nodes: {list(output_data.keys())}")
                    
                    # Look for Google Sheets Write output
                    for node_id, node_output in output_data.items():
                        if isinstance(node_output, dict):
                            node_status = node_output.get('status', 'unknown')
                            operation = node_output.get('operation', 'unknown')
                            
                            if 'sheets' in node_id.lower() or 'write' in node_id.lower():
                                print(f"   📝 {node_id}: {node_status} ({operation})")
                                
                                if node_status == 'success':
                                    data_written = node_output.get('data_written', {})
                                    print(f"      ✅ Data written: {data_written}")
                                elif node_status == 'simulated':
                                    print(f"      ⚠️  SIMULATED (API failed)")
                else:
                    print("   ❌ No output data")
                    
                # Check if still running and needs execution
                if status in ['draft', 'created']:
                    print(f"   ⏳ Status '{status}' - workflow not executed yet")
                elif status == 'running':
                    print(f"   🔄 Currently running...")
                elif status == 'completed':
                    print(f"   ✅ Completed")
                elif status == 'failed':
                    error = inst.get('error_message', 'Unknown error')
                    print(f"   ❌ Failed: {error}")
        else:
            print("No workflow instances found")
            
        # Also check Google Sheets directly
        print(f"\n=== Direct Google Sheets Check ===")
        
        # Import and check sheets
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.services.google_sheets_service import get_sheets_service
        
        sheets_service = get_sheets_service()
        if sheets_service.authenticate():
            # Check both sheet names
            sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
            
            # Try Test sheet (from frontend config)
            try:
                test_data = sheets_service.read_sheet(sheet_id, "Test!A1:D10")
                print(f"📊 'Test' sheet rows: {len(test_data) if test_data else 0}")
                if test_data:
                    print(f"   First few rows: {test_data[:3]}")
            except Exception as e:
                print(f"❌ 'Test' sheet error: {e}")
                
            # Try Result_Test sheet (from backend config)
            try:
                result_data = sheets_service.read_sheet(sheet_id, "Result_Test!A1:D10")
                print(f"📊 'Result_Test' sheet rows: {len(result_data) if result_data else 0}")
                if result_data:
                    print(f"   First few rows: {result_data[:3]}")
            except Exception as e:
                print(f"❌ 'Result_Test' sheet error: {e}")
        else:
            print("❌ Google Sheets authentication failed")
            
    else:
        print(f"❌ Failed to get instances: {instances_response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
