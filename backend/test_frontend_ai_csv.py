#!/usr/bin/env python3
"""
Test full workflow: Sheets -> AI -> Drive CSV (simulating frontend)
"""
import requests
import json
import time

def test_frontend_workflow():
    print("=== Frontend-like Workflow Test: Sheets -> AI -> CSV ===")
    
    # Template exactly like what frontend would send
    template_data = {
        'name': 'AI to CSV Frontend Test',
        'description': 'Test AI processing output converted to CSV',
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
                            'sheet_name': 'TEST121',  # Sheet with real AI data
                            'range': 'A1:F100'
                        }
                    }
                },
                {
                    'id': 'ai-processing-1',
                    'type': 'ai_processing',
                    'position': {'x': 500, 'y': 100},
                    'data': {
                        'label': 'AI Asset Generation',
                        'config': {
                            'provider': 'ollama',
                            'model': 'qwen3:8b',
                            'prompt': 'Generate asset based on: {input}',
                            'temperature': 0.3,
                            'max_tokens': 300
                        }
                    }
                },
                {
                    'id': 'drive-write-1', 
                    'type': 'google_drive_write',
                    'position': {'x': 700, 'y': 100},
                    'data': {
                        'label': 'Save as CSV',
                        'config': {
                            'file_name': 'AI_ProcessingResults.csv',  # CSV file
                            'file_type': 'auto',  # Auto-detect -> should become CSV
                            'folder_id': '14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182',
                            'content_source': 'previous_output'
                        }
                    }
                }
            ],
            'edges': [
                {'id': 'edge-1', 'source': 'trigger-1', 'target': 'sheets-read-1'},
                {'id': 'edge-2', 'source': 'sheets-read-1', 'target': 'ai-processing-1'},
                {'id': 'edge-3', 'source': 'ai-processing-1', 'target': 'drive-write-1'}
            ]
        }
    }
    
    try:
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
            'name': 'AI CSV Export Test',
            'template_id': template_id,
            'workflow_data': template_data['workflow_data'],
            'input_data': {'export_format': 'csv'}
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
        print("⏳ Waiting for AI processing to complete...")
        
        # Wait for completion (AI processing takes time)
        for i in range(24):  # Wait up to 2 minutes
            time.sleep(5)
            
            # Check via logs
            logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs')
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                steps = logs_data.get('data', {}).get('steps', [])
                
                # Find drive-write step
                drive_step = None
                for step in steps:
                    if step.get('step_type') == 'google_drive_write':
                        drive_step = step
                        break
                
                if drive_step and drive_step.get('status') == 'completed':
                    output_data = drive_step.get('output_data', {})
                    file_name = output_data.get('name', 'N/A')
                    mime_type = output_data.get('mime_type', 'N/A')
                    file_size = output_data.get('size', 'N/A')
                    
                    print(f"\n🎉 Workflow completed!")
                    print(f"📄 File: {file_name}")
                    print(f"📊 MIME: {mime_type}")
                    print(f"📏 Size: {file_size} bytes")
                    print(f"🔗 Link: {output_data.get('web_view_link', 'N/A')}")
                    
                    if 'csv' in mime_type.lower():
                        print("✅ SUCCESS: AI processing data converted to CSV!")
                        return True
                    else:
                        print(f"⚠️ Unexpected MIME type: {mime_type}")
                        return False
                        
            print(f"📊 Status check {i+1}/24...")
            
        print("⏰ Timeout waiting for completion")
        return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_workflow()
    if success:
        print("\n🎉 Frontend-like AI -> CSV workflow test PASSED!")
    else:
        print("\n❌ Frontend-like AI -> CSV workflow test FAILED!")
