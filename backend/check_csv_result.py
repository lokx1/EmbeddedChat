import requests
import json

instance_id = 'cdf61a9f-065b-4e69-a780-10f9df5e6215'  # CSV test instance
response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}')

if response.status_code == 200:
    data = response.json()
    print('Instance status:', data.get('status'))
    
    if 'output_data' in data and data['output_data']:
        output_data = data['output_data']
        
        if 'node_outputs' in output_data:
            node_outputs = output_data['node_outputs']
            print('Available nodes:', list(node_outputs.keys()))
            
            if 'drive-write-1' in node_outputs:
                drive_output = node_outputs['drive-write-1']
                print('\n🎉 Google Drive CSV Output:')
                print(f'  📄 File: {drive_output.get("name", "N/A")}')
                print(f'  📊 Type: {drive_output.get("mime_type", "N/A")}')
                print(f'  📏 Size: {drive_output.get("size", "N/A")} bytes')
                print(f'  🔗 Link: {drive_output.get("web_view_link", "N/A")}')
                print(f'  ⚡ Method: {drive_output.get("upload_method", "N/A")}')
                
                if drive_output.get("mime_type") == "text/csv":
                    print('\n✅ SUCCESS: CSV file created and uploaded!')
                else:
                    print(f'\n⚠️ Unexpected MIME type: {drive_output.get("mime_type")}')
            else:
                print('❌ No Google Drive output found')
                print('Available outputs:', list(node_outputs.keys()))
        else:
            print('❌ No node_outputs in data')
    else:
        print('❌ No output_data in response')
else:
    print(f'❌ Error: {response.status_code} - {response.text}')
