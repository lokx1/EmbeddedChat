#!/usr/bin/env python3
"""
Test complete workflow: Google Sheets -> AI Processing -> Google Drive CSV
"""
import json
import requests
import time

def test_sheets_ai_drive_workflow():
    print("=== Complete AI Workflow Test: Sheets -> AI -> Drive CSV ===")
    
    try:
        # Create workflow with Sheets -> AI -> Drive
        template_data = {
            'name': 'AI Processing to CSV Workflow',
            'description': 'Read Google Sheets, process with AI, save as CSV to Drive',
            'workflow_data': {
                'nodes': [
                    {
                        'id': 'trigger-1',
                        'type': 'manual_trigger',
                        'position': {'x': 100, 'y': 100},
                        'data': {'label': 'Start'}
                    },
                    {
                        'id': 'sheets-read-1',
                        'type': 'google_sheets',
                        'position': {'x': 300, 'y': 100},
                        'data': {
                            'label': 'Read Google Sheets',
                            'config': {
                                'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                                'sheet_name': 'Sheet1',
                                'range': 'A:Z'
                            }
                        }
                    },
                    {
                        'id': 'drive-write-1', 
                        'type': 'google_drive_write',
                        'position': {'x': 500, 'y': 100},
                        'data': {
                            'label': 'Save as CSV',
                            'config': {
                                'file_name': 'SheetsData_Export.csv',
                                'file_type': 'csv',  # Explicit CSV
                                'folder_id': '14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182',
                                'content_source': 'previous_output',
                                'include_timestamp': True
                            }
                        }
                    }
                ],
                'edges': [
                    {
                        'id': 'edge-1',
                        'source': 'trigger-1',
                        'target': 'sheets-read-1'
                    },
                    {
                        'id': 'edge-2',
                        'source': 'sheets-read-1',
                        'target': 'drive-write-1'
                    }
                ]
            }
        }
        
        # Create template
        template_response = requests.post(
            'http://localhost:8000/api/v1/workflow/templates',
            json=template_data
        )
        
        if template_response.status_code != 200:
            print(f"❌ Template creation failed: {template_response.text}")
            return False
            
        template_id = template_response.json()['template_id']
        print(f"✅ Template created: {template_id}")
        
        # Create instance
        instance_data = {
            'name': 'CSV Export Test Instance',
            'template_id': template_id,
            'workflow_data': template_data['workflow_data'],
            'input_data': {'export_format': 'csv', 'timestamp': time.strftime('%Y%m%d_%H%M%S')}
        }
        
        instance_response = requests.post(
            'http://localhost:8000/api/v1/workflow/instances',
            json=instance_data
        )
        
        if instance_response.status_code != 200:
            print(f"❌ Instance creation failed: {instance_response.text}")
            return False
            
        instance_id = instance_response.json()['instance_id']
        print(f"✅ Instance created: {instance_id}")
        
        # Execute workflow
        exec_response = requests.post(
            f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute',
            json={}
        )
        
        if exec_response.status_code != 200:
            print(f"❌ Execution failed: {exec_response.text}")
            return False
            
        print("✅ Workflow execution started")
        
        # Wait for completion and check status
        for i in range(10):  # Wait up to 50 seconds
            time.sleep(5)
            status_response = requests.get(
                f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/status'
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status', 'unknown')
                print(f"📊 Status check {i+1}: {current_status}")
                
                if current_status in ['completed', 'failed', 'error']:
                    break
            else:
                print(f"⚠️ Status check failed: {status_response.text}")
        
        # Get final results
        instance_response = requests.get(
            f'http://localhost:8000/api/v1/workflow/instances/{instance_id}'
        )
        
        if instance_response.status_code == 200:
            final_data = instance_response.json()
            
            print(f"\n📋 Final Status: {final_data.get('status', 'unknown')}")
            
            if 'output_data' in final_data and final_data['output_data']:
                output_data = final_data['output_data']
                print("📤 Final Output:")
                
                # Check Drive output specifically
                if 'node_outputs' in output_data and 'drive-write-1' in output_data['node_outputs']:
                    drive_output = output_data['node_outputs']['drive-write-1']
                    
                    print(f"📄 File uploaded: {drive_output.get('name', 'Unknown')}")
                    print(f"📊 File type: {drive_output.get('mime_type', 'Unknown')}")
                    print(f"📏 File size: {drive_output.get('size', 'Unknown')} bytes")
                    print(f"🔗 View link: {drive_output.get('web_view_link', 'N/A')}")
                    
                    if drive_output.get('mime_type') == 'text/csv':
                        print("🎉 SUCCESS: CSV file created successfully!")
                        return True
                    else:
                        print(f"⚠️ Unexpected file type: {drive_output.get('mime_type')}")
                else:
                    print("❌ No Drive output found")
                    print(json.dumps(output_data, indent=2))
            else:
                print("❌ No output data found")
        else:
            print(f"❌ Failed to get final results: {instance_response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_sheets_ai_drive_workflow()
    if success:
        print("\n🎉 Complete CSV workflow test PASSED!")
    else:
        print("\n❌ CSV workflow test FAILED!")
