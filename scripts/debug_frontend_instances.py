import requests
import json

# Check recent instances from frontend
response = requests.get('http://localhost:8000/api/v1/workflow/instances')

if response.status_code == 200:
    data = response.json()
    instances = data['data']['instances']
    
    print("=== Recent Workflow Instances ===")
    for i, instance in enumerate(instances[:5]):
        instance_id = instance.get('id', 'N/A')
        name = instance.get('name', 'N/A')
        status = instance.get('status', 'N/A')
        
        print(f"{i+1}. {name[:50]}...")
        print(f"   ID: {instance_id}")
        print(f"   Status: {status}")
        
        # Get details for completed instances
        if status == 'completed':
            detail_response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}')
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                
                if 'output_data' in detail_data and detail_data['output_data']:
                    output_data = detail_data['output_data']
                    if 'node_outputs' in output_data and 'drive-write-1' in output_data['node_outputs']:
                        drive_output = output_data['node_outputs']['drive-write-1']
                        file_name = drive_output.get('name', 'N/A')
                        mime_type = drive_output.get('mime_type', 'N/A')
                        print(f"   📄 File: {file_name}")
                        print(f"   📊 MIME: {mime_type}")
                        
                        if 'json' in mime_type.lower():
                            print("   ⚠️  JSON file detected - CSV conversion may not be working")
                        elif 'csv' in mime_type.lower():
                            print("   ✅ CSV file detected - conversion working")
                    else:
                        print("   ❌ No drive output found")
                else:
                    print("   ❌ No output data")
        print()
else:
    print(f"Error: {response.status_code} - {response.text}")
