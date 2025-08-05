#!/usr/bin/env python3
"""
Test Google Sheets reading directly to diagnose the issue
"""
import requests
import json

def test_sheets_read():
    """Test reading from Google Sheets directly"""
    
    print("=== Testing Google Sheets Read ===")
    
    # Test with different sheet names to see which one works
    sheet_names_to_test = [
        "Trang tính1",  # Original Vietnamese name
        "Sheet1",       # Default name
        "Automation Task",  # From the screenshot
        "Trang tinh1",  # Without accent
        "Sheet2"        # Alternative
    ]
    
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    for sheet_name in sheet_names_to_test:
        print(f"\n🔍 Testing sheet name: '{sheet_name}'")
        
        # Create a simple workflow that just reads sheets
        template_data = {
            'name': f'Test Sheets Read - {sheet_name}',
            'description': f'Test reading from {sheet_name}',
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
                            'label': 'Read Sheets',
                            'config': {
                                'sheet_id': sheet_id,
                                'sheet_name': sheet_name,
                                'range': 'A1:E10'
                            }
                        }
                    }
                ],
                'edges': [
                    {'id': 'edge-1', 'source': 'trigger-1', 'target': 'sheets-read-1'}
                ]
            }
        }
        
        try:
            # Create template
            template_response = requests.post(
                'http://localhost:8000/api/v1/workflow/templates',
                json=template_data,
                timeout=15
            )
            
            if template_response.status_code != 200:
                print(f"   ❌ Template creation failed: {template_response.text}")
                continue
                
            template_id = template_response.json()['template_id']
            
            # Create instance
            instance_data = {
                'name': f'Sheets Test - {sheet_name}',
                'template_id': template_id,
                'workflow_data': template_data['workflow_data'],
                'input_data': {}
            }
            
            instance_response = requests.post(
                'http://localhost:8000/api/v1/workflow/instances',
                json=instance_data,
                timeout=15
            )
            
            if instance_response.status_code != 200:
                print(f"   ❌ Instance creation failed: {instance_response.text}")
                continue
                
            instance_id = instance_response.json()['instance_id']
            
            # Execute workflow
            exec_response = requests.post(
                f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute',
                json={},
                timeout=15
            )
            
            if exec_response.status_code != 200:
                print(f"   ❌ Execution failed: {exec_response.text}")
                continue
            
            # Wait a moment for execution
            import time
            time.sleep(3)
            
            # Check results
            logs_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs', timeout=10)
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                steps = logs_data.get('data', {}).get('steps', [])
                
                for step in steps:
                    if step.get('step_type') == 'google_sheets':
                        output_data = step.get('output_data', {})
                        records = output_data.get('records', [])
                        values = output_data.get('values', [])
                        
                        print(f"   📊 Records found: {len(records) if isinstance(records, list) else 'Not a list'}")
                        print(f"   📊 Values found: {len(values) if isinstance(values, list) else 'Not a list'}")
                        
                        if records and len(records) > 0:
                            print(f"   ✅ SUCCESS! Found data in '{sheet_name}'")
                            print(f"   📋 First record: {records[0]}")
                            return sheet_name  # Return the working sheet name
                        elif values and len(values) > 0:
                            print(f"   ✅ SUCCESS! Found values in '{sheet_name}'")
                            print(f"   📋 Values: {values[:2]}")  # Show first 2 rows
                            return sheet_name
                        else:
                            print(f"   ⚠️ No data found in '{sheet_name}'")
                        break
            else:
                print(f"   ❌ Could not get logs: {logs_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception testing '{sheet_name}': {e}")
    
    print(f"\n❌ No working sheet name found. Please check:")
    print(f"   1. Sheet ID: {sheet_id}")
    print(f"   2. Sheet contains data in range A1:E10")
    print(f"   3. Google Sheets API access is properly configured")
    
    return None

if __name__ == "__main__":
    working_sheet = test_sheets_read()
    if working_sheet:
        print(f"\n🎉 Found working sheet name: '{working_sheet}'")
        print("You can now use this in your workflows!")
    else:
        print("\n❌ Could not find a working sheet configuration")
