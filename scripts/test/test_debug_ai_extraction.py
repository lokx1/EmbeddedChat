#!/usr/bin/env python3
"""
Test with the actual sheet data to debug the AI response extraction issue
"""
import requests
import time
import json

def test_with_correct_range():
    """Test reading the actual data range that has content"""
    
    print("=== Testing with Correct Data Range ===")
    
    # Updated template to read the correct range where data exists
    template_data = {
        'name': 'AI Response Debug Test',
        'description': 'Debug AI response extraction with correct range',
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
                            'sheet_name': 'Trang tính1',
                            'range': 'A3:E6'  # Read the actual data rows (3-6)
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
                            'prompt': 'Based on this asset request: {input}\n\nGenerate a comprehensive creative brief for: {Description}\nOutput format: {Desired Output Format}\nProvide detailed technical specifications, design guidelines, and implementation notes.',
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
                        'label': 'Write AI Results',
                        'config': {
                            'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                            'sheet_name': 'AI_Results_Debug',  # Write to a new sheet
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
        print("📝 Creating debug workflow template...")
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
            'name': 'AI Response Debug Instance',
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
        print("⏳ Monitoring execution...")
        
        # Monitor execution with detailed logging
        for i in range(24):  # Wait up to 2 minutes
            time.sleep(5)
            
            logs_response = requests.get(
                f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs',
                timeout=10
            )
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                steps = logs_data.get('data', {}).get('steps', [])
                
                # Check progress
                completed_steps = [s for s in steps if s.get('status') == 'completed']
                total_steps = len(steps)
                
                print(f"📊 Progress: {len(completed_steps)}/{total_steps} steps completed")
                
                # Check each step in detail
                for step in steps:
                    step_type = step.get('step_type', 'unknown')
                    step_status = step.get('status', 'unknown')
                    
                    if step_status == 'completed':
                        output_data = step.get('output_data', {})
                        
                        if step_type == 'google_sheets':
                            records = output_data.get('records', [])
                            print(f"   📊 Sheets Read: {len(records)} records found")
                            if records:
                                print(f"   📊 First record: {records[0]}")
                                
                        elif step_type == 'ai_processing':
                            processed_results = output_data.get('processed_results', [])
                            print(f"   🤖 AI Processing: {len(processed_results)} results")
                            
                            if processed_results:
                                # Check first result in detail
                                first_result = processed_results[0]
                                ai_response = first_result.get('ai_response', {})
                                print(f"   🤖 AI Response keys: {list(ai_response.keys())}")
                                
                                if 'ai_response' in ai_response:
                                    ai_text = ai_response['ai_response']
                                    print(f"   🤖 AI text length: {len(ai_text)} characters")
                                    print(f"   🤖 AI text preview: {ai_text[:150]}...")
                                
                            # Check formatted results for sheets
                            results_for_sheets = output_data.get('results_for_sheets', [])
                            if results_for_sheets:
                                print(f"   📋 Formatted for sheets: {len(results_for_sheets)} rows")
                                if len(results_for_sheets) > 1:
                                    headers = results_for_sheets[0]
                                    first_data_row = results_for_sheets[1]
                                    print(f"   📋 Headers: {headers}")
                                    print(f"   📋 First row length: {len(first_data_row)}")
                                    
                                    # Check Prompt column specifically
                                    if 'Prompt' in headers:
                                        prompt_index = headers.index('Prompt')
                                        if len(first_data_row) > prompt_index:
                                            prompt_content = first_data_row[prompt_index]
                                            print(f"   🎯 Prompt content length: {len(prompt_content)}")
                                            if prompt_content:
                                                print(f"   🎯 Prompt preview: {prompt_content[:100]}...")
                                            else:
                                                print(f"   ❌ PROMPT IS EMPTY!")
                                        
                        elif step_type == 'google_sheets_write':
                            data_written = output_data.get('data_written', {})
                            rows_count = data_written.get('rows_count', 0)
                            print(f"   📝 Sheets Write: {rows_count} rows written")
                
                # Check if workflow completed
                if len(completed_steps) == total_steps and total_steps > 0:
                    print("🎉 Workflow completed! Checking final results...")
                    
                    # Look for the AI processing step specifically
                    ai_step = None
                    for step in steps:
                        if step.get('step_type') == 'ai_processing':
                            ai_step = step
                            break
                    
                    if ai_step and ai_step.get('status') == 'completed':
                        output_data = ai_step.get('output_data', {})
                        processed_results = output_data.get('processed_results', [])
                        
                        if processed_results:
                            print(f"\n🔍 DETAILED AI ANALYSIS:")
                            for idx, result in enumerate(processed_results):
                                print(f"\n   Result {idx + 1}:")
                                input_data = result.get('input_data', {})
                                ai_response = result.get('ai_response', {})
                                
                                print(f"     Input: {input_data.get('Description', 'N/A')}")
                                print(f"     AI Response Type: {type(ai_response)}")
                                
                                if isinstance(ai_response, dict):
                                    print(f"     AI Response Keys: {list(ai_response.keys())}")
                                    
                                    # Check for AI response text
                                    if 'ai_response' in ai_response:
                                        ai_text = ai_response['ai_response']
                                        print(f"     AI Text Found: {len(ai_text)} chars")
                                        print(f"     AI Preview: {ai_text[:100]}...")
                                    else:
                                        print(f"     ❌ No 'ai_response' field found")
                                        
                                        # Check for other text fields
                                        for key, value in ai_response.items():
                                            if isinstance(value, str) and len(value) > 50:
                                                print(f"     Alternative text in '{key}': {len(value)} chars")
                                                print(f"     Preview: {value[:100]}...")
                                                break
                        else:
                            print(f"   ❌ No processed results found!")
                    
                    return True
                
                # Check for errors
                error_steps = [s for s in steps if s.get('status') == 'error']
                if error_steps:
                    print(f"❌ Found {len(error_steps)} error steps:")
                    for step in error_steps:
                        print(f"   {step.get('step_type')}: {step.get('error')}")
                    return False
            
            print(f"⏳ Check {i+1}/24...")
        
        print("⏰ Timeout waiting for completion")
        return False
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    result = test_with_correct_range()
    if result:
        print("\n🎉 DEBUG TEST COMPLETED - Check the logs above for AI response details!")
    else:
        print("\n❌ DEBUG TEST FAILED")
