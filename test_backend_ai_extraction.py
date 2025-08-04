#!/usr/bin/env python3
"""
Quick test of the backend AI processing and sheets write workflow
"""
import requests
import time
import json

def test_backend_workflow():
    """Test the backend workflow with the fixed AI response extraction"""
    
    print("=== Testing Backend AI Processing -> Sheets Write ===")
    
    # Test configuration that matches your workflow
    template_data = {
        'name': 'AI Response Extraction Test',
        'description': 'Test AI response extraction to Prompt column',
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
                        'label': 'Read Input Data',
                        'config': {
                            'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                            'sheet_name': 'Trang tính1',  # Your sheet name
                            'range': 'A1:E10'
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
                            'model': 'gemma3:1b',
                            'prompt': 'Based on this asset request: {input}\n\nGenerate a comprehensive asset specification.',
                            'temperature': 0.3,
                            'max_tokens': 500
                        }
                    }
                },
                {
                    'id': 'sheets-write-1',
                    'type': 'google_sheets_write',
                    'position': {'x': 700, 'y': 100},
                    'data': {
                        'label': 'Write Results',
                        'config': {
                            'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                            'sheet_name': 'Test_Results',
                            'range': 'A1',
                            'mode': 'overwrite',
                            'data_format': 'auto'
                        }
                    }
                }
            ],
            'edges': [
                {'id': 'edge-1', 'source': 'trigger-1', 'target': 'sheets-read-1'},
                {'id': 'edge-2', 'source': 'sheets-read-1', 'target': 'ai-processing-1'},
                {'id': 'edge-3', 'source': 'ai-processing-1', 'target': 'sheets-write-1'}
            ]
        }
    }
    
    try:
        # Create template
        print("📝 Creating workflow template...")
        template_response = requests.post(
            'http://localhost:8000/api/v1/workflow/templates',
            json=template_data,
            timeout=30
        )
        
        if template_response.status_code != 200:
            print(f"❌ Template creation failed: {template_response.text}")
            return False
            
        template_id = template_response.json()['template_id']
        print(f"✅ Template created: {template_id}")
        
        # Create instance
        print("🚀 Creating workflow instance...")
        instance_data = {
            'name': 'AI Response Test Instance',
            'template_id': template_id,
            'workflow_data': template_data['workflow_data'],
            'input_data': {}
        }
        
        instance_response = requests.post(
            'http://localhost:8000/api/v1/workflow/instances',
            json=instance_data,
            timeout=30
        )
        
        if instance_response.status_code != 200:
            print(f"❌ Instance creation failed: {instance_response.text}")
            return False
            
        instance_id = instance_response.json()['instance_id']
        print(f"✅ Instance created: {instance_id}")
        
        # Execute workflow
        print("⚡ Executing workflow...")
        exec_response = requests.post(
            f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute',
            json={},
            timeout=30
        )
        
        if exec_response.status_code != 200:
            print(f"❌ Execution failed: {exec_response.text}")
            return False
            
        print("✅ Workflow execution started")
        print("⏳ Waiting for completion...")
        
        # Wait and check logs
        for i in range(20):  # Wait up to 100 seconds
            time.sleep(5)
            
            logs_response = requests.get(
                f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs',
                timeout=10
            )
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                steps = logs_data.get('data', {}).get('steps', [])
                
                # Check if all steps completed
                completed_steps = [s for s in steps if s.get('status') == 'completed']
                total_steps = len(steps)
                
                print(f"📊 Progress: {len(completed_steps)}/{total_steps} steps completed")
                
                # Look for sheets write step
                sheets_write_step = None
                for step in steps:
                    if step.get('step_type') == 'google_sheets_write':
                        sheets_write_step = step
                        break
                
                if sheets_write_step and sheets_write_step.get('status') == 'completed':
                    print("🎉 Workflow completed successfully!")
                    
                    # Check the output data
                    output_data = sheets_write_step.get('output_data', {})
                    print(f"📊 Sheets write result: {output_data}")
                    
                    # Check for AI processing step logs
                    ai_step = None
                    for step in steps:
                        if step.get('step_type') == 'ai_processing':
                            ai_step = step
                            break
                    
                    if ai_step:
                        print("🤖 AI Processing step found:")
                        print(f"   Status: {ai_step.get('status')}")
                        output = ai_step.get('output_data', {})
                        if 'processed_results' in output:
                            results = output['processed_results']
                            print(f"   Processed {len(results)} results")
                            
                            # Check if AI responses have content
                            for idx, result in enumerate(results[:2]):  # Check first 2
                                ai_response = result.get('ai_response', {})
                                if 'ai_response' in ai_response:
                                    ai_text = ai_response['ai_response']
                                    print(f"   Row {idx+1}: AI response length = {len(ai_text)}")
                                    print(f"   Row {idx+1}: Preview = {ai_text[:100]}...")
                    
                    return True
                
                # Check for errors
                error_steps = [s for s in steps if s.get('status') == 'error']
                if error_steps:
                    print(f"❌ Found {len(error_steps)} error steps:")
                    for step in error_steps:
                        print(f"   {step.get('step_type')}: {step.get('error')}")
                    return False
            
            print(f"⏳ Waiting... check {i+1}/20")
        
        print("⏰ Timeout waiting for completion")
        return False
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    result = test_backend_workflow()
    if result:
        print("\n🎉 SUCCESS: AI response extraction test completed successfully!")
    else:
        print("\n❌ FAILED: AI response extraction test failed!")
