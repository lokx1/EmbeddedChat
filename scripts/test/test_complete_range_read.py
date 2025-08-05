#!/usr/bin/env python3
"""
Test reading the complete range including headers to understand data structure
"""
import requests
import time

def test_read_complete_range():
    """Test reading complete range with headers"""
    
    print("=== Testing Complete Range Read ===")
    
    template_data = {
        'name': 'Complete Range Debug',
        'description': 'Read complete range to debug data structure',
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
                        'label': 'Read Complete Data',
                        'config': {
                            'sheet_id': '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc',
                            'sheet_name': 'Trang tính1',
                            'range': 'A1:E10'  # Read everything including headers
                        }
                    }
                }
            ],
            'edges': []
        }
    }
    
    try:
        # Create and execute
        template_response = requests.post(
            'http://localhost:8000/api/v1/workflow/templates',
            json=template_data,
            timeout=30
        )
        
        template_id = template_response.json()['template_id']
        print(f"✅ Template created: {template_id}")
        
        instance_data = {
            'name': 'Complete Range Test',
            'template_id': template_id,
            'workflow_data': template_data['workflow_data']
        }
        
        instance_response = requests.post(
            'http://localhost:8000/api/v1/workflow/instances',
            json=instance_data,
            timeout=30
        )
        
        instance_id = instance_response.json()['instance_id']
        print(f"✅ Instance created: {instance_id}")
        
        exec_response = requests.post(
            f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute',
            json={},
            timeout=30
        )
        
        print("✅ Execution started, waiting for results...")
        time.sleep(10)  # Wait for completion
        
        # Get logs
        logs_response = requests.get(
            f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs',
            timeout=10
        )
        
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            steps = logs_data.get('data', {}).get('steps', [])
            
            for step in steps:
                if step.get('step_type') == 'google_sheets':
                    output_data = step.get('output_data', {})
                    
                    print(f"\n🔍 DETAILED SHEETS READ ANALYSIS:")
                    print(f"   Raw values count: {len(output_data.get('values', []))}")
                    print(f"   Records count: {len(output_data.get('records', []))}")
                    
                    # Show raw values
                    values = output_data.get('values', [])
                    if values:
                        print(f"\n📊 Raw Values:")
                        for i, row in enumerate(values):
                            print(f"   Row {i+1}: {row}")
                    
                    # Show converted records
                    records = output_data.get('records', [])
                    if records:
                        print(f"\n📋 Converted Records:")
                        for i, record in enumerate(records):
                            print(f"   Record {i+1}: {record}")
                    else:
                        print(f"\n❌ No records found!")
                        
                        # If no records but we have values, show the conversion issue
                        if values:
                            print(f"📝 Conversion Analysis:")
                            print(f"   First row (should be headers): {values[0] if values else 'None'}")
                            print(f"   Remaining rows: {len(values)-1 if len(values) > 1 else 0}")
                            
                            # Manual conversion test
                            if len(values) > 1:
                                headers = values[0]
                                data_rows = values[1:]
                                print(f"   Headers: {headers}")
                                print(f"   Data rows: {len(data_rows)}")
                                
                                # Convert manually
                                manual_records = []
                                for row in data_rows:
                                    if any(cell.strip() for cell in row if cell):  # Check if row has content
                                        record = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                                        manual_records.append(record)
                                
                                print(f"   Manual conversion result: {len(manual_records)} records")
                                if manual_records:
                                    print(f"   First manual record: {manual_records[0]}")
                    
                    # Show other output data
                    print(f"\n📊 Other Output Data:")
                    for key, value in output_data.items():
                        if key not in ['values', 'records']:
                            print(f"   {key}: {value}")
        
        print(f"\n✅ Complete range analysis finished")
        
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_read_complete_range()
