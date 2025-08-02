#!/usr/bin/env python3
"""Simple workflow execution test"""

import requests
import json

def main():
    # Get instances
    r = requests.get('http://localhost:8000/api/v1/workflow/instances')
    response_data = r.json()
    instances = response_data['data']['instances']
    latest = instances[0]  # First one is latest
    print(f'Latest instance: {latest["id"]} - {latest.get("name", "Unknown")}')
    print(f'Status: {latest.get("status")}')
    
    # Execute workflow
    exec_r = requests.post(f'http://localhost:8000/api/v1/workflow/instances/{latest["id"]}/execute')
    print(f'Execution result: {exec_r.status_code}')
    
    if exec_r.status_code == 200:
        print(f'Response: {exec_r.json()}')
    else:
        print(f'Error: {exec_r.text}')

if __name__ == "__main__":
    main()
