#!/usr/bin/env python3
"""
Check dataflow from Frontend to Backend - Debug AI response extraction
"""
import requests
import json

def check_frontend_backend_dataflow():
    """Check the complete dataflow from FE to BE"""
    
    print("=== Frontend to Backend Dataflow Analysis ===")
    
    try:
        # 1. Check recent workflow instances
        print("🔍 Step 1: Checking recent workflow instances...")
        instances_response = requests.get('http://localhost:8000/api/v1/workflow/instances', timeout=10)
        
        if instances_response.status_code != 200:
            print(f"❌ Cannot get instances: {instances_response.status_code}")
            return
            
        instances_data = instances_response.json()
        instances = instances_data.get('data', {}).get('instances', []) if isinstance(instances_data, dict) else instances_data
        
        print(f"Found {len(instances)} instances")
        
        if not instances:
            print("❌ No workflow instances found")
            return
            
        # Get the most recent instance
        latest_instance = instances[-1]
        instance_id = latest_instance.get('id')
        instance_name = latest_instance.get('name', 'Unknown')
        
        print(f"✅ Latest instance: {instance_id} ({instance_name})")
        
        # 2. Get detailed logs of the latest instance
        print(f"\n🔍 Step 2: Analyzing detailed logs for {instance_id}...")
        logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs', timeout=10)
        
        if logs_response.status_code != 200:
            print(f"❌ Cannot get logs: {logs_response.status_code}")
            return
            
        logs_data = logs_response.json()
        steps = logs_data.get('data', {}).get('steps', [])
        
        print(f"📋 Found {len(steps)} execution steps")
        
        # 3. Analyze each step in detail
        sheets_read_data = None
        ai_processing_data = None
        sheets_write_data = None
        
        for i, step in enumerate(steps, 1):
            step_type = step.get('step_type', 'unknown')
            step_status = step.get('status', 'unknown')
            step_id = step.get('step_id', 'unknown')
            
            print(f"\n📋 Step {i}: {step_type} ({step_id}) - Status: {step_status}")
            
            output_data = step.get('output_data', {})
            
            if step_type == 'google_sheets':
                sheets_read_data = output_data
                print("   📊 Google Sheets Read Analysis:")
                records = output_data.get('records', [])
                values = output_data.get('values', [])
                print(f"     - Records: {len(records)}")
                print(f"     - Values: {len(values)}")
                
                if records:
                    print(f"     - Sample record: {records[0]}")
                    for idx, record in enumerate(records[:3]):
                        desc = record.get('Description', 'N/A')
                        prompt = record.get('Prompt', 'EMPTY')
                        print(f"     - Record {idx+1}: {desc} | Prompt: {prompt[:50] if prompt else 'EMPTY'}")
                        
            elif step_type == 'ai_processing':
                ai_processing_data = output_data
                print("   🤖 AI Processing Analysis:")
                processed_results = output_data.get('processed_results', [])
                results_for_sheets = output_data.get('results_for_sheets', [])
                
                print(f"     - Processed results: {len(processed_results)}")
                print(f"     - Results for sheets: {len(results_for_sheets)}")
                
                if processed_results:
                    print("     - AI Results Detail:")
                    for idx, result in enumerate(processed_results[:3]):
                        input_data = result.get('input_data', {})
                        ai_response = result.get('ai_response', {})
                        status = result.get('status', 'unknown')
                        
                        desc = input_data.get('Description', 'N/A')
                        print(f"       * Result {idx+1}: {desc} - Status: {status}")
                        
                        if ai_response:
                            ai_keys = list(ai_response.keys())
                            print(f"         AI Response keys: {ai_keys}")
                            
                            # Check for actual AI response text
                            ai_text = ""
                            if 'ai_response' in ai_response:
                                ai_text = ai_response['ai_response']
                            elif 'text' in ai_response:
                                ai_text = ai_response['text']
                            elif 'response' in ai_response:
                                ai_text = ai_response['response']
                            
                            if ai_text:
                                print(f"         AI Text length: {len(ai_text)}")
                                print(f"         AI Text preview: {ai_text[:100]}...")
                            else:
                                print(f"         ❌ No AI text found!")
                
                if results_for_sheets:
                    print("     - Results for Sheets Detail:")
                    if len(results_for_sheets) > 0:
                        headers = results_for_sheets[0]
                        print(f"       Headers: {headers}")
                        
                        if 'Prompt' in headers:
                            prompt_idx = headers.index('Prompt')
                            print(f"       Prompt column index: {prompt_idx}")
                            
                            for idx, row in enumerate(results_for_sheets[1:4]):  # Check first 3 data rows
                                if idx < len(row):
                                    prompt_content = row[prompt_idx] if prompt_idx < len(row) else ""
                                    desc_content = row[1] if len(row) > 1 else ""  # Assuming description is index 1
                                    print(f"       Row {idx+1}: {desc_content[:30]}... | Prompt: {len(prompt_content)} chars")
                                    if prompt_content:
                                        print(f"                Prompt preview: {prompt_content[:150]}...")
                                    else:
                                        print(f"                ❌ Prompt is EMPTY!")
                        else:
                            print(f"       ❌ No Prompt column found in headers!")
                            
            elif step_type == 'google_sheets_write':
                sheets_write_data = output_data
                print("   📝 Google Sheets Write Analysis:")
                operation = output_data.get('operation', 'unknown')
                data_written = output_data.get('data_written', {})
                sheet_info = output_data.get('sheet_info', {})
                
                print(f"     - Operation: {operation}")
                print(f"     - Rows written: {data_written.get('rows_count', 0)}")
                print(f"     - Columns written: {data_written.get('columns_count', 0)}")
                print(f"     - Target sheet: {sheet_info.get('sheet_name', 'unknown')}")
                print(f"     - Range: {sheet_info.get('range', 'unknown')}")
                print(f"     - Mode: {sheet_info.get('mode', 'unknown')}")
                
            # Show step logs
            step_logs = step.get('logs', [])
            if step_logs:
                print(f"   📜 Step logs ({len(step_logs)} entries):")
                for log in step_logs[-3:]:  # Show last 3 logs
                    print(f"     - {log}")
        
        # 4. Summary and Diagnosis
        print(f"\n🎯 DATAFLOW DIAGNOSIS:")
        
        if sheets_read_data:
            records = sheets_read_data.get('records', [])
            print(f"✅ Google Sheets Read: {len(records)} records")
        else:
            print(f"❌ Google Sheets Read: No data")
            
        if ai_processing_data:
            processed_results = ai_processing_data.get('processed_results', [])
            results_for_sheets = ai_processing_data.get('results_for_sheets', [])
            print(f"✅ AI Processing: {len(processed_results)} results, {len(results_for_sheets)} rows for sheets")
            
            # Check if AI responses contain actual text
            has_ai_text = False
            if processed_results:
                for result in processed_results:
                    ai_response = result.get('ai_response', {})
                    if ai_response and 'ai_response' in ai_response:
                        ai_text = ai_response['ai_response']
                        if ai_text and len(ai_text) > 50:
                            has_ai_text = True
                            break
            
            if has_ai_text:
                print(f"✅ AI Responses: Contain actual text")
            else:
                print(f"❌ AI Responses: No meaningful text found")
                
        else:
            print(f"❌ AI Processing: No data")
            
        if sheets_write_data:
            rows_written = sheets_write_data.get('data_written', {}).get('rows_count', 0)
            print(f"✅ Google Sheets Write: {rows_written} rows written")
        else:
            print(f"❌ Google Sheets Write: No data")
            
        print(f"\n💡 CONCLUSION:")
        if sheets_read_data and ai_processing_data and sheets_write_data:
            print(f"✅ All steps executed successfully")
            
            # Check if the issue is in the data format
            if ai_processing_data:
                results_for_sheets = ai_processing_data.get('results_for_sheets', [])
                if results_for_sheets and len(results_for_sheets) > 1:
                    headers = results_for_sheets[0]
                    if 'Prompt' in headers:
                        prompt_idx = headers.index('Prompt')
                        first_row = results_for_sheets[1]
                        prompt_content = first_row[prompt_idx] if prompt_idx < len(first_row) else ""
                        
                        if prompt_content and len(prompt_content) > 0:
                            print(f"✅ Prompt column has content - check if it's being written to the correct sheet/range")
                            print(f"💡 The issue might be with sheet range or overwrite mode")
                        else:
                            print(f"❌ Prompt column is empty in results_for_sheets - AI extraction failed")
                    else:
                        print(f"❌ No Prompt column in results_for_sheets")
        else:
            print(f"❌ Some steps failed - check individual step logs above")
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    check_frontend_backend_dataflow()
