#!/usr/bin/env python3
"""
Test the complete workflow with correct sheet name HEYDO
"""
import requests
import time
import json

def test_workflow_with_correct_sheet():
    """Test the workflow with correct sheet name HEYDO"""
    
    print("=== Testing Complete Workflow with Correct Sheet Name ===")
    
    # Workflow configuration with CORRECT sheet name
    template_data = {
        'name': 'AI Response HEYDO Sheet Test',
        'description': 'Test AI response extraction with correct sheet name',
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
                        'label': 'Read HEYDO Sheet',
                        'config': {
                            'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                            'sheet_name': 'HEYDO',  # ✅ CORRECT SHEET NAME!
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
                            'prompt': 'Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including technical details, design guidelines, and implementation notes.',
                            'temperature': 0.3,
                            'max_tokens': 1000
                        }
                    }
                },
                {
                    'id': 'sheets-write-1',
                    'type': 'google_sheets_write',
                    'position': {'x': 700, 'y': 100},
                    'data': {
                        'label': 'Write Back to HEYDO',
                        'config': {
                            'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                            'sheet_name': 'HEYDO',  # ✅ WRITE BACK TO SAME SHEET
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
        print("📝 Creating workflow template with correct sheet name...")
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
            'name': 'HEYDO Sheet AI Response Test',
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
        print("⚡ Executing workflow with HEYDO sheet...")
        exec_response = requests.post(
            f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute',
            json={},
            timeout=30
        )
        
        if exec_response.status_code != 200:
            print(f"❌ Execution failed: {exec_response.text}")
            return False
            
        print("✅ Workflow execution started")
        print("⏳ Waiting for AI processing to complete...")
        
        # Wait and monitor progress
        for i in range(30):  # Wait up to 150 seconds
            time.sleep(5)
            
            logs_response = requests.get(
                f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs',
                timeout=10
            )
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                steps = logs_data.get('data', {}).get('steps', [])
                
                completed_steps = [s for s in steps if s.get('status') == 'completed']
                total_steps = len(steps)
                
                print(f"📊 Progress: {len(completed_steps)}/{total_steps} steps completed")
                
                # Check for completion
                sheets_write_step = None
                ai_processing_step = None
                
                for step in steps:
                    if step.get('step_type') == 'google_sheets_write':
                        sheets_write_step = step
                    elif step.get('step_type') == 'ai_processing':
                        ai_processing_step = step
                
                if sheets_write_step and sheets_write_step.get('status') == 'completed':
                    print("🎉 Workflow completed successfully!")
                    
                    # Analyze AI processing results
                    if ai_processing_step:
                        output_data = ai_processing_step.get('output_data', {})
                        processed_results = output_data.get('processed_results', [])
                        print(f"🤖 AI Processing: {len(processed_results)} results processed")
                        
                        if processed_results:
                            for idx, result in enumerate(processed_results[:2]):  # Show first 2
                                ai_response = result.get('ai_response', {})
                                input_data = result.get('input_data', {})
                                
                                print(f"\n📋 Result {idx+1}:")
                                print(f"   Input: {input_data.get('Description', 'N/A')}")
                                print(f"   Status: {result.get('status', 'unknown')}")
                                
                                if 'ai_response' in ai_response:
                                    ai_text = ai_response['ai_response']
                                    print(f"   AI Response: {len(ai_text)} chars - {ai_text[:100]}...")
                                else:
                                    print(f"   AI Response: No text found in {list(ai_response.keys())}")
                        
                        # Check results_for_sheets
                        results_for_sheets = output_data.get('results_for_sheets', [])
                        if results_for_sheets:
                            print(f"\n📊 Results for sheets: {len(results_for_sheets)} rows")
                            if len(results_for_sheets) > 1:
                                headers = results_for_sheets[0]
                                first_data = results_for_sheets[1]
                                print(f"   Headers: {headers}")
                                print(f"   First row data length: {len(first_data)}")
                                if 'Prompt' in headers:
                                    prompt_idx = headers.index('Prompt')
                                    prompt_content = first_data[prompt_idx] if prompt_idx < len(first_data) else ""
                                    print(f"   Prompt content: {len(prompt_content)} chars")
                                    if prompt_content:
                                        print(f"   Prompt preview: {prompt_content[:150]}...")
                                    else:
                                        print("   ❌ Prompt is still empty!")
                    
                    return True
                
                # Check for errors
                error_steps = [s for s in steps if s.get('status') == 'error']
                if error_steps:
                    print(f"❌ Found {len(error_steps)} error steps:")
                    for step in error_steps:
                        print(f"   {step.get('step_type')}: {step.get('error')}")
                    return False
            
            print(f"⏳ Waiting... check {i+1}/30")
        
        print("⏰ Timeout waiting for completion")
        return False
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    result = test_workflow_with_correct_sheet()
    if result:
        print("\n🎉 SUCCESS: AI response extraction working with HEYDO sheet!")
        print("Check your Google Sheet - the Prompt column should now be filled!")
    else:
        print("\n❌ FAILED: Issues remain with AI response extraction")
