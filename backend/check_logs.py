import requests

# Check logs of most recent instance
instance_id = 'e96d0cab-ce98-4312-bbc7-bf89558f49cb'
response = requests.get(f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/logs')

if response.status_code == 200:
    logs = response.json()
    print('=== Workflow Logs ===')
    print(f'Response type: {type(logs)}')
    
    if isinstance(logs, dict):
        print(f'Available keys: {list(logs.keys())}')
        
        if 'logs' in logs:
            log_list = logs['logs']
            print(f'Found {len(log_list)} logs')
            
            for log in log_list[-10:]:  # Last 10 logs
                timestamp = log.get('timestamp', 'N/A')
                message = log.get('message', 'N/A')
                level = log.get('level', 'INFO')
                print(f'[{level}] {timestamp}: {message}')
        elif 'data' in logs:
            print('Logs in data field:', logs['data'])
        else:
            print('Raw response:', str(logs)[:500])
    else:
        print('Raw logs:', str(logs)[:500])
else:
    print(f'Error getting logs: {response.status_code} - {response.text}')
