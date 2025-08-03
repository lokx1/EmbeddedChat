import requests

response = requests.get('http://localhost:8000/api/v1/workflow/instances')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response keys: {list(data.keys())}")
    if 'data' in data:
        data_obj = data['data']
        if 'instances' in data_obj:
            instances = data_obj['instances']
            print(f"Found {len(instances)} instances")
            for i, instance in enumerate(instances[:2]):
                print(f"Instance {i+1}:")
                print(f"  ID: {instance.get('id', 'N/A')}")
                print(f"  Status: {instance.get('status', 'N/A')}")
                print(f"  Name: {instance.get('name', 'N/A')}")
        else:
            print(f"No instances key found. Keys: {list(data_obj.keys())}")
else:
    print(f"Error: {response.text}")
